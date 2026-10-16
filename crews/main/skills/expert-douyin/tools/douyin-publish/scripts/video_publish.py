#!/usr/bin/env python3
"""Persistent creator video publication with validated inputs and resumable SMS."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import time
import traceback
import unicodedata
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '_shared'))
from publish_browser import Browser, MANAGE_URL, SESSION, UPLOAD_URL, publish_lock, video_publish_state_path

PERSISTENT_SESSION = SESSION
UPLOAD_TIMEOUT_S = 300
TRANSCODE_MAX_WAIT_S = 600
POST_PUBLISH_MAX_WAIT_S = 60
TITLE_SELECTOR = 'input[placeholder*="填写作品标题"]'
CAPTION_SELECTOR = '[contenteditable="true"][data-slate-editor="true"]'
WORK_LIST_URL = ('https://creator.douyin.com/janus/douyin/creator/pc/work_list'
                 '?status=0&count=20&max_cursor=0&scene=star_atlas&device_platform=android&aid=1128')
PENDING_STATES = {'submitted', 'awaiting_verification', 'unconfirmed'}
DRAFT_HINT = '保留当前页面；用 edit-draft 继续编辑并检查视频、标题与双封面；视频缺失时 upload --resume-draft --video 原成片路径'
RESULT_HINT = '用 resume/get-link 核查本次作品，勿重跑 run 或重复点发布；未确认成功时可检查原草稿'
MODAL_DOM = r'''
  const modalVisible=e=>!!(e.getClientRects().length && getComputedStyle(e).visibility!=='hidden');
  const matchingModals=kind=>{
    const pattern=kind==='declaration' ? /对作品内容添加声明|内容由AI生成/ : /封面/;
    const roots=Array.from(document.querySelectorAll('[role="dialog"],[role="modal"],.semi-modal,.semi-modal-content'))
      .filter(e=>modalVisible(e) && pattern.test(e.innerText||''));
    // Semi wraps one modal in several matching nodes. Count the innermost
    // content roots, rather than treating its mask/header/footer as dialogs.
    return roots.filter(e=>!roots.some(child=>child!==e && e.contains(child)));
  };
  const coverQualityReason=text=>/封面边框面积过大|边框面积过大/.test(text) ? 'COVER_BORDER_TOO_LARGE' :
    /封面存在文字展示不全/.test(text) ? 'COVER_TEXT_UNSAFE' : /封面不佳/.test(text) ? 'COVER_QUALITY_REJECTED' : '';
  const coverTabActive=e=>e.getAttribute('aria-selected')==='true' || Array.from(e.classList).some(c=>/^(?:tab-item-active|tab-item-activ|active)(?:[-_]|$)/.test(c));
  const coverEditorKind=dialog=>{
    const heading=(dialog.innerText||'').trim().split('\n')[0].trim();
    const title=heading.match(/^设置(横|竖)封面$/);
    if(title)return title[1]==='横' ? 'horizontal' : 'vertical';
    const active=Array.from(dialog.querySelectorAll('[role="tab"],[class*="tab-item"]')).filter(e=>
      modalVisible(e) && /^(横|竖)封面$/.test((e.innerText||'').trim()) &&
      coverTabActive(e));
    return active.length===1 ? ((active[0].innerText||'').trim()==='横封面' ? 'horizontal' : 'vertical') : '';
  };
'''
QUALITY_HINTS = {
    'COVER_BORDER_TOO_LARGE': '平台拒绝封面宽边框；改用按目标比例重新构图的封面，不反复加宽补底，不裁掉文字或跳过检测',
    'COVER_TEXT_UNSAFE': '检查两张封面的文字安全区后重新设置',
    'COVER_QUALITY_REJECTED': '平台判定封面不佳；更换封面并通过质量检测后再继续',
}


class PublishError(RuntimeError):
    def __init__(self, code, hint='', exit_code=1):
        super().__init__(code)
        self.code, self.hint, self.exit_code = code, hint, exit_code


def browser(session):
    if session != SESSION:
        raise PublishError('SESSION_INVALID', '必须使用持久化 session douyin')
    return Browser()


def camoufox_eval(session, js, timeout=30):
    result = browser(session).command('eval', js, timeout=timeout)
    return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)


def evaluate(session, js):
    result = browser(session).eval(js)
    return result


def modal_scope(session, kind, *, required=True):
    """Mark a unique visible modal of the required purpose, never a global button."""
    prefix = {'declaration': 'AIGC', 'cover': 'COVER'}[kind]
    selector = f'[data-xiaobei-modal-target="{kind}"]'
    count = evaluate(session, '(() => {' + MODAL_DOM + f'''
      document.querySelectorAll({json.dumps(selector)}).forEach(e=>e.removeAttribute('data-xiaobei-modal-target'));
      const roots=matchingModals({json.dumps(kind)});
      if(roots.length===1)roots[0].setAttribute('data-xiaobei-modal-target',{json.dumps(kind)});
      return roots.length;
    }})()''')
    if type(count) is not int:
        raise PublishError(f'{prefix}_DIALOG_UNAVAILABLE', DRAFT_HINT)
    if count > 1:
        raise PublishError(f'{prefix}_DIALOG_AMBIGUOUS', '同类弹窗不唯一；保留草稿核查，不猜测按钮或继续发布')
    if count == 0:
        if required:
            raise PublishError(f'{prefix}_DIALOG_MISSING', DRAFT_HINT)
        return None
    return selector


def complete_open_declaration(session):
    # A failed fill can leave the declaration overlay blocking the page inputs.
    if modal_scope(session, 'declaration', required=False) and not _select_ai_declaration(session):
        raise PublishError('AIGC_DECLARATION_MISSING', DRAFT_HINT)


def state_path():
    return video_publish_state_path()


def read_state():
    path = state_path()
    if not path.exists():
        return {}
    try:
        state = json.loads(path.read_text('utf-8'))
        if not isinstance(state, dict) or state.get('session') != SESSION:
            raise ValueError('invalid state')
        return state
    except (OSError, ValueError) as exc:
        raise PublishError('PUBLISH_STATE_INVALID', '保留原状态文件并人工核查本次任务') from exc


def save_state(state):
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    state['session'] = SESSION
    fd, temporary = tempfile.mkstemp(prefix='.douyin-video-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(state, stream, ensure_ascii=False)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check_no_pending():
    if read_state().get('state') in PENDING_STATES:
        raise PublishError('PUBLISH_PENDING', RESULT_HINT, 3)


def _check_logged_in(session):
    url = evaluate(session, 'window.location.href') or ''
    if url.split('?', 1)[0].rstrip('/').endswith(('/login', '/creator-micro/login')):
        raise PublishError('SESSION_EXPIRED', '执行 douyin-publish login；提交过的作品先核实，勿重发', 2)


# Keyboard and pointer operations use fresh, scoped Playwright refs.
def control_ref(session, selector, *, button=False):
    marker = 'data-xiaobei-publish-target'
    setup = evaluate(session, f'''(() => {{
      const visible = e => !!(e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden');
      const nodes = Array.from(document.querySelectorAll({json.dumps(selector)})).filter(visible);
      if (nodes.length !== 1 || nodes[0].disabled || nodes[0].readOnly || nodes[0].getAttribute('aria-disabled') === 'true') return false;
      document.querySelectorAll('[{marker}]').forEach(e => e.removeAttribute('{marker}'));
      const e = nodes[0]; e.setAttribute('{marker}', '1');
      e.setAttribute('data-xiaobei-old-label', e.getAttribute('aria-label') || '');
      e.setAttribute('aria-label', 'xiaobei publication target');
      if ({json.dumps(button)} && !e.matches('button,[role="button"],a,input')) {{
        e.setAttribute('data-xiaobei-old-role', e.getAttribute('role') || ''); e.setAttribute('role', 'button');
      }} else if (!{json.dumps(button)} && e.isContentEditable && e.getAttribute('role')!=='textbox') {{
        e.setAttribute('data-xiaobei-old-role', e.getAttribute('role') || ''); e.setAttribute('role', 'textbox');
      }}
      return true;
    }})()''')
    if setup is not True:
        raise PublishError('CONTROL_NOT_UNIQUE_OR_EDITABLE', selector)
    snapshot = browser(session).command('snapshot', '-s', f'[{marker}]')
    refs = re.findall(r'\[ref=(e\d+)\]', snapshot.get('snapshot', ''))
    if not refs:
        raise PublishError('CONTROL_REF_MISSING', selector)
    return refs[0]


def cleanup_control(session):
    evaluate(session, '''(() => {
      document.querySelectorAll('[data-xiaobei-old-role]').forEach(e => {
        const role=e.getAttribute('data-xiaobei-old-role');
        if (role) e.setAttribute('role',role); else e.removeAttribute('role');
        e.removeAttribute('data-xiaobei-old-role');
      });
      document.querySelectorAll('[data-xiaobei-old-label]').forEach(e => {
        const label=e.getAttribute('data-xiaobei-old-label');
        if (label) e.setAttribute('aria-label',label); else e.removeAttribute('aria-label');
        e.removeAttribute('data-xiaobei-old-label');
      });
      document.querySelectorAll('[data-xiaobei-publish-target]').forEach(e => e.removeAttribute('data-xiaobei-publish-target'));
    })()''')


def click_selector(session, selector):
    try:
        ref = control_ref(session, selector, button=True)
        browser(session).command('click', ref)
    finally:
        cleanup_control(session)


def click_text(session, text, *, scope='body', required=True):
    selected = evaluate(session, f'''(() => {{
      const root=document.querySelector({json.dumps(scope)}); if (!root) return false;
      const visible=e=>!!(e.getClientRects().length && getComputedStyle(e).visibility!=='hidden');
      const nodes=Array.from(root.querySelectorAll('button,[role="button"],div,span,li,option,a,label'))
        .filter(e=>visible(e) && (e.innerText||'').trim()==={json.dumps(text)});
      const buttons=nodes.filter(e=>e.matches('button,[role="button"]'));
      const leaves=nodes.filter(e=>!nodes.some(child=>child!==e && e.contains(child)));
      const targets=buttons.length ? buttons : leaves;
      if (targets.length!==1) return false;
      targets[0].setAttribute('data-xiaobei-text-target','1'); return true;
    }})()''')
    if not selected:
        if required:
            raise PublishError('CONTROL_NOT_FOUND', text)
        return False
    try:
        click_selector(session, '[data-xiaobei-text-target]')
    finally:
        evaluate(session, "document.querySelectorAll('[data-xiaobei-text-target]').forEach(e=>e.removeAttribute('data-xiaobei-text-target'))")
    return True


def editor_text_matches(actual, expected):
    # Slate topic nodes may add Unicode spaces/format characters. Compare the
    # whole logical text: a matching prefix cannot prove the rest was written.
    def normalized(text):
        return ''.join(c for c in unicodedata.normalize('NFKC', text)
                       if not c.isspace() and unicodedata.category(c) != 'Cf')
    return normalized(actual) == normalized(expected)


def camoufox_type(session, selector, text):
    try:
        ref = control_ref(session, selector)
        b = browser(session)
        b.command('click', ref)
        b.command('press', 'ControlOrMeta+A')
        b.command('press', 'Backspace')
        if text:
            b.command('type', ref, text)
        b.command('press', 'Tab')
        # Read after React renders, including controlled-value reversion. Inputs
        # (titles and OTPs) must match exactly, including short or empty values.
        result = evaluate(session, f'''(async () => {{
          await new Promise(r=>setTimeout(r,150));
          const e=document.querySelector({json.dumps(selector)});
          if (!e) return null;
          return 'value' in e ? {{value:e.value}} : {{editor:e.innerText||''}};
        }})()''')
        if not isinstance(result, dict):
            return False
        if 'value' in result:
            return result['value'] == text
        return editor_text_matches(result.get('editor', ''), text)
    finally:
        cleanup_control(session)


def page_status(session):
    _check_logged_in(session)
    result = evaluate(session, '(() => {' + MODAL_DOM + r'''
      const visible=e=>!!(e.getClientRects().length && getComputedStyle(e).visibility!=='hidden');
      const text=document.body.innerText||'';
      // The permanent "点击发布后…上传中…请勿关闭页面" footer is advice,
      // not upload progress. It can span lines in the rendered page.
      const busyText=text.replace(/点击发布后[\s\S]*?请勿关闭页面[^\n]*/g, '');
      const busy=/上传中|正在上传|转码中|正在转码|视频处理中/.test(busyText);
      const progress=Array.from(document.querySelectorAll('[role="progressbar"]')).some(e=>
        visible(e) && Number(e.getAttribute('aria-valuenow')) < Number(e.getAttribute('aria-valuemax')||100));
      const videos=Array.from(document.querySelectorAll('video'));
      const video=videos.some(v=>
        (v.currentSrc||v.getAttribute('src')) && v.readyState>=2 && Number.isFinite(v.duration) && v.duration>0);
      const title=document.querySelector('input[placeholder*="填写作品标题"]');
      const caption=document.querySelector('[contenteditable="true"][data-slate-editor="true"]');
      const declarationDialog=matchingModals('declaration').length>0;
      const coverDialog=matchingModals('cover').length>0;
      const coverControls=Array.from(document.querySelectorAll('[class*="coverControl"]')).filter(visible);
      const hasPreview=e=>Array.from(e.querySelectorAll('img')).some(i=>
        i.complete && i.naturalWidth>=120 && i.naturalHeight>=120 && !!i.getAttribute('src')) ||
        [e,...e.querySelectorAll('*')].some(n=>n.clientWidth>=60 && n.clientHeight>=60 && /^url\(/.test(getComputedStyle(n).backgroundImage));
      // Prefer the two observed cover slots; fallback to separately labelled slots.
      const labelledCover=label=>Array.from(document.querySelectorAll('div,section'))
        .some(e=>visible(e) && (e.innerText||'').trim().length<100 &&
          (e.innerText||'').includes(label) && hasPreview(e) &&
          !/选择封面|设置横封面|设置竖封面/.test(e.innerText||''));
      const covers=coverControls.length===2 ? coverControls.every(hasPreview) :
        labelledCover('竖封面') && labelledCover('横封面');
      const missing=/双封面缺失|横封面缺失|竖封面缺失/.test(text);
      const qualityReason=coverQualityReason(text);
      const sms=/接收短信验证码|请输入当前手机号收到的短信验证码/.test(text);
      const rejected=(text.match(/(?:发布失败|上传失败|转码失败|验证码错误|验证码不正确|验证码已过期)[^\n]{0,80}/)||[])[0]||'';
      return {url:location.href,video_ready:video && !busy && !progress,busy:busy||progress,
        video_sources:videos.map(v=>v.currentSrc||v.getAttribute('src')).filter(Boolean),
        video_duration:videos.find(v=>v.readyState>=2 && Number.isFinite(v.duration) && v.duration>0)?.duration||0,
        caption:caption ? caption.innerText||'' : null,
        title:title ? title.value : '',dual_cover_ready:covers && !missing && !coverDialog,cover_missing:missing,
        cover_quality_error:!!qualityReason,cover_quality_reason:qualityReason,sms_required:sms,rejected:rejected,
        aigc:text.includes('内容由AI生成') && !text.includes('请选择自主声明') && !declarationDialog};
    })()''')
    if not isinstance(result, dict):
        raise PublishError('PAGE_STATUS_UNAVAILABLE', DRAFT_HINT)
    return result


def wait_for(session, check, timeout, code, hint=DRAFT_HINT):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status = page_status(session)
        if status['rejected']:
            raise PublishError('PLATFORM_REJECTED', status['rejected'])
        if check(status):
            return status
        time.sleep(2)
    raise PublishError(code, hint)


def validate_media(video):
    path = Path(video).expanduser().resolve()
    if path.suffix.lower() not in {'.mp4', '.mov'} or not path.is_file() or path.stat().st_size == 0:
        raise PublishError('VIDEO_INPUT_INVALID', '需要非空 mp4/mov 文件')
    return path


def validate_content(title, caption):
    if not title.strip():
        raise PublishError('TITLE_MISSING')
    if len(title) > 30 or len(caption) > 1000:
        raise PublishError('CONTENT_LENGTH_OUT_OF_RANGE')


def validate_cover(path):
    from PIL import Image
    file = Path(path).expanduser().resolve()
    try:
        with Image.open(file) as im:
            im.verify()
    except (OSError, ValueError) as exc:
        raise PublishError('COVER_INPUT_INVALID', str(file)) from exc
    return file


def prepare_cover(source, output, ratio):
    """Fit the entire image into the required ratio, padding instead of cropping."""
    from PIL import Image, ImageOps
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert('RGB')
        unit = math.ceil(max(image.width / ratio[0], image.height / ratio[1]))
        size = (ratio[0] * unit, ratio[1] * unit)
        # Cap large uploads without changing the ratio or cutting text.
        if max(size) > 2048:
            unit = 2048 // max(ratio)
            size = (ratio[0] * unit, ratio[1] * unit)
        fitted = ImageOps.contain(image, size, Image.Resampling.LANCZOS)
        canvas = Image.new('RGB', size, (234, 234, 234))
        canvas.paste(fitted, ((size[0]-fitted.width)//2, (size[1]-fitted.height)//2))
        canvas.save(output, quality=95)
        return size


def cmd_open_page(*, session=SESSION):
    check_no_pending()
    browser(session).command('open', UPLOAD_URL)
    _check_logged_in(session)
    return {'ok': True, 'session': session, 'url': evaluate(session, 'window.location.href')}


def cmd_upload(*, video, session=SESSION, resume_draft=False):
    path = validate_media(video)
    check_no_pending()
    save_state({'state': 'draft', 'video': str(path)})
    if not resume_draft:
        cmd_open_page(session=session)
    else:
        _check_logged_in(session)
        if not is_draft_url(evaluate(session, 'window.location.href') or ''):
            raise PublishError('DRAFT_PAGE_REQUIRED', '先打开上传页并续编目标草稿')
    if evaluate(session, "document.body.innerText.includes('你还有上次未发布的视频')"):
        if resume_draft:
            click_text(session, '继续编辑')
        else:
            raise PublishError('DRAFT_PRESENT', '用 edit-draft 继续编辑已有草稿；核实后再决定是否放弃，不自动清除')
    previous_sources = evaluate(session, "Array.from(document.querySelectorAll('video')).map(v=>v.currentSrc||v.getAttribute('src')).filter(Boolean)") or []
    browser(session).command('upload', 'input[type="file"][accept*="video"]', str(path), timeout=UPLOAD_TIMEOUT_S)
    sys.stderr.write('[douyin-publish video] 等待视频可播放且上传/转码结束…\n')
    # Require stable readiness; the title form can exist before any media is uploaded.
    ready = 0
    def stable(status):
        nonlocal ready
        changed = any(source not in previous_sources for source in status.get('video_sources', []))
        ready = ready + 1 if status['video_ready'] and changed else 0
        return ready >= 2
    wait_for(session, stable, TRANSCODE_MAX_WAIT_S, 'VIDEO_NOT_UPLOADED')
    return {'ok': True, 'state': 'video_ready', 'session': session, 'video': str(path)}


def cmd_edit_draft(*, session=SESSION, confirm_unpublished=False):
    state = read_state()
    if state.get('state') in PENDING_STATES:
        if not confirm_unpublished:
            raise PublishError('PUBLISH_PENDING', '先 resume 核查；仅人工确认未发布后用 edit-draft --confirm-unpublished 续编', 3)
        status = page_status(session)
        if status['sms_required']:
            raise PublishError('SMS_VERIFICATION_REQUIRED', '先完成当前短信验证，不清除验证任务', 4)
        item = matching_work(state, work_items(session))
        if item:
            state.update(state='published', aweme_id=item['id'])
            save_state(state)
            return published_result(state)
        state['state'] = 'draft'
        for field in ('submitted_at', 'baseline_ids', 'sms_requested', 'aweme_id'):
            state.pop(field, None)
        save_state(state)
        if '/content/manage' in status['url']:
            cmd_open_page(session=session)
    if evaluate(session, "document.body.innerText.includes('你还有上次未发布的视频')"):
        click_text(session, '继续编辑')
    status = page_status(session)
    if '/content/manage' in status['url']:
        raise PublishError('DRAFT_PAGE_REQUIRED', '先用 open-page 打开上传页')
    state['state'] = 'draft'
    save_state(state)
    return {'ok': True, 'state': 'draft', 'page': status, 'hint': DRAFT_HINT}


def _select_ai_declaration(session):
    if page_status(session)['aigc']:
        return True
    scope = modal_scope(session, 'declaration', required=False)
    if not scope and not click_text(session, '请选择自主声明', required=False):
        return False
    scope = modal_scope(session, 'declaration')
    # Semi's parent label intercepts pointer clicks on its nested span. Click
    # the unique label, then confirm its radio state before saving the dialog.
    selected = evaluate(session, '(async () => {' + f'const dialog=document.querySelector({json.dumps(scope)});' + r'''
      if(!dialog)return false;
      const visible=e=>!!(e.getClientRects().length && getComputedStyle(e).visibility!=='hidden');
      const labels=Array.from(dialog.querySelectorAll('label.semi-radio'))
        .filter(e=>visible(e) && (e.innerText||'').trim()==='内容由AI生成');
      if (labels.length!==1) return false;
      labels[0].click();
      await new Promise(r=>setTimeout(r,150));
      const radio=labels[0].querySelector('input[type="radio"],[role="radio"]');
      return !!(radio && (radio.checked || radio.getAttribute('aria-checked')==='true')) ||
        labels[0].classList.contains('semi-radio-checked');
    })()''')
    if selected is not True:
        return False
    click_text(session, '确定', scope=modal_scope(session, 'declaration'))
    return wait_for(session, lambda s: s['aigc'], 10, 'AIGC_DECLARATION_MISSING')['aigc']


def cmd_fill(*, session, title='', caption=''):
    validate_content(title, caption)
    check_no_pending()
    _check_logged_in(session)
    complete_open_declaration(session)
    if not camoufox_type(session, TITLE_SELECTOR, title):
        raise PublishError('TITLE_WRITE_FAILED', '真实键盘输入后标题读回不一致；保留草稿检查')
    if not camoufox_type(session, CAPTION_SELECTOR, caption):
        raise PublishError('CAPTION_WRITE_FAILED', DRAFT_HINT)
    if not _select_ai_declaration(session):
        raise PublishError('AIGC_DECLARATION_MISSING')
    if page_status(session)['title'] != title:
        raise PublishError('TITLE_WRITE_FAILED')
    state = read_state()
    state.update(state='draft', title=title, caption=caption)
    save_state(state)
    return {'ok': True, 'state': 'filled', 'title': title, 'caption': caption}


def cover_editor_kind(session):
    scope = modal_scope(session, 'cover')
    return evaluate(session, '(() => {' + MODAL_DOM + f'''
      return coverEditorKind(document.querySelector({json.dumps(scope)}));
    }})()''')


def open_cover_editor(session, horizontal):
    """Enter a named cover slot and prove the editor kind before selecting a file."""
    kind, label = ('horizontal', '横封面') if horizontal else ('vertical', '竖封面')
    scope = modal_scope(session, 'cover', required=False)
    if not scope:
        # The editor's side preview follows the PAGE's cover preview tab,
        # independently of the editor heading. Select both before uploading.
        preview = evaluate(session, '''(() => {
          const visible=e=>!!(e.getClientRects().length && getComputedStyle(e).visibility!=='hidden');
          const tabs=Array.from(document.querySelectorAll('[class*="tabItem"]'))
            .filter(e=>visible(e) && (e.innerText||'').trim()==='预览封面/标题');
          return tabs.length===1;
        })()''')
        if preview:
            click_text(session, '预览封面/标题')
    preview_tabs = '(() => {' + MODAL_DOM + f'''
      const editors=matchingModals('cover');
      const tabs=Array.from(document.querySelectorAll('[class*="tab-item"],[role="tab"]'))
        .filter(e=>modalVisible(e) && (e.innerText||'').trim()==={json.dumps(label)} && !editors.some(d=>d.contains(e)));
    '''
    count = evaluate(session, preview_tabs + '''
      document.querySelectorAll('[data-xiaobei-cover-preview-tab]').forEach(e=>e.removeAttribute('data-xiaobei-cover-preview-tab'));
      if(tabs.length===1)tabs[0].setAttribute('data-xiaobei-cover-preview-tab','1');
      return tabs.length;
    })()''')
    if type(count) is not int or count > 1:
        raise PublishError('COVER_PREVIEW_TAB_AMBIGUOUS', '封面预览选项卡不唯一；保留草稿，不猜测目标')
    if count == 1:
        active = evaluate(session, preview_tabs + "return tabs.length===1 && coverTabActive(tabs[0]);})()") is True
        if not active and scope:
            evaluate(session, "document.querySelectorAll('[data-xiaobei-cover-preview-tab]').forEach(e=>e.removeAttribute('data-xiaobei-cover-preview-tab'))")
            raise PublishError('COVER_PREVIEW_TAB_NOT_SELECTED', f'已有编辑器遮挡{label}页面预览选项卡；保留草稿，先处理当前未保存弹窗再续编')
        try:
            if not active:
                click_selector(session, '[data-xiaobei-cover-preview-tab]')
        finally:
            evaluate(session, "document.querySelectorAll('[data-xiaobei-cover-preview-tab]').forEach(e=>e.removeAttribute('data-xiaobei-cover-preview-tab'))")
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if evaluate(session, preview_tabs + "return tabs.length===1 && coverTabActive(tabs[0]);})()") is True:
                break
            time.sleep(0.2)
        else:
            raise PublishError('COVER_PREVIEW_TAB_NOT_SELECTED', f'{label}预览未激活；保留草稿，不上传或发布')
    if not scope:
        count = evaluate(session, '(() => {' + MODAL_DOM + f'''
          document.querySelectorAll('[data-xiaobei-cover-entry]').forEach(e=>e.removeAttribute('data-xiaobei-cover-entry'));
          const controls=Array.from(document.querySelectorAll('[class*="coverControl"]'))
            .filter(e=>modalVisible(e) && (e.innerText||'').includes({json.dumps(label)}));
          if(controls.length===1){{
            const surfaces=Array.from(controls[0].children).filter(e=>modalVisible(e) && Array.from(e.classList).some(c=>c.startsWith('cover-')));
            if(surfaces.length>1)return 0;
            (surfaces[0]||controls[0]).setAttribute('data-xiaobei-cover-entry','1');
          }}
          return controls.length;
        }})()''')
        if type(count) is not int or count != 1:
            raise PublishError('COVER_ENTRY_NOT_UNIQUE', f'{label}入口不唯一；保留草稿，不按 DOM 下标猜测')
        try:
            try:
                ref = control_ref(session, '[data-xiaobei-cover-entry]', button=True)
                browser(session).command('hover', ref)
            finally:
                cleanup_control(session)
            if not click_text(session, '编辑封面', scope='[data-xiaobei-cover-entry]', required=False):
                click_selector(session, '[data-xiaobei-cover-entry]')
        finally:
            evaluate(session, "document.querySelectorAll('[data-xiaobei-cover-entry]').forEach(e=>e.removeAttribute('data-xiaobei-cover-entry'))")
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            scope = modal_scope(session, 'cover', required=False)
            if scope:
                break
            time.sleep(0.2)
        if not scope:
            raise PublishError('COVER_DIALOG_MISSING', DRAFT_HINT)
    if cover_editor_kind(session) != kind:
        # Some versions share one modal and expose the two cover types as tabs.
        # Only a tab IN this editor can switch it; page preview tabs are unrelated.
        count = evaluate(session, '(() => {' + MODAL_DOM + f'''
          const dialog=document.querySelector({json.dumps(scope)});
          const tabs=Array.from(dialog.querySelectorAll('[role="tab"],[class*="tab-item"]'))
            .filter(e=>modalVisible(e) && (e.innerText||'').trim()==={json.dumps(label)});
          if(tabs.length===1)tabs[0].setAttribute('data-xiaobei-cover-tab','1');
          return tabs.length;
        }})()''')
        if count == 1:
            try:
                click_selector(session, '[data-xiaobei-cover-tab]')
            finally:
                evaluate(session, "document.querySelectorAll('[data-xiaobei-cover-tab]').forEach(e=>e.removeAttribute('data-xiaobei-cover-tab'))")
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if cover_editor_kind(session) == kind:
                    return
                time.sleep(0.2)
        if cover_editor_kind(session) != kind:
            raise PublishError('COVER_EDITOR_MISMATCH', f'当前编辑器不是{label}；保留草稿，核查封面入口/选项卡，不上传或发布')


def cover_input(session, horizontal=None):
    scope = modal_scope(session, 'cover')
    if horizontal is not None and cover_editor_kind(session) != ('horizontal' if horizontal else 'vertical'):
        raise PublishError('COVER_EDITOR_MISMATCH', '封面编辑器类型不符；保留草稿，不上传或发布')
    # Semi's initial input can ignore a second file at maxCount. When the editor
    # already holds an uploaded cover preview, use its replacement input, never
    # global nth. A built-in preview image (e.g. the video frame) must not be
    # mistaken for an existing cover: only an uploaded image matching the target
    # ratio counts as an existing cover, otherwise a fresh slot would wrongly
    # pick the replacement input and the upload never refreshes the preview.
    target_ratio = None if horizontal is None else (4.0 / 3.0 if horizontal else 3.0 / 4.0)
    selected = evaluate(session, '(() => {' + MODAL_DOM + f'''
      document.querySelectorAll('[data-xiaobei-cover-input]').forEach(e=>e.removeAttribute('data-xiaobei-cover-input'));
      const dialog=document.querySelector({json.dumps(scope)});
      const targetRatio={json.dumps(target_ratio)};
      const inputs=Array.from(dialog.querySelectorAll('input[type="file"]'))
        .filter(e=>e.accept.includes('image') && !e.accept.includes('video') && !e.disabled);
      const primary=inputs.filter(e=>e.classList.contains('semi-upload-hidden-input'));
      const replacement=inputs.filter(e=>e.classList.contains('semi-upload-hidden-input-replace'));
      const hasUploadedPreview=Array.from(dialog.querySelectorAll('img')).some(i=>
        modalVisible(i) && i.complete && i.naturalWidth>=120 && i.naturalHeight>=120 &&
        /^(data:image|blob:)/.test(i.currentSrc||i.getAttribute('src')||'') &&
        (targetRatio===null || Math.abs(i.naturalWidth/i.naturalHeight-targetRatio)<=0.05));
      const targets=hasUploadedPreview && replacement.length ? replacement : primary.length ? primary : inputs;
      if(targets.length!==1)return false;
      targets[0].setAttribute('data-xiaobei-cover-input','1');return true;
    }})()''')
    if selected is not True:
        raise PublishError('COVER_INPUT_LAYOUT_CHANGED', '当前封面编辑器没有唯一上传框；不猜测 file input 序号')
    return '[data-xiaobei-cover-input]'


def watch_cover_preview(session, *, input_selector=None, expected_size=None, horizontal=None):
    # Capture the chosen File before React clears input.files. Keep all image
    # bytes inside this page; a cached src need not emit a new img load event.
    input_selector = input_selector or cover_input(session, horizontal)
    scope = modal_scope(session, 'cover')
    started = evaluate(session, '(() => {' + f'''
      const dialog=document.querySelector({json.dumps(scope)});
      const input=document.querySelector({json.dumps(input_selector)});
      const expectedSize={json.dumps(expected_size)};
      const expectedKind={json.dumps(None if horizontal is None else ('horizontal' if horizontal else 'vertical'))};
    ''' + r'''
      if (!dialog) return false;
      if (!input || !input.accept.includes('image')) return false;
      const previous=window.__xiaobeiCoverUpload;
      if(previous?.onChange)document.removeEventListener('change',previous.onChange,true);
      if(previous?.onLoad)previous.dialog.removeEventListener('load',previous.onLoad,true);
      const watch={input,expectedSize,expectedKind,selected:false,fileData:null,
        beforeSources:new Set(Array.from(dialog.querySelectorAll('img')).map(i=>i.currentSrc||i.getAttribute('src')||'')),
        blobData:new Map(),pixelMatches:new Map(),filePixels:null};
      watch.onChange=e=>{
        if(e.target!==input || input.files.length!==1)return;
        const file=input.files[0];
        watch.selected=true;watch.file=file;watch.fileData=null;watch.blobData.clear();watch.pixelMatches.clear();watch.filePixels=null;
        const reader=new FileReader();
        reader.onload=()=>{if(watch.file===file)watch.fileData=String(reader.result)};
        reader.readAsDataURL(file);
      };
      document.addEventListener('change',watch.onChange,true);
      window.__xiaobeiCoverUpload=watch;
      return true;
    })()''')
    if started is not True:
        raise PublishError('COVER_DIALOG_MISSING', DRAFT_HINT)


def cover_preview_ready(session):
    result = evaluate(session, '(async () => {' + MODAL_DOM + r'''
      const watch=window.__xiaobeiCoverUpload;
      if(!watch || !watch.selected || !watch.fileData)return {ready:false};
      const roots=matchingModals('cover');
      if(roots.length>1)return {ready:false,error:'COVER_DIALOG_AMBIGUOUS'};
      if(roots.length!==1)return {ready:false};
      const dialog=roots[0];
      if(watch.expectedKind && coverEditorKind(dialog)!==watch.expectedKind)return {ready:false,error:'COVER_EDITOR_MISMATCH'};
      if(/上传中|正在上传/.test(dialog.innerText||''))return {ready:false};
      // Rejected uploads may leave the previous preview intact. An explicit
      // platform quality error must not be converted to an upload timeout.
      const quality=coverQualityReason(dialog.innerText||'');
      if(quality)return {ready:false,error:quality};
      const payload=data=>data.slice(data.indexOf(',')+1);
      const readBlob=blob=>new Promise((resolve,reject)=>{
        const reader=new FileReader();reader.onload=()=>resolve(String(reader.result));
        reader.onerror=()=>reject(new Error('PREVIEW_READ_FAILED'));reader.readAsDataURL(blob);
      });
      const selectedPixels=async()=>{
        if(!watch.filePixels){
          const selected=document.createElement('img');
          await new Promise((resolve,reject)=>{selected.onload=resolve;selected.onerror=reject;selected.src=watch.fileData});
          const canvas=document.createElement('canvas');canvas.width=selected.naturalWidth;canvas.height=selected.naturalHeight;
          const context=canvas.getContext('2d');context.drawImage(selected,0,0);
          watch.filePixels={image:selected,width:canvas.width,height:canvas.height,data:context.getImageData(0,0,canvas.width,canvas.height).data};
        }
        return watch.filePixels;
      };
      const samePixels=async image=>{
        const src=image.currentSrc||image.getAttribute('src')||'';
        if(watch.pixelMatches.has(src))return watch.pixelMatches.get(src);
        try{
          const file=await selectedPixels();
          if(image.naturalWidth!==file.width || image.naturalHeight!==file.height){watch.pixelMatches.set(src,false);return false}
          const canvas=document.createElement('canvas');canvas.width=file.width;canvas.height=file.height;
          const context=canvas.getContext('2d');context.drawImage(image,0,0);
          const preview=context.getImageData(0,0,canvas.width,canvas.height).data;
          let total=0;
          // Allow only small JPEG encoding noise: a single large pixel change
          // or a changed text patch rejects even if whole-image averages agree.
          for(let y=0;y<file.height;y+=8)for(let x=0;x<file.width;x+=8){
            let tile=0,count=0;
            for(let yy=y;yy<Math.min(y+8,file.height);yy++)for(let xx=x;xx<Math.min(x+8,file.width);xx++){
              const offset=(yy*file.width+xx)*4;
              for(let channel=0;channel<3;channel++){
                const diff=Math.abs(file.data[offset+channel]-preview[offset+channel]);
                if(diff>10){watch.pixelMatches.set(src,false);return false}
                total+=diff;tile+=diff;count++;
              }
            }
            if(tile/count>2){watch.pixelMatches.set(src,false);return false}
          }
          const matches=total/(file.width*file.height*3)<=0.5;
          watch.pixelMatches.set(src,matches);return matches;
        }catch{return false}
      };
      const targetRatio=watch.expectedSize ? watch.expectedSize[0]/watch.expectedSize[1] :
        watch.expectedKind==='horizontal' ? 4/3 : watch.expectedKind==='vertical' ? 3/4 : null;
      const sameCanvas=async canvas=>{
        try{
          const key=canvas.toDataURL('image/png');
          if(watch.pixelMatches.has(key))return watch.pixelMatches.get(key);
          const file=await selectedPixels();
          if(Math.abs(file.width/file.height-targetRatio)>0.02)return false;
          const reference=document.createElement('canvas');reference.width=canvas.width;reference.height=canvas.height;
          const context=reference.getContext('2d');context.drawImage(file.image,0,0,canvas.width,canvas.height);
          const selected=context.getImageData(0,0,canvas.width,canvas.height).data;
          const preview=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
          let total=0;
          // Fabric's small preview raster differs from browser image scaling.
          // Compare 3x3 local RGB means; bound every patch AND the full image.
          for(let y=0;y<canvas.height;y++)for(let x=0;x<canvas.width;x++){
            if(preview[(y*canvas.width+x)*4+3]<250){watch.pixelMatches.set(key,false);return false}
            for(let channel=0;channel<3;channel++){
              let a=0,b=0,count=0;
              for(let yy=Math.max(0,y-1);yy<Math.min(canvas.height,y+2);yy++)for(let xx=Math.max(0,x-1);xx<Math.min(canvas.width,x+2);xx++){
                const offset=(yy*canvas.width+xx)*4+channel;a+=selected[offset];b+=preview[offset];count++;
              }
              const difference=Math.abs(a-b)/count;
              if(difference>35){watch.pixelMatches.set(key,false);return false}
              total+=difference;
            }
          }
          const matches=total/(canvas.width*canvas.height*3)<=3.5;
          watch.pixelMatches.set(key,matches);return matches;
        }catch{return false}
      };
      for(const image of dialog.querySelectorAll('img')){
        const src=image.currentSrc||image.getAttribute('src')||'';
        if(!modalVisible(image)||!image.complete||image.naturalWidth<120||image.naturalHeight<120||! /^(data:image|blob:)/.test(src))continue;
        const ratioMatches=!watch.expectedSize || Math.abs(image.naturalWidth/image.naturalHeight-watch.expectedSize[0]/watch.expectedSize[1])<=0.02;
        let sameFile=false;
        if(/^data:image[^,]*;base64,/i.test(src))sameFile=payload(src)===payload(watch.fileData);
        else if(/^blob:/.test(src)){
          try{
            if(!watch.blobData.has(src))watch.blobData.set(src,await readBlob(await (await fetch(src)).blob()));
            sameFile=payload(watch.blobData.get(src))===payload(watch.fileData);
          }catch{continue;}
        }
        // Cached editor previews may re-encode JPEGs. Exact bytes or a strict
        // pixel match prove the selected content; ratio alone cannot prove it.
        if(!sameFile && watch.beforeSources.has(src))sameFile=await samePixels(image);
        if(!sameFile && (!ratioMatches || watch.beforeSources.has(src)))continue;
        return {ready:true};
      }
      if(targetRatio)for(const canvas of dialog.querySelectorAll('canvas:not(.upper-canvas)')){
        if(!modalVisible(canvas)||canvas.width<60||canvas.height<60||canvas.width>512||canvas.height>512||Math.abs(canvas.width/canvas.height-targetRatio)>0.02)continue;
        if(await sameCanvas(canvas))return {ready:true};
      }
      return {ready:false};
    })()''')
    if isinstance(result, dict) and result.get('error'):
        code = result['error']
        raise PublishError(code, QUALITY_HINTS.get(code, DRAFT_HINT))
    return isinstance(result, dict) and result.get('ready') is True


def clear_cover_watch(session):
    evaluate(session, '''(() => {
      const watch=window.__xiaobeiCoverUpload;
      if(watch?.onChange)document.removeEventListener('change',watch.onChange,true);
      if(watch?.onLoad)watch.dialog.removeEventListener('load',watch.onLoad,true);
      delete window.__xiaobeiCoverUpload;
      document.querySelectorAll('[data-xiaobei-cover-input]').forEach(e=>e.removeAttribute('data-xiaobei-cover-input'));
    })()''')


def cmd_cover(*, session, cover_vertical, cover_horizontal):
    vertical, horizontal = validate_cover(cover_vertical), validate_cover(cover_horizontal)
    check_no_pending()
    complete_open_declaration(session)
    initial = page_status(session)
    if not initial['video_ready']:
        raise PublishError('VIDEO_NOT_UPLOADED', DRAFT_HINT)
    if not modal_scope(session, 'cover', required=False):
        browser(session).command('press', 'Escape')
    # Slate topic suggestions can remain after Tab and intercept cover clicks.
    evaluate(session, "Array.from(document.querySelectorAll('[class*=\"publish-mention-wrapper\"]')).forEach(w=>{w.style.display='none';w.style.visibility='hidden';})")
    with tempfile.TemporaryDirectory(prefix='douyin-covers-') as temporary:
        for is_horizontal, source, ratio in ((False, vertical, (3, 4)), (True, horizontal, (4, 3))):
            output = Path(temporary) / ('horizontal.jpg' if is_horizontal else 'vertical.jpg')
            size = prepare_cover(source, output, ratio)
            open_cover_editor(session, is_horizontal)
            selector = cover_input(session, is_horizontal)
            watch_cover_preview(session, input_selector=selector, expected_size=size, horizontal=is_horizontal)
            try:
                browser(session).command('upload', selector, str(output), timeout=UPLOAD_TIMEOUT_S)
                deadline = time.monotonic() + 60
                while time.monotonic() < deadline:
                    if cover_preview_ready(session):
                        break
                    time.sleep(2)
                else:
                    raise PublishError('COVER_UPLOAD_TIMEOUT', DRAFT_HINT)
            finally:
                clear_cover_watch(session)
            click_text(session, '完成', scope=modal_scope(session, 'cover'))
            # The editor saves and dismisses asynchronously; it can linger a few
            # seconds. Wait for it to actually close before the next slot, or the
            # still-open editor blocks the next cover preview tab (COVER_PREVIEW_TAB_NOT_SELECTED).
            deadline = time.monotonic() + 15
            while modal_scope(session, 'cover', required=False):
                if time.monotonic() >= deadline:
                    raise PublishError('COVER_EDITOR_NOT_CLOSED', '封面编辑器保存后未关闭；保留草稿，先处理当前弹窗再续编')
                time.sleep(0.3)
    def covers_ready(status):
        if status['cover_quality_error']:
            code = status.get('cover_quality_reason') or 'COVER_TEXT_UNSAFE'
            raise PublishError(code, QUALITY_HINTS.get(code, DRAFT_HINT))
        return status['dual_cover_ready']
    status = wait_for(session, covers_ready,
                      60, 'DUAL_COVER_MISSING', '核查两张封面保存结果及平台文字安全区检测；不要点发布')
    state = read_state()
    state.update(cover_vertical=str(vertical), cover_horizontal=str(horizontal))
    state['cover_recovery'] = {'url': status['url'], 'title': initial['title'],
                               'caption': initial.get('caption'),
                               'duration': initial.get('video_duration', 0), 'attempted': False}
    save_state(state)
    status = restore_cover_video(session, status)
    return {'ok': True, 'state': 'covers_ready', 'page': status}


def is_draft_url(url):
    parsed = urlparse(url)
    return (parsed.scheme == 'https' and parsed.netloc == 'creator.douyin.com'
            and parsed.path in {'/creator-micro/content/upload', '/creator-micro/content/post/video'})


def restore_cover_video(session, status):
    state = read_state()
    recovery = state.get('cover_recovery', {})
    # Only the observed cover-induced DOM removal warrants reopening a draft.
    # Never reload an uploading video, an SMS challenge, or a submitted task.
    if (status['video_ready'] or status.get('video_sources') or status['busy']
            or status['sms_required'] or state.get('state') != 'draft' or not recovery
            or recovery.get('attempted') or recovery.get('url') != status['url']
            or not is_draft_url(status['url']) or not status['dual_cover_ready']
            or status['cover_quality_error'] or status['rejected']):
        return status
    def same_form(current):
        return (current['title'] == recovery['title'] and current['dual_cover_ready']
                and current['aigc'] and not current['cover_quality_error']
                and (recovery.get('caption') is None or
                     (current.get('caption') is not None and
                      editor_text_matches(current['caption'], recovery['caption']))))
    if not same_form(status):
        raise PublishError('DRAFT_CHANGED_AFTER_COVER', DRAFT_HINT)
    recovery['attempted'] = True
    save_state(state)
    browser(session).command('open', status['url'])
    if evaluate(session, "document.body.innerText.includes('你还有上次未发布的视频')"):
        click_text(session, '继续编辑')
    ready = 0
    def restored(current):
        nonlocal ready
        ready = ready + 1 if current['video_ready'] else 0
        return ready >= 2
    current = wait_for(session, restored, 60, 'VIDEO_NOT_UPLOADED')
    if (not same_form(current) or
            (recovery.get('duration', 0) and
             abs(current.get('video_duration', 0)-recovery['duration']) > 0.5)):
        raise PublishError('DRAFT_CHANGED_AFTER_COVER', DRAFT_HINT)
    return current


def preflight(session):
    status = restore_cover_video(session, page_status(session))
    if not status['title'].strip():
        raise PublishError('TITLE_MISSING', DRAFT_HINT)
    validate_content(status['title'], read_state().get('caption', ''))
    if not status['video_ready']:
        raise PublishError('VIDEO_NOT_UPLOADED', DRAFT_HINT)
    if status['cover_quality_error']:
        code = status.get('cover_quality_reason') or 'COVER_TEXT_UNSAFE'
        raise PublishError(code, QUALITY_HINTS.get(code, DRAFT_HINT))
    if not status['dual_cover_ready']:
        raise PublishError('DUAL_COVER_MISSING', DRAFT_HINT)
    if not status['aigc']:
        raise PublishError('AIGC_DECLARATION_MISSING')
    if status['rejected']:
        raise PublishError('PLATFORM_REJECTED', status['rejected'])
    expected = read_state().get('title')
    if expected and expected != status['title']:
        raise PublishError('TITLE_MISMATCH', '当前草稿标题与本次填入标题不同')
    expected_caption = read_state().get('caption')
    if (expected_caption is not None and
            (status.get('caption') is None or not editor_text_matches(status['caption'], expected_caption))):
        raise PublishError('CAPTION_WRITE_FAILED', '当前草稿简介与本次填入内容不一致；'+DRAFT_HINT)
    return status


def work_items(session):
    # Quote integer IDs before parsing in JS, preserving all 19 digits.
    js = f'''(async () => {{
      const response=await fetch({json.dumps(WORK_LIST_URL)},{{credentials:'include'}});
      if (!response.ok) return {{error:'WORK_LIST_HTTP_ERROR'}};
      const raw=await response.text();
      const data=JSON.parse(raw.replace(/("(?:aweme_id|item_id)"\\s*:\\s*)(\\d+)(?=\\s*[,}}])/g,'$1"$2"'));
      if (data.status_code!==0) return {{error:data.status_code===8?'SESSION_EXPIRED':'WORK_LIST_REJECTED'}};
      if (!Array.isArray(data.aweme_list)) return {{error:'WORK_LIST_INVALID'}};
      return {{items:data.aweme_list.map(it=>({{
        id:String(it.aweme_id||it.item_id||''),ct:Number(it.create_time||0),
        title:String(it.title||it.aweme_title||(it.aweme_desc && (it.aweme_desc.title||it.aweme_desc.text))||it.desc||'')
      }})).filter(it=>/^\\d{{15,22}}$/.test(it.id))}};
    }})()'''
    # Retain the bounded same-page retry for intermittent creator authentication responses.
    for attempt in range(3):
        result = evaluate(session, js)
        if isinstance(result, dict) and result.get('error') == 'SESSION_EXPIRED' and attempt < 2:
            time.sleep(2)
            continue
        break
    if not isinstance(result, dict) or 'items' not in result:
        code = result.get('error', 'WORK_LIST_INVALID') if isinstance(result, dict) else 'WORK_LIST_INVALID'
        raise PublishError(code, RESULT_HINT, 2 if code == 'SESSION_EXPIRED' else 3)
    return result['items']


def matching_work(state, items):
    old = set(state['baseline_ids'])
    title = state['title']
    accepted = {title}
    if state.get('caption'):
        accepted.update({title+'\n'+state['caption'], title+' '+state['caption']})
    candidates = [it for it in items if it['id'] not in old and it['ct'] >= state['submitted_at']-5
                  and it['title'] in accepted]
    if len(candidates) > 1:
        raise PublishError('PUBLISH_RESULT_AMBIGUOUS', RESULT_HINT, 3)
    return candidates[0] if candidates else None


def published_result(state):
    return {'ok': True, 'state': 'published', 'session': SESSION, 'aweme_id': state['aweme_id'],
            'url': 'https://www.douyin.com/video/' + state['aweme_id']}


def cmd_resume(*, session=SESSION, timeout=POST_PUBLISH_MAX_WAIT_S):
    state = read_state()
    if state.get('state') == 'published':
        return published_result(state)
    if state.get('state') not in PENDING_STATES:
        raise PublishError('NO_PENDING_PUBLICATION', '尚无本次提交记录；不能用最新旧作品代替', 3)
    started = time.monotonic()
    deadline = started + timeout
    while time.monotonic() < deadline:
        status = page_status(session)
        if status['sms_required']:
            state['state'] = 'awaiting_verification'
            save_state(state)
            raise PublishError('SMS_VERIFICATION_REQUIRED', '页面已保留；verify-send 获取验证码，再用 verify-code --code-file 私有文件续接；也可在窗口完成验证后 resume', 4)
        if status['rejected']:
            state['state'] = 'unconfirmed'
            save_state(state)
            raise PublishError('PLATFORM_REJECTED', status['rejected']+'；'+RESULT_HINT, 3)
        if '/creator-micro/content/manage' in status['url']:
            item = matching_work(state, work_items(session))
            if item:
                state.update(state='published', aweme_id=item['id'])
                save_state(state)
                return published_result(state)
        # Surface validation blockers immediately instead of waiting for an unrelated navigation.
        elif time.monotonic()-started >= 6 and (not status['video_ready'] or not status['title'].strip() or not status['dual_cover_ready'] or status['cover_quality_error']):
            state['state'] = 'unconfirmed'
            save_state(state)
            raise PublishError('PUBLISH_BLOCKED', DRAFT_HINT+'；'+RESULT_HINT, 3)
        time.sleep(2)
    state['state'] = 'unconfirmed'
    save_state(state)
    raise PublishError('PUBLISH_UNCONFIRMED', RESULT_HINT+'；'+DRAFT_HINT, 3)


def cmd_publish(*, session):
    check_no_pending()
    status = preflight(session)
    baseline = work_items(session)
    # Recheck after the read-only request; do not click if the form changed meanwhile.
    current = preflight(session)
    if current['title'] != status['title']:
        raise PublishError('TITLE_MISMATCH')
    state = read_state()
    state.update(state='submitted', title=current['title'], submitted_at=int(time.time()),
                 baseline_ids=[it['id'] for it in baseline])
    state.pop('aweme_id', None)
    state.pop('sms_requested', None)
    save_state(state)  # Persist before clicking: a transport failure must never cause automatic resubmit.
    click_text(session, '发布')
    return cmd_resume(session=session)


def cmd_get_link(*, session):
    return cmd_resume(session=session)


def verification_state(session):
    state = read_state()
    if state.get('state') not in PENDING_STATES or not page_status(session)['sms_required']:
        raise PublishError('SMS_DIALOG_MISSING', '只续接已提交任务的当前短信验证弹窗')
    return state


def cmd_verify_send(*, session):
    state = verification_state(session)
    if state.get('sms_requested'):
        raise PublishError('SMS_ALREADY_REQUESTED', '等待当前验证码；不自动重发')
    state.update(state='awaiting_verification', sms_requested=True)
    save_state(state)
    # Persist the send intent before clicking, including ambiguous transport outcomes.
    click_text(session, '获取验证码')
    deadline = time.monotonic()+10
    while time.monotonic()<deadline:
        if evaluate(session, r"Array.from(document.querySelectorAll('[role=\"dialog\"]')).some(d=>/接收短信验证码|请输入当前手机号收到的短信验证码/.test(d.innerText) && /\d+\s*(?:s|秒)|重新获取/.test(d.innerText))"):
            return {'ok': False, 'state': 'awaiting_verification', 'sms_requested': True, 'session': session}
        time.sleep(1)
    raise PublishError('SMS_SEND_UNCONFIRMED', '点击结果未确认；检查页面倒计时，不自动重复发送', 4)


def read_code_file(file):
    path = Path(file).expanduser()
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'r', encoding='utf-8') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
                raise PublishError('CODE_FILE_UNSAFE', '使用当前用户拥有、权限 0600 的普通文件，不接受软链接')
            code = stream.read(32).strip()
    except OSError as exc:
        raise PublishError('CODE_FILE_UNSAFE', '使用当前用户拥有、权限 0600 的普通文件，不接受软链接') from exc
    if not re.fullmatch(r'[0-9]{4,8}', code):
        raise PublishError('CODE_INVALID', '验证码文件仅含 4–8 位数字')
    return code


def cmd_verify_code(*, session, code_file):
    code = read_code_file(code_file)
    verification_state(session)
    selector = '[role="dialog"] input:not([type="hidden"]):not([type="file"]):not([type="button"]):not([type="submit"]):not([readonly]):not([disabled])'
    if not camoufox_type(session, selector, code):
        raise PublishError('CODE_WRITE_FAILED', '验证码未写入当前弹窗；勿重发作品', 4)
    click_text(session, '验证', scope='[role="dialog"]')
    # Give the validation response a chance to dismiss the SMS dialog.
    deadline = time.monotonic()+15
    while time.monotonic()<deadline:
        status = page_status(session)
        if status['rejected']:
            raise PublishError('SMS_CODE_REJECTED', status['rejected'], 4)
        if not status['sms_required']:
            break
        time.sleep(1)
    return cmd_resume(session=session)


def cmd_status(*, session):
    return {'ok': False, 'state': read_state().get('state', 'idle'), 'session': session,
            'page': page_status(session), 'hint': RESULT_HINT if read_state().get('state') in PENDING_STATES else DRAFT_HINT}


def cmd_run(*, video, title, caption='', cover_vertical, cover_horizontal):
    validate_media(video)
    validate_content(title, caption)
    validate_cover(cover_vertical)
    validate_cover(cover_horizontal)
    check_no_pending()
    try:
        cmd_upload(video=video)
        cmd_fill(session=SESSION, title=title, caption=caption)
        cmd_cover(session=SESSION, cover_vertical=cover_vertical, cover_horizontal=cover_horizontal)
        return cmd_publish(session=SESSION)
    finally:
        # Preserve an unfinished form or challenge for diagnosis and continuation.
        if read_state().get('state') == 'published':
            try:
                Browser().close()
            except Exception:
                pass


def execute(args):
    """Execute a validated command from the unified publication entrypoint."""
    try:
        with publish_lock(allow_pending_video=True):
            result = args.func(args)
            if result.get('state') == 'published' and args.action != 'run':
                try:
                    browser(SESSION).close()
                except Exception:
                    pass
        print(json.dumps(result, ensure_ascii=False))
        return 4 if result.get('state') == 'awaiting_verification' else 0
    except PublishError as exc:
        state = safe_error_state()
        hint = exc.hint
        if exc.code == 'SESSION_EXPIRED' and state.get('state') in PENDING_STATES:
            hint = '本次提交结果未知；验证页面已丢失或登录失效时用 douyin-publish login --resume-video 恢复同一 profile，登录后 resume 核查原作品，勿重发'
        print(json.dumps({'ok': False, 'error': exc.code, 'state': state.get('state', 'idle'),
                          'publish_attempted': state.get('state') in PENDING_STATES | {'published'},
                          'hint': hint, 'session': SESSION}, ensure_ascii=False))
        return exc.exit_code
    except Exception as exc:
        # Browser errors may contain code input or response data. Return only a safe error category.
        state = safe_error_state()
        pending = state.get('state') in PENDING_STATES
        diagnostic = {'exception_type': type(exc).__name__,
                      'frames': [{'file': Path(frame.filename).name, 'line': frame.lineno, 'function': frame.name}
                                 for frame in traceback.extract_tb(exc.__traceback__)]}
        print(json.dumps({'ok': False, 'error': 'BROWSER_OPERATION_FAILED', 'state': state.get('state', 'idle'),
                          'publish_attempted': pending, 'hint': RESULT_HINT if pending else DRAFT_HINT,
                          'diagnostic': diagnostic}, ensure_ascii=False))
        return 3 if pending else 1


def safe_error_state():
    try:
        return read_state()
    except PublishError:
        return {'state': 'unconfirmed'}

#!/usr/bin/env python3
"""Unified persistent creator login, video and image-note publication CLI."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

SCRIPTS = Path(__file__).resolve().parent
TOOLS = SCRIPTS.parents[1]
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TOOLS / '_shared'))
from publish_browser import Browser, MANAGE_URL, SESSION, publish_lock
sys.path.insert(0, str(TOOLS.parent.parent / '_shared'))
from publish_text import PublishTextError, read_publish_text
import video_publish as video
import note_publish as note


def content_options(parser):
    parser.add_argument('--title', required=True)
    parser.add_argument('--caption', default='', help='正文文字或 @UTF-8正文文件路径')


def video_commands(parent):
    commands = parent.add_subparsers(dest='action', required=True)
    for name, function in (
        ('open-page', video.cmd_open_page), ('publish', video.cmd_publish),
        ('get-link', video.cmd_get_link), ('resume', video.cmd_resume),
        ('status', video.cmd_status), ('verify-send', video.cmd_verify_send),
    ):
        command = commands.add_parser(name)
        command.add_argument('--session', default=SESSION, choices=[SESSION])
        command.set_defaults(func=lambda a, f=function: f(session=a.session))
        if name == 'publish':
            command.add_argument('--confirm', action='store_true')
    draft = commands.add_parser('edit-draft')
    draft.add_argument('--session', default=SESSION, choices=[SESSION])
    draft.add_argument('--confirm-unpublished', action='store_true',
                       help='仅人工确认原提交未发布后结案并续编草稿')
    draft.set_defaults(func=lambda a: video.cmd_edit_draft(
        session=a.session, confirm_unpublished=a.confirm_unpublished))
    upload = commands.add_parser('upload')
    upload.add_argument('--video', required=True)
    upload.add_argument('--session', default=SESSION, choices=[SESSION])
    upload.add_argument('--resume-draft', action='store_true', help='保留当前草稿并补传视频')
    upload.set_defaults(func=lambda a: video.cmd_upload(
        video=a.video, session=a.session, resume_draft=a.resume_draft))
    fill = commands.add_parser('fill')
    content_options(fill)
    fill.add_argument('--session', default=SESSION, choices=[SESSION])
    fill.set_defaults(func=lambda a: video.cmd_fill(
        session=a.session, title=a.title, caption=a.caption))
    cover = commands.add_parser('cover')
    cover.add_argument('--session', default=SESSION, choices=[SESSION])
    cover.add_argument('--cover-vertical', required=True)
    cover.add_argument('--cover-horizontal', required=True)
    cover.set_defaults(func=lambda a: video.cmd_cover(
        session=a.session, cover_vertical=a.cover_vertical, cover_horizontal=a.cover_horizontal))
    run = commands.add_parser('run', help='完整视频流程；默认预览，--confirm 后提交')
    content_options(run)
    run.add_argument('--video', required=True)
    run.add_argument('--cover-vertical', help='竖封面；等比补底到 3:4')
    run.add_argument('--cover-horizontal', help='横封面；等比补底到 4:3')
    run.add_argument('--declaration', choices=('aigc', 'ai', 'none'), default='aigc')
    run.add_argument('--confirm', action='store_true')
    run.set_defaults(func=lambda a: video.cmd_run(
        video=a.video, title=a.title, caption=a.caption,
        cover_vertical=a.cover_vertical, cover_horizontal=a.cover_horizontal))
    verify = commands.add_parser('verify-code')
    verify.add_argument('--session', default=SESSION, choices=[SESSION])
    verify.add_argument('--code-file', required=True)
    verify.set_defaults(func=lambda a: video.cmd_verify_code(
        session=a.session, code_file=a.code_file))


def note_commands(parent):
    commands = parent.add_subparsers(dest='action', required=True)
    for name in ('open-page', 'upload', 'music-list', 'music-select',
                 'fill', 'publish', 'get-link', 'run'):
        command = commands.add_parser(name)
        command.add_argument('--headed', action='store_true')
        if name in ('run', 'upload'):
            command.add_argument('--images', nargs='+', required=True)
        if name in ('run', 'fill'):
            content_options(command)
            command.add_argument('--declaration', choices=('aigc', 'ai', 'none'), default='ai')
        if name == 'get-link':
            command.add_argument('--title', required=True)
        if name == 'music-select':
            command.add_argument('--choice', required=True)
        if name in ('publish', 'run'):
            command.add_argument('--original-sound', action='store_true',
                                 help='明确使用原声；配乐使用 music-list/music-select')
            command.add_argument('--confirm', action='store_true')


def build_parser():
    parser = argparse.ArgumentParser(prog='douyin-publish', description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    login = commands.add_parser('login', help='打开持久化有头创作者页面，由用户完成登录')
    login.add_argument('--resume-video', action='store_true',
                       help='验证页面已丢失或登录失效时恢复登录，保留原视频提交记录')
    check = commands.add_parser('check', help='复用持久 profile，通过 HTTP 验证创作者接口')
    check.add_argument('--kind', choices=('video', 'note'), default='video')
    video_commands(commands.add_parser('video', help='视频一键流程、草稿操作、验证续接与取链'))
    note_commands(commands.add_parser('note', help='图文一键流程、配乐与取链'))
    return parser


def normalize_argv(argv):
    args = list(sys.argv[1:] if argv is None else argv)
    # Preserve the existing "video/note --media ..." one-step form.
    if len(args) > 1 and args[0] in ('video', 'note') and args[1].startswith('--') and args[1] != '--help':
        args.insert(1, 'run')
    return args


def preview_run(args):
    if args.command == 'video':
        media = [str(video.validate_media(args.video))]
        video.validate_content(args.title, args.caption)
    else:
        media = [str(Path(path).expanduser().resolve()) for path in args.images]
        note.validate(media, args.title, args.caption)
    result = {'ok': True, 'preview': True, 'kind': args.command, 'action': 'run',
              'title': args.title, 'caption': args.caption, 'files': media,
              'declaration': args.declaration}
    if args.command == 'video':
        result.update(cover_vertical=args.cover_vertical, cover_horizontal=args.cover_horizontal,
                      ready=bool(args.cover_vertical and args.cover_horizontal))
    print(json.dumps(result, ensure_ascii=False))
    return 0


def main(argv=None):
    args = build_parser().parse_args(normalize_argv(argv))
    if args.command == 'check':
        return subprocess.call([sys.executable, str(TOOLS / 'douyin-engagement/scripts/douyin_engagement.py'), 'check'])
    if args.command == 'login':
        lock = publish_lock(allow_pending_video=True) if args.resume_video else publish_lock()
        with lock:
            current = Browser()
            state = current.command('info')
            if isinstance(state, dict) and state.get('running'):
                if args.resume_video and current.eval("/接收短信验证码|请输入当前手机号收到的短信验证码/.test(document.body.innerText)"):
                    raise ValueError('SMS_VERIFICATION_PENDING_USE_VIDEO_RESUME')
                current.headed = bool(state.get('headed'))
                current.close()
            Browser(headed=True).command('open', MANAGE_URL)
            print(json.dumps({'ok': True, 'state': 'awaiting_user_login', 'session': SESSION,
                              'hint': '在有头窗口完成登录后执行 douyin-publish check；登录态保存在持久化 profile'}, ensure_ascii=False))
        return 0
    if hasattr(args, 'caption'):
        args.caption = read_publish_text(args.caption)
        if args.command == 'video':
            video.validate_content(args.title, args.caption)
        else:
            note.validate(title=args.title, caption=args.caption)
    if hasattr(args, 'images'):
        args.images = [str(Path(path).expanduser().resolve()) for path in args.images]
        note.validate(images=args.images, title=getattr(args, 'title', '上传'))
    if args.command == 'video' and args.action == 'run':
        args.video = str(video.validate_media(args.video))
    if args.command == 'note' and hasattr(args, 'declaration'):
        args.declaration = 'none' if args.declaration == 'none' else 'ai'
    if args.action in ('run', 'publish') and not args.confirm:
        if args.action == 'run':
            return preview_run(args)
        print(json.dumps({'ok': True, 'preview': True, 'kind': args.command, 'action': 'publish',
                          'message': '先核对当前草稿、账号、文案、媒体与声明；已有发布授权时加 --confirm'}, ensure_ascii=False))
        return 0
    if args.action == 'run':
        if args.command == 'note' and not args.original_sound:
            raise ValueError('ORIGINAL_SOUND_REQUIRED_USE_STEPS_FOR_MUSIC')
        if args.command == 'video':
            if args.declaration == 'none':
                raise ValueError('VIDEO_BROWSER_PUBLISH_REQUIRES_AIGC_DECLARATION')
            if not args.cover_vertical or not args.cover_horizontal:
                raise ValueError('DUAL_COVER_MISSING: 需要 --cover-vertical 和 --cover-horizontal')
    return (video if args.command == 'video' else note).execute(args)


def cli(argv=None):
    try:
        return main(argv)
    except PublishTextError as exc:
        print(json.dumps({'ok': False, 'error': 'CONTENT_FILE_INVALID', 'message': str(exc),
                          'publish_attempted': False}, ensure_ascii=False))
        return 1
    except video.PublishError as exc:
        print(json.dumps({'ok': False, 'error': exc.code, 'hint': exc.hint,
                          'publish_attempted': False}, ensure_ascii=False))
        return exc.exit_code
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    sys.exit(cli())

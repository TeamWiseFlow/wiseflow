#!/usr/bin/env python3
"""
Fill form fields and publish on WeChat Channels creator center via CDP.

Handles wujie shadow DOM for all form interactions.

Usage:
  python fill_form.py --title "标题" --cdp-port 18800
  python fill_form.py --caption "描述内容 #话题" --cdp-port 18800
  python fill_form.py --title "标题" --caption "描述" --cdp-port 18800
  python fill_form.py --publish --cdp-port 18800
  python fill_form.py --draft --cdp-port 18800
"""

import argparse
import json
import sys
import time

# Shadow DOM utility JS (same as upload_video.py)
DEEP_QUERY_JS = """
function wujieRoot() {
  var w = document.querySelector('wujie-app');
  return (w && w.shadowRoot) || null;
}
function deepQuery(selector) {
  var el = document.querySelector(selector);
  if (el) return el;
  var sr = wujieRoot();
  return sr ? sr.querySelector(selector) : null;
}
function deepQueryAll(selector) {
  var results = [];
  var main = document.querySelectorAll(selector);
  for (var i = 0; i < main.length; i++) results.push(main[i]);
  var sr = wujieRoot();
  if (sr) {
    var shadow = sr.querySelectorAll(selector);
    for (var i = 0; i < shadow.length; i++) results.push(shadow[i]);
  }
  return results;
}
function isVisible(el) {
  if (!el) return false;
  var rect = el.getBoundingClientRect();
  return rect.width > 0 && rect.height > 0;
}
"""


def evaluate_js(port, js_code):
    """Evaluate JavaScript in the page via CDP Runtime.evaluate."""
    import subprocess
    # Get tab list
    url = f"http://localhost:{port}/json"
    import urllib.request
    tabs = json.loads(urllib.request.urlopen(url, timeout=5).read())
    target = None
    for tab in tabs:
        if "channels.weixin.qq.com" in tab.get("url", ""):
            target = tab
            break
    if not target:
        for tab in tabs:
            if tab.get("type") == "page":
                target = tab
                break
    if not target:
        print("ERROR: No browser tab found", file=sys.stderr)
        return None

    ws_url = target["webSocketDebuggerUrl"]
    cmd = [
        "python3", "-c",
        f"""
import asyncio, json, websockets
async def main():
    async with websockets.connect("{ws_url}") as ws:
        msg = {{"id": 1, "method": "Runtime.evaluate", "params": {{"expression": {json.dumps(js_code)}, "returnByValue": True, "awaitPromise": True}}}}
        await ws.send(json.dumps(msg))
        resp = json.loads(await ws.recv())
        result = resp.get("result", {{}}).get("result", {{}})
        print(json.dumps(result.get("value")))
asyncio.run(main())
"""
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"CDP error: {result.stderr}", file=sys.stderr)
        return None
    try:
        val = result.stdout.strip()
        if val == "undefined" or val == "None":
            return None
        return json.loads(val)
    except json.JSONDecodeError:
        return result.stdout.strip() if result.stdout.strip() else None


def fill_field(port, selectors, text, field_name):
    """Fill a form field in shadow DOM with text."""
    js = f"""
    (function(selectors, text) {{
      {DEEP_QUERY_JS}

      var el = null;
      var foundSel = null;
      for (var i = 0; i < selectors.length; i++) {{
        var candidate = deepQuery(selectors[i]);
        if (candidate && isVisible(candidate)) {{
          el = candidate;
          foundSel = selectors[i];
          break;
        }}
      }}
      if (!el) return {{ ok: false }};

      el.focus();

      if (el.isContentEditable) {{
        el.textContent = '';
        var sel = window.getSelection();
        var range = document.createRange();
        range.selectNodeContents(el);
        range.collapse(false);
        if (sel) {{ sel.removeAllRanges(); sel.addRange(range); }}
        var inserted = document.execCommand('insertText', false, text);
        if (!inserted) el.textContent = text;
        el.dispatchEvent(new InputEvent('input', {{ bubbles: true, data: text, inputType: 'insertText' }}));
        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
      }} else {{
        var proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
        var nativeSetter = Object.getOwnPropertyDescriptor(proto, 'value') && Object.getOwnPropertyDescriptor(proto, 'value').set;
        if (nativeSetter) {{
          nativeSetter.call(el, text);
        }} else {{
          el.value = text;
        }}
        el.dispatchEvent(new InputEvent('input', {{ bubbles: true, data: text, inputType: 'insertText' }}));
        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
      }}

      var actual = el.isContentEditable ? (el.innerText || el.textContent || '') : (el.value || '');
      el.blur();
      return {{ ok: actual.indexOf(text) >= 0, sel: foundSel, actual: actual }};
    }})({json.dumps(selectors)}, {json.dumps(text)})
    """
    result = evaluate_js(port, js)
    if result and result.get("ok"):
        print(f"✅ {field_name} filled successfully (selector: {result.get('sel')})", file=sys.stderr)
        return True
    else:
        actual = result.get("actual", "") if result else "no result"
        print(f"❌ Failed to fill {field_name} (actual: {actual[:50]})", file=sys.stderr)
        return False


def click_publish(port, is_draft=False):
    """Click publish or draft button."""
    labels = ["存草稿", "保存草稿", "草稿"] if is_draft else ["发表", "发布"]
    js = f"""
    (function(labels) {{
      {DEEP_QUERY_JS}
      var btns = deepQueryAll('button');
      for (var i = 0; i < btns.length; i++) {{
        var btn = btns[i];
        var text = (btn.innerText || btn.textContent || '').trim();
        var isDisabled = btn.disabled || btn.getAttribute('disabled') !== null ||
                         btn.classList.contains('weui-desktop-btn_disabled');
        if (!isDisabled && isVisible(btn)) {{
          for (var j = 0; j < labels.length; j++) {{
            if (text === labels[j] || text.includes(labels[j])) {{
              btn.click();
              return {{ ok: true, text: text }};
            }}
          }}
        }}
      }}
      return {{ ok: false }};
    }})({json.dumps(labels)})
    """
    result = evaluate_js(port, js)
    if result and result.get("ok"):
        action = "draft saved" if is_draft else "published"
        print(f"✅ Clicked '{result.get('text')}' button ({action})", file=sys.stderr)
        return True
    else:
        print(f"❌ Could not find {'draft' if is_draft else 'publish'} button", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Fill form and publish on WeChat Channels via CDP")
    parser.add_argument("--cdp-port", type=int, default=18800, help="CDP port (default: 18800)")
    parser.add_argument("--title", help="Video title (短标题)")
    parser.add_argument("--caption", help="Description / caption (支持 #话题)")
    parser.add_argument("--publish", action="store_true", help="Click publish button")
    parser.add_argument("--draft", action="store_true", help="Click save draft button")
    args = parser.parse_args()

    port = args.cdp_port
    any_action = False

    # Fill title
    if args.title:
        title_selectors = [
            'input[placeholder*="短标题"]',
            'input[placeholder*="填写短标题"]',
            'input.weui-desktop-form__input[placeholder*="短标题"]',
            'input.weui-desktop-form__input',
        ]
        if fill_field(port, title_selectors, args.title, "Title"):
            any_action = True
            time.sleep(0.5)
        else:
            print("WARNING: Could not fill title, continuing...", file=sys.stderr)

    # Fill caption
    if args.caption:
        desc_selectors = [
            'div[contenteditable][data-placeholder="添加描述"]',
            'div.input-editor[contenteditable=""][data-placeholder="添加描述"]',
            'div[data-placeholder*="描述"][contenteditable]',
            'div.input-editor[contenteditable]',
        ]
        if fill_field(port, desc_selectors, args.caption, "Caption"):
            any_action = True
            time.sleep(0.5)
        else:
            print("WARNING: Could not fill caption, continuing...", file=sys.stderr)

    # Publish
    if args.publish:
        if click_publish(port, is_draft=False):
            any_action = True
            # Wait and verify
            time.sleep(4)
            js = f"""
            (() => {{
              {DEEP_QUERY_JS}
              var all = deepQueryAll('*');
              var markers = ['已发表', '发布成功', '发表成功', '审核中'];
              for (var i = 0; i < all.length; i++) {{
                var el = all[i];
                var text = (el.innerText || '').trim();
                if (el.children.length === 0 && text) {{
                  for (var j = 0; j < markers.length; j++) {{
                    if (text.includes(markers[j])) return {{ ok: true, msg: text }};
                  }}
                }}
              }}
              return {{ ok: false, url: location.href }};
            }})()
            """
            result = evaluate_js(port, js)
            if result and result.get("ok"):
                print(f"✅ Publish verified: {result.get('msg')}", file=sys.stderr)
            else:
                print("⚠️ Could not verify publish success, please check manually", file=sys.stderr)

    # Save draft
    if args.draft:
        if click_publish(port, is_draft=True):
            any_action = True

    if not any_action:
        print("No action specified. Use --title, --caption, --publish, or --draft", file=sys.stderr)
        sys.exit(1)

    print(json.dumps({"ok": True}))


if __name__ == "__main__":
    main()

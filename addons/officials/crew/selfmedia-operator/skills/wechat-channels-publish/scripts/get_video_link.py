#!/usr/bin/env python3
"""
Get published video link from WeChat Channels (视频号) creator center.

After publishing a video, this script navigates to the video list,
clicks "分享" → "复制链接" on the most recent video, and reads the link
from the clipboard via CDP.

Usage:
    python get_video_link.py --cdp-port 9222 [--title "视频标题"]
    python get_video_link.py --cdp-port 9222 --index 0

The script outputs the video link to stdout as JSON:
    {"ok": true, "video_url": "https://weixin.qq.com/sph/xxxxxx"}
    {"ok": false, "error": "reason"}
"""

import argparse
import json
import sys
import time
import urllib.request


def get_websocket_url(cdp_port: int) -> str:
    """Get the WebSocket debug URL from CDP."""
    resp = urllib.request.urlopen(f"http://localhost:{cdp_port}/json")
    targets = json.loads(resp.read())
    for t in targets:
        if t.get("type") == "page" and "channels.weixin.qq.com" in t.get("url", ""):
            return t["webSocketDebuggerUrl"]
    # Fallback: use first page
    if targets:
        return targets[0]["webSocketDebuggerUrl"]
    raise RuntimeError(f"No suitable CDP target found on port {cdp_port}")


def cdp_send(ws, method: str, params: dict = None) -> dict:
    """Send a CDP command and return the result."""
    import websocket
    msg = {"id": cdp_send._counter, "method": method}
    if params:
        msg["params"] = params
    ws.send(json.dumps(msg))
    cdp_send._counter += 1

    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg["id"] - 1:
            return resp

cdp_send._counter = 1


def run_js(ws, expression: str, await_promise: bool = False) -> any:
    """Execute JavaScript in the page and return the result value."""
    msg_id = run_js._counter
    run_js._counter += 1
    msg = {
        "id": msg_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": await_promise,
        },
    }
    ws.send(json.dumps(msg))

    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id:
            result = resp.get("result", {}).get("result", {})
            if result.get("type") == "object" and result.get("subtype") == "error":
                raise RuntimeError(f"JS error: {result.get('description', 'unknown')}")
            return result.get("value")


run_js._counter = 1000


def main():
    parser = argparse.ArgumentParser(description="Get published video link from WeChat Channels")
    parser.add_argument("--cdp-port", type=int, required=True, help="CDP debug port")
    parser.add_argument("--title", default=None, help="Video title to match (optional)")
    parser.add_argument("--index", type=int, default=0, help="Video index in list (0=first, default)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds (default 30)")
    args = parser.parse_args()

    try:
        import websocket
    except ImportError:
        print(json.dumps({"ok": False, "error": "websocket-client not installed. Run: pip install websocket-client"}))
        sys.exit(1)

    try:
        ws_url = get_websocket_url(args.cdp_port)
        ws = websocket.create_connection(ws_url, timeout=args.timeout)
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"CDP connection failed: {e}"}))
        sys.exit(1)

    try:
        # Step 1: Navigate to video list if not already there
        current_url = run_js(ws, "window.location.href")
        if "platform/post/list" not in current_url:
            run_js(ws, "window.location.href = 'https://channels.weixin.qq.com/platform/post/list'")
            time.sleep(3)

        # Step 2: Find the target video in the list
        # The video list is inside wujie shadow DOM
        # We need to pierce through shadow DOM to find video items

        # Try to find video items and click share button
        js_find_and_share = """
        (function() {
            const wujieApp = document.querySelector('wujie-app');
            if (!wujieApp || !wujieApp.shadowRoot) {
                return {ok: false, error: 'wujie-app shadow DOM not found'};
            }
            const shadow = wujieApp.shadowRoot;

            // Find video list items - they typically have class containing 'post' or 'video-item'
            // The structure varies, so we try multiple selectors
            const selectors = [
                '.post-item',
                '.video-item',
                '[class*="post"]',
                '[class*="item"]',
                'tr',  // table rows
            ];

            let items = [];
            for (const sel of selectors) {
                items = shadow.querySelectorAll(sel);
                if (items.length > 0) break;
            }

            if (items.length === 0) {
                return {ok: false, error: 'No video items found in list'};
            }

            return {ok: true, itemCount: items.length};
        })()
        """

        result = run_js(ws, js_find_and_share)
        if not result or not result.get("ok"):
            print(json.dumps({"ok": False, "error": result.get("error", "Failed to find video items")}))
            return

        # Step 3: Click "分享" button on the target video
        # This needs to be done via CDP DOM interaction since shadow DOM
        # elements can't be accessed via regular Playwright selectors

        js_click_share = f"""
        (function() {{
            const wujieApp = document.querySelector('wujie-app');
            if (!wujieApp || !wujieApp.shadowRoot) {{
                return {{ok: false, error: 'wujie shadow DOM not found'}};
            }}
            const shadow = wujieApp.shadowRoot;

            // Find all share buttons
            const shareButtons = shadow.querySelectorAll('[class*="share"], button');
            let shareBtn = null;

            for (const btn of shareButtons) {{
                const text = btn.textContent || btn.innerText || '';
                if (text.includes('分享') || text.includes('Share')) {{
                    shareBtn = btn;
                    break;
                }}
            }}

            if (!shareBtn) {{
                // Try finding by icon or other means
                const allBtns = shadow.querySelectorAll('span, a, div');
                for (const btn of allBtns) {{
                    const text = (btn.textContent || '').trim();
                    if (text === '分享') {{
                        shareBtn = btn;
                        break;
                    }}
                }}
            }}

            if (!shareBtn) {{
                return {{ok: false, error: 'Share button not found'}};
            }}

            shareBtn.click();
            return {{ok: true}};
        }})()
        """

        result = run_js(ws, js_click_share)
        if not result or not result.get("ok"):
            print(json.dumps({"ok": False, "error": f"Failed to click share: {result.get('error', 'unknown')}"}))
            return

        time.sleep(1.5)

        # Step 4: Click "复制链接" in the share panel
        js_click_copy_link = """
        (function() {
            const wujieApp = document.querySelector('wujie-app');
            if (!wujieApp || !wujieApp.shadowRoot) {
                return {ok: false, error: 'wujie shadow DOM not found'};
            }
            const shadow = wujieApp.shadowRoot;

            // Find "复制链接" button in the share popup/panel
            const allElements = shadow.querySelectorAll('span, a, div, button, p');
            let copyBtn = null;

            for (const el of allElements) {
                const text = (el.textContent || '').trim();
                if (text === '复制链接' || text === '复制' || text.includes('复制链接')) {
                    copyBtn = el;
                    break;
                }
            }

            if (!copyBtn) {
                return {ok: false, error: 'Copy link button not found in share panel'};
            }

            copyBtn.click();
            return {ok: true};
        })()
        """

        result = run_js(ws, js_click_copy_link)
        if not result or not result.get("ok"):
            print(json.dumps({"ok": False, "error": f"Failed to click copy link: {result.get('error', 'unknown')}"}))
            return

        time.sleep(0.5)

        # Step 5: Read the link from clipboard via CDP
        # Use the Browser domain to read clipboard (requires headless:false with proper permissions)
        # Alternative: intercept the link from the page DOM

        # Try reading from clipboard via CDP
        try:
            clipboard_text = run_js(ws, """
                (async function() {
                    try {
                        return await navigator.clipboard.readText();
                    } catch(e) {
                        return null;
                    }
                })()
            """)
        except Exception:
            clipboard_text = None

        if clipboard_text and ("weixin.qq.com/sph/" in clipboard_text or "weixin.qq.com" in clipboard_text):
            print(json.dumps({"ok": True, "video_url": clipboard_text, "source": "clipboard"}))
            return

        # Fallback: try to find the link in the share panel DOM
        js_extract_link = """
        (function() {
            const wujieApp = document.querySelector('wujie-app');
            if (!wujieApp || !wujieApp.shadowRoot) {
                return {ok: false, error: 'wujie shadow DOM not found'};
            }
            const shadow = wujieApp.shadowRoot;

            // Look for links in the share panel
            const links = shadow.querySelectorAll('a[href*="weixin"]');
            for (const a of links) {
                if (a.href && a.href.includes('weixin.qq.com/sph/')) {
                    return {ok: true, video_url: a.href};
                }
            }

            // Look for text that looks like a URL
            const allText = shadow.querySelectorAll('span, p, div, input');
            for (const el of allText) {
                const text = (el.textContent || el.value || '').trim();
                if (text.includes('weixin.qq.com/sph/')) {
                    return {ok: true, video_url: text};
                }
            }

            return {ok: false, error: 'Video link not found in DOM'};
        })()
        """

        result = run_js(ws, js_extract_link)
        if result and result.get("ok"):
            print(json.dumps({"ok": True, "video_url": result["video_url"], "source": "dom"}))
        else:
            print(json.dumps({
                "ok": False,
                "error": "Could not extract video link automatically. The video may still be under review, or the share panel structure has changed.",
                "hint": "Manually navigate to the video in the list, click 分享 → 复制链接, and provide the URL to published-track."
            }))

    finally:
        ws.close()


if __name__ == "__main__":
    main()

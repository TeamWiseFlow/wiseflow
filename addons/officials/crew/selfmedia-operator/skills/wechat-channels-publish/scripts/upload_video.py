#!/usr/bin/env python3
"""Upload video via single persistent WS connection (more reliable)."""
import argparse, asyncio, base64, json, os, sys, time, urllib.request
import websockets

CHUNK_SIZE = 50_000
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".webm"}
MIME_MAP = {".mp4": "video/mp4", ".mov": "video/quicktime", ".avi": "video/avi", ".webm": "video/webm"}


def get_target(port):
    url = f"http://127.0.0.1:{port}/json"
    tabs = json.loads(urllib.request.urlopen(url, timeout=5).read())
    for t in tabs:
        if "channels.weixin.qq.com" in t.get("url", "") and t.get("type") == "page":
            return t
    for t in tabs:
        if t.get("type") == "page":
            return t
    return None


class CDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self._msg_id = 0
        self._lock = asyncio.Lock()

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=128 * 1024 * 1024)

    async def close(self):
        if self.ws:
            await self.ws.close()
            self.ws = None

    async def send(self, method, params=None, timeout=60):
        self._msg_id += 1
        msg_id = self._msg_id
        async with self._lock:
            await self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                raw = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
                resp = json.loads(raw)
                if resp.get("id") == msg_id:
                    return resp
                # skip events

    async def eval_js(self, expr, timeout=60):
        r = await self.send("Runtime.evaluate", {
            "expression": expr, "returnByValue": True, "awaitPromise": True,
        }, timeout=timeout)
        if "error" in r:
            return {"__error": r["error"].get("text", "")}
        result = r.get("result", {}).get("result", {})
        if "exceptionDetails" in r.get("result", {}):
            return {"__exception": r["result"]["exceptionDetails"].get("text", "")}
        return result.get("value")


def click_upload_trigger_via(eval_fn):
    js = """(() => {
      var w = document.querySelector('wujie-app');
      var sr = w && w.shadowRoot;
      var sels = ['span.add-icon.weui-icon-outlined-add', 'div.upload-content', '.finder-video-upload-btn', 'div[class*=\"upload-content\"]'];
      for (var i = 0; i < sels.length; i++) {
        var el = (document.querySelector(sels[i])) || (sr ? sr.querySelector(sels[i]) : null);
        if (el) { el.click(); return JSON.stringify({ ok: true, sel: sels[i] }); }
      }
      return JSON.stringify({ ok: false });
    })()"""
    return eval_fn(js)


async def upload_cdp_attempt(client, video_path):
    """Try CDP setFileInputFiles via DOM.performSearch."""
    await click_upload_trigger_via(client.eval_js)
    await asyncio.sleep(1)
    r = await client.send("DOM.performSearch", {"query": "input[type=\"file\"]"})
    if not r or "result" not in r:
        return False
    search_id = r["result"].get("searchId")
    count = r["result"].get("resultCount", 0)
    if count == 0:
        print("  no file input found", file=sys.stderr)
        return False
    nr = await client.send("DOM.getSearchResults", {
        "searchId": search_id, "fromIndex": 0, "toIndex": count
    })
    if not nr or "result" not in nr:
        return False
    node_ids = nr["result"].get("nodeIds", [])
    abs_path = os.path.abspath(video_path)
    for nid in node_ids:
        r = await client.send("DOM.setFileInputFiles", {
            "files": [abs_path], "nodeId": nid
        })
        if r and "error" not in r:
            print(f"  OK CDP setFileInputFiles nodeId={nid}", file=sys.stderr)
            return True
    return False


async def upload_base64(client, video_path):
    with open(video_path, "rb") as f:
        file_data = f.read()
    b64 = base64.b64encode(file_data).decode("ascii")
    file_name = os.path.basename(video_path)
    ext = os.path.splitext(video_path)[1].lower()
    mime = MIME_MAP.get(ext, "video/mp4")
    r = await client.eval_js("(() => { window.__oc_chunks = []; return 'init'; })()")
    print("  init:", r, file=sys.stderr)
    total = (len(b64) + CHUNK_SIZE - 1) // CHUNK_SIZE
    print(f"  pushing {total} chunks...", file=sys.stderr)
    for i in range(0, len(b64), CHUNK_SIZE):
        chunk = b64[i:i + CHUNK_SIZE]
        await client.eval_js(f"((s) => {{ window.__oc_chunks.push(s); return window.__oc_chunks.length; }})({json.dumps(chunk)})", timeout=120)
        if (i // CHUNK_SIZE + 1) % 100 == 0:
            print(f"    pushed {i // CHUNK_SIZE + 1}/{total}", file=sys.stderr)
    # verify
    r = await client.eval_js("(() => JSON.stringify({type: typeof window.__oc_chunks, len: window.__oc_chunks.length}))()")
    print("  verify:", r, file=sys.stderr)
    # click
    click = await click_upload_trigger_via(client.eval_js)
    print("  click:", click, file=sys.stderr)
    await asyncio.sleep(0.5)
    # assemble & inject
    params_js = json.dumps({"fileName": file_name, "mimeType": mime})
    js = f"""((p) => {{
      var w = document.querySelector('wujie-app');
      var sr = w && w.shadowRoot;
      function q(sel) {{
        var el = document.querySelector(sel);
        if (el) return el;
        return sr ? sr.querySelector(sel) : null;
      }}
      var inputSels = ['input[type=\"file\"][accept*=\"video\"]', 'input[type=\"file\"]'];
      var input = null;
      for (var i = 0; i < inputSels.length; i++) {{
        input = q(inputSels[i]);
        if (input) break;
      }}
      if (!input) return JSON.stringify({{ ok: false, error: 'no file input' }});
      try {{
        var b64 = window.__oc_chunks.join('');
        window.__oc_chunks = [];
        var binary = atob(b64);
        var bytes = new Uint8Array(binary.length);
        for (var i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
        var dt = new DataTransfer();
        dt.items.add(new File([bytes], p.fileName, {{ type: p.mimeType }}));
        Object.defineProperty(input, 'files', {{ value: dt.files, configurable: true }});
        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
        input.dispatchEvent(new Event('input',  {{ bubbles: true }}));
        return JSON.stringify({{ ok: true, size: bytes.length }});
      }} catch(e) {{
        return JSON.stringify({{ ok: false, error: e.message, stack: e.stack }});
      }}
    }})({params_js})"""
    r = await client.eval_js(js, timeout=120)
    print("  inject:", r, file=sys.stderr)
    # JS returns JSON.stringify({ok: true, size: N}) — eval_js returns the
    # string, not a dict. Parse it to check the ok field.
    if isinstance(r, str):
        try:
            r = json.loads(r)
        except (json.JSONDecodeError, TypeError):
            pass
    if isinstance(r, dict) and r.get("ok"):
        return True
    return False


async def wait_for_upload(client, file_name, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        fname_js = json.dumps(file_name)
        js = f"""((fileName) => {{
          var w = document.querySelector('wujie-app');
          var sr = w && w.shadowRoot;
          function q(sel) {{
            var el = document.querySelector(sel);
            if (el) return el;
            return sr ? sr.querySelector(sel) : null;
          }}
          var root = sr || document;
          var bodyText = (root.innerText || root.textContent || '').trim();
          var uploading = q('[class*=\"upload\"][class*=\"progress\"]') ||
                          q('[class*=\"uploading\"]') ||
                          q('[class*=\"transcoding\"]') ||
                          q('.weui-desktop-upload__status');
          var preview = q('video') || q('[class*=\"preview-video\"]') || q('[class*=\"video-thumb\"]');
          var uploadFailed = q('[class*=\"upload-fail\"]') || q('[class*=\"upload-error\"]');
          if (uploadFailed || /上传失败|转码失败|处理失败/.test(bodyText)) return JSON.stringify({{ done: false, failed: true }});
          var hasFileEvidence = fileName && bodyText.indexOf(fileName) >= 0;
          var hasSuccessText = /上传成功|转码完成|处理完成/.test(bodyText);
          return JSON.stringify({{ done: !uploading && (!!preview || hasFileEvidence || hasSuccessText), failed: false }});
        }})({fname_js})"""
        r = await client.eval_js(js)
        # JS returns JSON.stringify(...) — eval_js may return the raw string
        if isinstance(r, str):
            try:
                r = json.loads(r)
            except (json.JSONDecodeError, TypeError):
                pass
        if isinstance(r, dict):
            if r.get("failed"):
                return False
            if r.get("done"):
                return True
        elapsed = int(time.time() - start)
        print(f"  waiting... ({elapsed}s/{timeout}s)", file=sys.stderr)
        await asyncio.sleep(3)
    return False


async def run(port, video_path, method, timeout):
    target = get_target(port)
    if not target:
        print("ERROR: no browser tab", file=sys.stderr)
        return False
    client = CDPClient(target["webSocketDebuggerUrl"])
    await client.connect()
    try:
        if method == "cdp":
            ok = await upload_cdp_attempt(client, video_path)
            if not ok:
                print("CDP setFileInput failed, fallback base64", file=sys.stderr)
                ok = await upload_base64(client, video_path)
        else:
            ok = await upload_base64(client, video_path)
        if not ok:
            return False
        ok = await wait_for_upload(client, os.path.basename(video_path), timeout)
        return ok
    finally:
        await client.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--cdp-port", type=int, default=18800)
    ap.add_argument("--method", choices=["cdp", "base64"], default="cdp")
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()
    video_path = os.path.abspath(args.video)
    if not os.path.isfile(video_path):
        print(f"ERROR: {video_path} not found", file=sys.stderr)
        sys.exit(1)
    if os.path.splitext(video_path)[1].lower() not in VIDEO_EXTS:
        print("ERROR: unsupported format", file=sys.stderr)
        sys.exit(1)
    ok = asyncio.run(run(args.cdp_port, video_path, args.method, args.timeout))
    if ok:
        print(json.dumps({"ok": True, "file": os.path.basename(video_path)}))
    else:
        print("ERROR: upload failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

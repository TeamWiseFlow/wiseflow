#!/usr/bin/env python3
"""
通过 CDP 为头条号文章上传封面图，并点击确定完成选择。

用法：
    python3 ./skills/toutiao-publish/scripts/cdp_cover_upload.py <image_path> [cdp_port]

前提：发布页面已打开，可处于任意状态（脚本会自动打开封面面板）。

流程：
    1. 若封面上传面板未打开，先点击 + 按钮（.article-cover-add）
    2. 用 DOM.setFileInputFiles 注入图片到 input[type=file][accept="image/*"]
    3. 等待缩略图出现后点击「确定」
"""
import sys, json, time, os, urllib.request

try:
    import websocket
except ImportError:
    print("ERROR: 缺少 websocket-client，请运行: pip install websocket-client")
    sys.exit(1)


def get_toutiao_tab(port):
    tabs = json.loads(urllib.request.urlopen("http://localhost:{}/json".format(port)).read())
    for tab in tabs:
        if "mp.toutiao.com" in tab.get("url", "") and tab.get("type") == "page":
            return tab["id"]
    raise RuntimeError("未找到头条号 tab，请确认浏览器已打开 mp.toutiao.com")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    image_path = os.path.abspath(sys.argv[1])
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 18800

    if not os.path.isfile(image_path):
        print("ERROR: 文件不存在: {}".format(image_path))
        sys.exit(1)

    tab_id = get_toutiao_tab(port)
    print("连接 tab: {}".format(tab_id))

    ws = websocket.WebSocket()
    ws.connect("ws://localhost:{}/devtools/page/{}".format(port, tab_id),
               suppress_origin=True, timeout=30)

    _id = 0
    def send(method, params=None):
        nonlocal _id
        _id += 1
        ws.send(json.dumps({"id": _id, "method": method, "params": params or {}}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == _id:
                return r

    def js(expr):
        r = send("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        return r.get("result", {}).get("result", {}).get("value")

    send("DOM.enable")

    # Step 1: 若面板未开，点击封面 + 按钮
    panel_open = js(
        "(function(){ var btns=document.querySelectorAll('button');"
        " for(var i=0;i<btns.length;i++){"
        "   if(btns[i].textContent.trim()==='本地上传' && btns[i].offsetParent) return true;"
        " } return false; })()"
    )
    if not panel_open:
        r = js(
            "(function(){ var el=document.querySelector('.article-cover-add');"
            " if(!el) return 'NOT FOUND'; el.click(); return 'clicked'; })()"
        )
        print("点击封面 + 按钮: {}".format(r))
        if r == "NOT FOUND":
            print("ERROR: 未找到封面 + 按钮，请确认页面已加载")
            ws.close()
            sys.exit(2)
        time.sleep(0.8)
    else:
        print("封面上传面板已打开")

    # Step 2: 注入文件到 input[type=file][accept="image/*"]
    root = send("DOM.getDocument")["result"]["root"]["nodeId"]
    result = send("DOM.querySelector", {
        "nodeId": root,
        "selector": 'input[type="file"][accept="image/*"]'
    })
    node_id = result["result"]["nodeId"]
    if not node_id:
        print("ERROR: 未找到封面 file input，请重试")
        ws.close()
        sys.exit(3)

    r = send("DOM.setFileInputFiles", {"nodeId": node_id, "files": [image_path]})
    if "error" in r:
        print("ERROR: setFileInputFiles 失败: {}".format(r["error"]))
        ws.close()
        sys.exit(4)
    print("图片已注入: {}".format(image_path))

    # Step 3: 等待缩略图出现，再点确定
    print("等待缩略图（最多 10s）...")
    for _ in range(20):
        time.sleep(0.5)
        uploaded = js(
            "(function(){ var el=document.querySelector('.image-item, .upload-list-item, [class*=\"upload\"][class*=\"item\"]');"
            " return el && el.offsetParent ? true : false; })()"
        )
        if uploaded:
            break

    time.sleep(0.3)
    r = js(
        "(function(){ var btns=document.querySelectorAll('button');"
        " for(var i=0;i<btns.length;i++){"
        "   if(btns[i].textContent.trim()==='确定'){btns[i].click();return 'clicked';}"
        " } return 'not found'; })()"
    )
    print("点击确定: {}".format(r))
    if r == "not found":
        print("WARNING: 未找到确定按钮，请手动点击确定完成封面选择")

    ws.close()
    print("OK: 封面上传完成")


if __name__ == "__main__":
    main()

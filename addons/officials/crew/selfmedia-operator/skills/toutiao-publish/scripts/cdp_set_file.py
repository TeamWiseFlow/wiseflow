#!/usr/bin/env python3
"""
通过 CDP DOM.setFileInputFiles 向已打开的 file input 注入文件。
用于头条号「文档导入」弹窗：browser upload 工具无法触发该 input，
需要直接走 CDP 底层。

用法：
    python3 ./skills/toutiao-publish/scripts/cdp_set_file.py <file_path> [cdp_port]

参数：
    file_path   要注入的文件绝对路径（必须是真实存在的文件）
    cdp_port    CDP 调试端口，默认 18800
"""
import sys
import json
import urllib.request

try:
    import websocket
except ImportError:
    print("ERROR: websocket-client not installed. Run: pip install websocket-client")
    sys.exit(1)


def get_toutiao_tab(port):
    url = f"http://localhost:{port}/json"
    tabs = json.loads(urllib.request.urlopen(url).read())
    # 优先找活跃的发布页
    for tab in tabs:
        if "mp.toutiao.com" in tab.get("url", "") and tab.get("type") == "page":
            return tab["id"]
    raise RuntimeError("未找到头条号 tab，请确认浏览器已打开 mp.toutiao.com")


def cdp_set_file(tab_id, file_path, port):
    ws = websocket.WebSocket()
    ws.connect(
        f"ws://localhost:{port}/devtools/page/{tab_id}",
        suppress_origin=True,
        timeout=15,
    )

    _id = 0

    def send(method, params=None):
        nonlocal _id
        _id += 1
        ws.send(json.dumps({"id": _id, "method": method, "params": params or {}}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == _id:
                return r

    send("DOM.enable")

    root_id = send("DOM.getDocument")["result"]["root"]["nodeId"]
    result = send("DOM.querySelector", {"nodeId": root_id, "selector": 'input[type="file"]'})
    node_id = result["result"]["nodeId"]

    if not node_id:
        ws.close()
        print("ERROR: 未找到 file input，请确认「文档导入」弹窗已打开")
        sys.exit(2)

    r = send("DOM.setFileInputFiles", {"nodeId": node_id, "files": [file_path]})
    ws.close()

    if "error" in r:
        print(f"ERROR: setFileInputFiles 失败: {r['error']}")
        sys.exit(3)

    print(f"OK: 文件已注入 → {file_path}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    file_path = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 18800

    import os
    if not os.path.isfile(file_path):
        print(f"ERROR: 文件不存在: {file_path}")
        sys.exit(1)

    tab_id = get_toutiao_tab(port)
    print(f"连接 tab: {tab_id}")
    cdp_set_file(tab_id, file_path, port)


if __name__ == "__main__":
    main()

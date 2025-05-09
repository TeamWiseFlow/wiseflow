from playwright.sync_api import sync_playwright # 或者 async_api for async

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True) # 浏览器窗口会显示出来
    page = browser.new_page()
    page.goto("https://mp.weixin.qq.com/s/t0aXokWLyKZFu7LpnUBU7w")
    print(page.content())
    browser.close()
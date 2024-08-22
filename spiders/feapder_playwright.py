import time
import subprocess
from playwright.sync_api import Playwright, Page, sync_playwright
import feapder
from feapder.utils.webdriver import PlaywrightDriver


class TestPlaywright(feapder.AirSpider):
    __custom_setting__ = dict(
        RENDER_DOWNLOADER="feapder.network.downloader.PlaywrightDownloader",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.playwright = None
        self.browser = None
        self.context = None

    def start_requests(self):
        # 启动本地 Chrome 浏览器并连接
        chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'
        debugging_port = "--remote-debugging-port=9222"
        command = f"{chrome_path} {debugging_port}"
        subprocess.Popen(command, shell=True)
        time.sleep(2)  # 等待浏览器启动并打开调试端口
        with sync_playwright() as playwright:
            self.playwright = playwright
            self.browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
            self.context = self.browser.contexts[0]
            print('self.context', self.context)
        print('连接成功')
        yield feapder.Request("https://www.temu.com", render=False, proxies={"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"})

    def parse(self, request, response):
        print('进入parse')
        page = self.context.new_page()  # 使用已连接的浏览器创建新页面
        print('进入page', page)
        # print('进入parse page', page)
        # page.goto(request.url)  # 打开目标页面

    def spider_end(self):
        # 在爬虫结束时关闭浏览器连接
        if self.browser:
            self.browser.close()


if __name__ == "__main__":
    TestPlaywright(thread_count=1).run()

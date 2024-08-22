import feapder
import time
from playwright.sync_api import Page, Response
from feapder.utils.webdriver import PlaywrightDriver, InterceptResponse, InterceptRequest


def on_response(response: Response):
    print(response.url)

class TestPlaywright(feapder.AirSpider):
    __custom_setting__ = dict(
        RENDER_DOWNLOADER="feapder.network.downloader.PlaywrightDownloader",
        PLAYWRIGHT=dict(
            # user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            # 字符串 或 无参函数，返回值为user_agent
            proxy='http://127.0.0.1:7897',
            headless=False,  # 是否为无头浏览器
            driver_type="chromium",  # chromium、firefox、webkit
            timeout=60,  # 请求超时时间
            window_size=(2100, 1200),  # 窗口大小
            executable_path="C:\Program Files\Google\Chrome\Application\chrome.exe",  # 浏览器路径，默认为默认路径
            use_stealth_js=True,
            download_path=None,  # 下载文件的路径
            render_time=0,  # 渲染时长，即打开网页等待指定时间后再获取源码
            wait_until="networkidle",  # 等待页面加载完成的事件,可选值："commit", "domcontentloaded", "load", "networkidle"
            storage_state_path="",  # 保存浏览器状态的路径
            url_regexes=["de-en/electronics-o3-248.html"],  # 拦截接口，支持正则，数组类型
            save_all=True,  # 是否保存所有拦截的接口
            connect_over_cdp="http://localhost:9222",

        )
    )

    def start_requests(self):
        yield feapder.Request("https://www.temu.com", render=True)
    def parse(self, request, response):
        driver: PlaywrightDriver = response.driver
        page: Page = driver.page

        # 等待页面完全加载
        page.wait_for_load_state("networkidle")
        time.sleep(120)
        # 获取拦截的接口响应
        # intercept_response: InterceptResponse = driver.get_response("de-en/electronics-o3-248.html")
        # if intercept_response:
        #     intercept_request: InterceptRequest = intercept_response.request
        #     req_url = intercept_request.url
        #     req_header = intercept_request.headers
        #     req_data = intercept_request.data
        #     print("请求 URL:", req_url)
        #     print("请求 Header:", req_header)
        #     print("请求 Data:", req_data)
        #     # 获取接口返回的 JSON 数据
        #     data = driver.get_json("de/api/poppy/v1/opt")
        #     if data:
        #         print("接口返回的数据:", data)
        #         products = data.get("data", {}).get("items", [])
        #         print("接口返回的商品列表:", products)
        #     else:
        #         print("未能获取到数据或数据格式错误")
        # else:
        #     print("未能拦截到指定接口的响应")
        # 循环处理多个链接
        for i in range(1, 100):  # 假设有最多 100 个链接，根据实际情况调整
            try:
                # 动态生成 XPath
                xpath = f'//*[@id="containerWithFilters"]/div[3]/div[2]/div[1]/div[{i}]/div/div/div[2]/a'

                # 查找并点击链接
                element = page.wait_for_selector(xpath, timeout=10000)
                if element:
                    href = element.get_attribute('href')
                    print(f'Href {i}:', href)
                    page.goto('https://www.temu.com' + href)
                else:
                    print(f'Link {i} not found')
                    continue  # 如果没有找到链接，则继续下一个

                time.sleep(10)

                # 查找第二个链接
                try:
                    print('当前页面链接', page.url, page)
                    time.sleep(10)
                    element2 = page.query_selector('//*[@id="rightContent"]/div[4]/div[1]/a')
                    if element2 is not None:
                        href2 = element2.get_attribute('href')
                        print('Href2:', href2)
                        page2 = driver.context.new_page()
                        page2.goto('https://www.temu.com' + href2)

                    else:
                        print('Element2 not found')
                        page.go_back()  # 返回到之前的页面
                        continue  # 跳过后续操作，继续下一个链接
                except TimeoutError:
                    print(f'Element2 not found or timed out for link {i}, returning to previous page')
                    page.go_back()  # 返回到之前的页面
                    continue  # 跳过后续操作，继续下一个链接

                time.sleep(10)

                # 点击最终元素
                page.click('//*[@id="main_scale"]/div[2]/div/div[1]/div/div/div[1]/div[2]/div[1]/h1')
                time.sleep(10)

                # 获取所有相关的文本内容
                elements = page.query_selector_all('div._3XGSUReo')
                for element in elements:
                    labels = element.query_selector_all('p')
                    for label in labels:
                        text = label.text_content()
                        print(text)

            except TimeoutError:
                print(f'Link {i} caused a timeout or was not found. Moving to next link.')
                continue  # 如果遇到超时或找不到链接，继续处理下一个链接

        # page.click('//*[@id="containerWithFilters"]/div[3]/div[2]/div[1]/div[1]/div/div')
        # contexts = driver.browser.contexts
        # print(f"Contexts: {contexts}, contexts: {len(contexts)}")
        # for context in contexts:
        #     pages = context.pages
        #     print(f"pages: {pages}, contexts: {len(pages)}")

        # 定义点击路径列表
        # click_paths = [
        #     '//*[@id="containerWithFilters"]/div[3]/div[2]/div[1]/div[1]/div/div',
        #     '//*[@id="rightContent"]/div[3]/div[1]/a/div/div[2]',
        #     '//*[@id="main_scale"]/div[2]/div/div[1]/div/div/div[1]/div[2]/div[1]'
        # ]
        #
        # # 循环处理每个点击路径
        # for path in click_paths:
        #     page.click(path)
        #     time.sleep(10)
        #     contexts = driver.browser.contexts
        #     for context in contexts:
        #         pages = context.pages
        #         print(f"Context: {context}, contexts: {len(contexts)}")
        #         page = pages[0]
        #
        # # 在最后一个窗口中提取内容
        # content = page.query_selector('//*[@id="main_scale"]/div[2]/div/div[6]/div[1]')
        # print('content', content.inner_text() if content else '未找到内容')

        # 清理缓存
        driver.clear_cache()


if __name__ == "__main__":
    TestPlaywright(thread_count=1).run()

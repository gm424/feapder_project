import feapder
import time
from items import SpiderDataItem
from utils import *
from playwright.sync_api import Page, Playwright, Response, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError,sync_playwright
from feapder.utils.webdriver import PlaywrightDriver, InterceptResponse, InterceptRequest
import os
import subprocess
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
            # storage_state_path=r"C:\Users\jw\Desktop\temu",
            storage_state_path="",
            url_regexes=["de-en/electronics-o3-248.html"],  # 拦截接口，支持正则，数组类型
            save_all=True,  # 是否保存所有拦截的接口
        )
    )
    def start_requests(self):
        yield feapder.Request("https://www.temu.com", render=True)

    def parse(self, request, response):
        time.sleep(120)
        driver: PlaywrightDriver = response.driver
        page: Page = driver.page
        data = {}
        # 等待页面完全加载
        page.wait_for_load_state("networkidle")
        # 循环处理多个链接
        for i in range(1, 100):  # 假设有最多 100 个链接，根据实际情况调整
            try:
                # 动态生成 XPath
                xpath = f'//*[@id="containerWithFilters"]/div[3]/div[2]/div[1]/div[{i}]'
                xpath2 = f'//*[@id="containerWithFilters"]/div[2]/div[1]/div[1]/div[{i}]'
                xpath3 = f'//*[@id="containerWithFilters"]/div[3]/div[1]/div[1]/div[{i}]'

                try:
                    print('当前页面链接', page.url)
                    product = page.wait_for_selector(xpath, timeout=10000)
                    if product:
                        path = xpath
                        print('xpath', path)
                    else:
                        product2 = page.wait_for_selector(xpath2, timeout=10000)
                        if product2:
                            path = xpath2
                            print('xpath2', path)
                        else:
                            path = xpath3
                            print('xpath3', path)
                    with page.expect_popup() as popup_info:
                        page.click(path)
                    img = page.wait_for_selector(f'{path}/div/div/div[1]/div/div/div[1]/span', timeout=10000)
                    if img:
                        # 获取 <img> 标签的 src 属性
                        img_element = img.query_selector('img')
                        if img_element:
                            img_url = img_element.get_attribute('src')
                            print(f'Image src: {img_url}')
                            data["img_url"] = img_url
                        else:
                            print("没有找到 img 元素")
                    else:
                        print("没有找到指定的 span 元素，请检查 XPath 是否正确")
                    h2_element = page.wait_for_selector(f'//*[@id="containerWithFilters"]/div[3]/div[2]/div[1]/div[{i}]/div/div/div[2]/a/h2',timeout=10000)
                    if h2_element:
                        # 获取 h2 元素的文本内容
                        text_content = h2_element.inner_text().strip()
                        data["name"] = text_content
                        print(f'Text content: {text_content}')
                    else:
                        print("没有找到 h2 元素，请检查 XPath 是否正确")
                    time.sleep(2)
                    new_page = popup_info.value
                    time.sleep(5)
                except (PlaywrightTimeoutError, PlaywrightError) as e:
                    print(f'XPath not found.')

                if new_page:
                    print('New page URL:', new_page.url, new_page)
                    try:
                        for f in range(2, 5):
                            try:
                                print('f', f)
                                with new_page.expect_popup() as popup_info:
                                    new_page.click(f'//*[@id="rightContent"]/div[{f}]/div[1]/a')
                                new_page2 = popup_info.value
                                print('成功找到element2')
                                time.sleep(5)
                                data['store_name'] = new_page2.query_selector('//*[@id="main_scale"]/div[2]/div/div[1]/div/div/div[1]/div[2]/div').inner_text().strip()
                                new_page2.click('//*[@id="main_scale"]/div[2]/div/div[1]/div/div/div[1]/div[2]/div')
                                print('已点击店铺名')
                                # 选择包含信息的最外层 div
                                time.sleep(5)
                                info_div = new_page2.query_selector('//*[@id="main_scale"]/div[2]/div/div[6]/div[1]/div[2]')
                                # 判断 info_div 是否为 None
                                if info_div is not None:
                                    print('打开弹窗')
                                else:
                                    new_page2.click('//*[@id="main_scale"]/div[2]/div/div[1]/div/div/div[1]/div[2]/div')
                                    print('再次点击店铺名')
                                sections = info_div.query_selector_all('div._3XGSUReo')
                                # 遍历每个 section，并打印标题和内容
                                if sections:
                                    data['company'] = sections[0].query_selector('p._3fmkb7bP').inner_text().strip()
                                    data['address'] = sections[1].query_selector('p._3fmkb7bP').inner_text().strip()
                                    print('data', data)
                                    spider_data_item = SpiderDataItem()
                                    spider_data_item["id"] = Snowflake().generate_id()
                                    spider_data_item["name"] = data['name']
                                    spider_data_item["img_url"] = data["img_url"]
                                    spider_data_item["company"] = data["company"]
                                    spider_data_item["address"] = data["address"]
                                    yield spider_data_item
                                time.sleep(2)
                                new_page2.close()
                                time.sleep(2)
                                new_page.close()
                                break
                            except (PlaywrightTimeoutError, PlaywrightError) as e:
                                print('未找到element2,继续')
                                continue

                    except TimeoutError:
                        print('Element2 not found')
                        new_page.close()
                        time.sleep(10)
                        continue
                else:
                    print('No new page found after clicking')
                    continue

            except TimeoutError:
                print(f'Link {i} caused a timeout or was not found. Moving to next link.')
                continue  # 如果遇到超时或找不到链接，继续处理下一个链接
        # 清理缓存
        driver.clear_cache()


if __name__ == "__main__":
    try:
        TestPlaywright(thread_count=1).run()
    except Exception as e:
        print(f"发生错误: {e}")


import feapder
from items import SpiderProductItem
import time
from datetime import datetime
from utils import *
from playwright.sync_api import Page
from playwright.sync_api import Response
from feapder.utils.webdriver import (
    PlaywrightDriver,
    InterceptResponse,
    InterceptRequest,
)
def on_response(response: Response):
    print(response.url)

class TestPlaywright(feapder.AirSpider):
    __custom_setting__ = dict(
        RENDER_DOWNLOADER="feapder.network.downloader.PlaywrightDownloader",
        PLAYWRIGHT=dict(
            user_agent=None,  # 字符串 或 无参函数，返回值为user_agent
            proxy=None,  # xxx.xxx.xxx.xxx:xxxx 或 无参函数，返回值为代理地址
            headless=False,  # 是否为无头浏览器
            driver_type="chromium",  # chromium、firefox、webkit
            timeout=30,  # 请求超时时间
            window_size=(1800, 800),  # 窗口大小
            executable_path=None,  # 浏览器路径，默认为默认路径
            download_path=None,  # 下载文件的路径
            render_time=0,  # 渲染时长，即打开网页等待指定时间后再获取源码
            wait_until="networkidle",  # 等待页面加载完成的事件,可选值："commit", "domcontentloaded", "load", "networkidle"
            use_stealth_js=False,  # 使用stealth.min.js隐藏浏览器特征
            # page_on_event_callback=dict(response=on_response),  # 监听response事件
            # page.on() 事件的回调 如 page_on_event_callback={"dialog": lambda dialog: dialog.accept()}
            storage_state_path=None,  # 保存浏览器状态的路径
            url_regexes=["api/competing-lookup"],  # 拦截接口，支持正则，数组类型

            save_all=True,  # 是否保存所有拦截的接口
        ),
    )
    def start_requests(self):
        yield feapder.Request("https://www.sellersprite.com/w/user/signin", render=True)

    def parse(self, reqeust, response):
        driver: PlaywrightDriver = response.driver
        page: Page = driver.page
        page.click('a[aria-controls="pills-account"]')
        print("Step1")
        page.wait_for_selector('//*[@id="form_signin_password"]/div[1]/input', state="visible", timeout=60000)
        page.type('//*[@id="form_signin_password"]/div[1]/input', "13670704438")
        page.type('//*[@id="form_signin_password"]/div[2]/input', "13670704438m.")
        print("Step2")
        page.click('//*[@id="form_signin_passW"]/div/div/button')
        print("Step3")
        new_url = "https://www.sellersprite.com/v3/competitor-lookup?market=DE&monthName=bsr_sales_nearly&asins=%5B%5D&page=1&nodeIdPaths=%5B%5D&symbolFlag=true&size=60&order%5Bfield%5D=total_units&order%5Bdesc%5D=true"  # 替换为你想导航的链接
        page.goto(new_url)
        print("Step4")

        # 等待页面加载完成
        page.wait_for_load_state("networkidle")

        # 检查是否登录成功，登录成功后获取拦截的请求
        if "/v3/competitor-lookup" in page.url:
           print("登录成功")

        time.sleep(10)

        intercept_response: InterceptResponse = driver.get_response("api/competing-lookup")
        print("请求intercept_response", intercept_response)
        intercept_request: InterceptRequest = intercept_response.request
        req_url = intercept_request.url
        req_header = intercept_request.headers
        req_data = intercept_request.data
        print("请求url", req_url)
        print("请求header", req_header)
        print("请求data", req_data)
        data = driver.get_json("api/competing-lookup")

        products = data.get("data", {}).get("items", [])
        print("接口返回的数据items", products)
        for product in products:
            spider_product_item = SpiderProductItem()
            spider_product_item["id"] = Snowflake().generate_id()
            spider_product_item["product_id"] = product.get("id")
            if product.get("syncTime") is not None:
                spider_product_item["sync_time"] = datetime.fromtimestamp(product.get("syncTime") / 1000)
            spider_product_item["asin"] = product.get("asin")
            spider_product_item["parent_asin"] = product.get("parent")
            spider_product_item["brand"] = product.get("brand")
            spider_product_item["big_image_url"] = product.get("bigImageUrl")
            spider_product_item["category_id"] = product.get("categoryId")
            spider_product_item["category_name"] = product.get("categoryName")
            spider_product_item["dimension_type"] = product.get("dimensionType")
            spider_product_item["dimensions"] = product.get("dimensions")
            spider_product_item["dimensions_tag"] = product.get("dimensionsTag")
            spider_product_item["image_url"] = product.get("imageUrl")
            spider_product_item["market_id"] = str(product.get("marketId"))
            spider_product_item["node_label_locale"] = str(product.get("nodeLabelLocale"))
            spider_product_item["node_label_path"] = str(product.get("nodeLabelPath"))
            spider_product_item["node_label_path_locale"] = str(product.get("nodeLabelPathLocale"))
            spider_product_item["sku"] = str(product.get("sku"))
            spider_product_item["title"] = str(product.get("title"))
            if product.get("firstReviewDate") is not None:
                spider_product_item["first_review_date"] = datetime.fromtimestamp(product.get("firstReviewDate") / 1000)
            spider_product_item["station"] = str(product.get("station"))
            spider_product_item["price"] = str(product.get("averagePrice"))
            spider_product_item["sub_total_amount"] = str(product.get("subTotalAmount"))
            spider_product_item["total_amount"] = str(product.get("totalAmount"))
            spider_product_item["weight"] = str(product.get("weightTag"))
            spider_product_item["total_amount"] = str(product.get("totalAmount"))
            spider_product_item["platform"] = str("AMAZON")
            seller = product.get("sellerDto")
            if seller is None:
                continue
            spider_product_item["seller_id"] = seller.get("sellerId")

            spider_product_item["seller_name"] = seller.get("shortName")
            spider_product_item["business_name"] = seller.get("businessName")
            spider_product_item["station"] = seller.get("station")
            spider_product_item["business_address"] = seller.get("businessAddress")
            spider_product_item["business_type"] = seller.get("businessType")
            spider_product_item["customer_address"] = seller.get("customerAddress")
            spider_product_item["email"] = seller.get("email")
            spider_product_item["manager"] = seller.get("manger")
            spider_product_item["nation"] = seller.get("nation")
            spider_product_item["phone"] = seller.get("phone")
            yield spider_product_item
        driver.clear_cache()




if __name__ == "__main__":
    TestPlaywright(thread_count=1).run()

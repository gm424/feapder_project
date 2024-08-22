from playwright.sync_api import Response


from feapder.utils.webdriver import (
    PlaywrightDriver,
    InterceptResponse,
    InterceptRequest,
)

import feapder

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
            window_size=(1024, 800),  # 窗口大小
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
        yield feapder.Request(

            "https://www.sellersprite.com/v3/competitor-lookup?market=DE&monthName=bsr_sales_nearly&asins=%5B%5D&page=1&nodeIdPaths=%5B%5D&symbolFlag=true&size=60&order%5Bfield%5D=total_units&order%5Bdesc%5D=true",
            render=True,
        )

    def download_midware(self, request):
        if not hasattr(request, 'headers') or request.headers is None:
            request.headers = {}
        # 添加 Cookie 到请求头
        request.headers.update({
            "accept": "application/json",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/json;charset=UTF-8",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Cookie": '_gid=GA1.2.1425788605.1722928730; 01c498a6a4309e28943d=f235c0f6a8ac6e768f58921e59d421cd; JSESSIONID=0F1AAA72B9F19A967DCE13639D6228B5; _fp=0cb62452d569892a96abea4ae9cecd88; _gaf_fp=99387f691a0542cc7ced719c7ea47639; MEIQIA_TRACK_ID=2kH7dC8YtC8OL8CWeUJ0q2cRqax; MEIQIA_VISIT_ID=2kH7d6HBfLprPAf5PwZjhz0W6NU; current_guest=LFxV3P6Upqu9_240806-151806; rank-login-user=7146892271O4EzR0y/C8y4QD7aOKZfh3onr06X2lJbN3oY7Q5IDefB+Seu7wh/h9+9crJn5Bsn; rank-login-user-info=eyJuaWNrbmFtZSI6ImdtNDI0IiwiaXNBZG1pbiI6ZmFsc2UsImFjY291bnQiOiIxMzYqKioqNDQzOCIsInRva2VuIjoiNzE0Njg5MjI3MU80RXpSMHkvQzh5NFFEN2FPS1pmaDNvbnIwNlgybEpiTjNvWTdRNUlEZWZCK1NldTd3aC9oOSs5Y3JKbjVCc24ifQ==; Sprite-X-Token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2Nzk5NjI2YmZlMDQzZTBiYzI5NTEwMTE4ODA3YWExIn0.eyJqdGkiOiJ1OENJTW84ZGZPTWNwZkdHLWNOa01nIiwiaWF0IjoxNzIyOTI4ODE3LCJleHAiOjE3MjMwMTUyMTcsIm5iZiI6MTcyMjkyODc1Nywic3ViIjoieXVueWEiLCJpc3MiOiJyYW5rIiwiYXVkIjoic2VsbGVyU3BhY2UiLCJpZCI6MTEzMjExNywicGkiOm51bGwsIm5uIjoiZ200MjQiLCJzeXMiOiJTU19DTiIsImVkIjoiTiIsInBobiI6IjEzNjcwNzA0NDM4IiwiZW0iOiIyMjE3ODgyMjQ5QHFxLmNvbSIsIm1sIjoiRyJ9.ZSSfcaVlhp64HZoll9d_gcM1FL-UsSc6VdL3yXyEAbivaIFBRBAOX9_gXBIRuapsUV99XW76tTPo1agQzIG4nfADqf0CeFS0NTGJalE96sbRVsYMwbbCqQ2Z1EQZ3b-c-d0A8wReMsziOaLek2PDilV8a1O1wRHk5l3R3EfGlrb221FGZNbtrwz3NGV72yHBplMKtMVxOL5GbHA1gdpHyV7tZEJoTpk-clKm1gsGRfjc_fsXivhQnksDipSXbj9opmVsGsYftr2YyNZ7jgK3Ti53Mro8Vhvi_Uqd3oGQ3aBz8njE2OAcsdoaYKw0WnbaINHUK43RyCQ1mhNDZ7_wlw; ao_lo_to_n=7146892271O4EzR0y/C8y4QD7aOKZfh3onr06X2lJbN3oY7Q5IDeemCBGKAlYCOVDyg1vEZt4vis4QSLIuyTN0YHopQu39U26ynixZltsOzgI/ejcygZw=; _gat_gtag_UA_135032196_1=1; _ga=GA1.1.159667367.1722928730; _ga_38NCVF2XST=GS1.1.1722925813.4.1.1722928817.59.0.0; _ga_CTHVPP65BQ=GS1.1.1722925813.4.1.1722928817.0.0.0; rank-guest-user=9146892271Ri8c0wf8KNaIcu5m5TNFMNi+xRaRi6BAWpTqh3RiH1qagG/7zUO+bg40qTNHZ8U6; _ga_CN0F80S6GL=GS1.1.1722928338.1.1.1722928821.0.0.0'
        })
        # 打印已更新的请求头进行调试
        print("Updated headers: ", request.headers)
        return request

    def parse(self, reqeust, response):

        driver: PlaywrightDriver = response.driver
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
        print("接口返回的数据", data)
        #
        # print("------ 测试save_all=True ------- ")
        #
        # # 测试save_all=True
        # all_intercept_response: list = driver.get_all_response("competing-lookup")
        # for intercept_response in all_intercept_response:
        #     intercept_request: InterceptRequest = intercept_response.request
        #     req_url = intercept_request.url
        #     req_header = intercept_request.headers
        #     req_data = intercept_request.data
        #     print("请求url", req_url)
        #     print("请求header", req_header)
        #     print("请求data", req_data)
        #
        # all_intercept_json = driver.get_all_json("competing-lookup")
        # for intercept_json in all_intercept_json:
        #     print("接口返回的数据", intercept_json)

        # 千万别忘了
        driver.clear_cache()


if __name__ == "__main__":
    TestPlaywright(thread_count=1).run()

import playwright
from playwright.sync_api import Playwright, sync_playwright
import subprocess

#输入Chrome浏览器所在路径
chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'
debugging_port = "--remote-debugging-port=9222"

command = f"{chrome_path} {debugging_port}"
subprocess.Popen(command, shell=True)

def run(playwright :Playwright) -> None:
    print('come in')
    browser = playwright.chromium.connect_over_cdp(("http://localhost:9222"))
    context = browser.contexts[0]
    page = context.new_page()
    page.goto('https://www.temu.com')

with sync_playwright() as playwright:
    run(playwright)
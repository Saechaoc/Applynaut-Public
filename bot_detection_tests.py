from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import time


def browserOptions():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-gpu')

    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    options.add_argument("-profile")
    options.add_experimental_option(
        "excludeSwitches", ["enable-logging", "enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    return options


options = browserOptions()
driver = webdriver.Chrome(
    options=options, executable_path=r'C:\Users\chris\Documents\GitHub\EasyApplyJobsBot\chromedriver-win64\chromedriver.exe')


ua = UserAgent()
user_agent = ua.random
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win64",
        webgl_vendor="Google Inc. (NVIDIA)",
        renderer="ANGLE (NVIDIA, NVIDIA GeForce GTX 970 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        fix_hairline=True
        )
# {     "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"


url = "https://bot.sannysoft.com/"
driver.get(url)
time.sleep(99999)

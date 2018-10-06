#
# 当前文件夹下需放入驱动文件: chromedriver.exe
#

import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def get_yahoo_cookies():
    """获取雅虎所需cookie"""

    # 启动selenium
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    this_dir = os.path.abspath(os.path.dirname(__file__))
    driver = webdriver.Chrome(os.path.join(this_dir, 'chromedriver.exe'))

    # get cookies
    driver.get('https://uk.search.yahoo.com/search?pz=10&p=key&b=101')
    wait = WebDriverWait(driver, 10)
    wait.until(lambda driver: 'oath' in driver.current_url)

    driver.find_element_by_css_selector('div > input[type=submit]').click()

    cookies = driver.get_cookies()
    driver.close()
    return cookies


yahoo_cookies = get_yahoo_cookies()

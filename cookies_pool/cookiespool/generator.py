import json

import requests
import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .config import *
from .db import *
from .verify import Yundama


class CookiesGenerator(object):
    def __init__(self, name='name', brower_type=DEFAULT_BROWSER):
        """
        父类
        :param brower_type:
        """
        self.name = name
        self.cookies_db = CookiesRedisClient(name=self.name)
        self.accounts_db = AccountRedisClient(name=self.name)
        self.browser_type = brower_type

    def _init_browser(self, browser_type):
        """
        通过browser参数初始化全局浏览器供模拟登录使用
        :param browser: 浏览器 PhantomJS/ Chrome
        :return:
        """
        if browser_type == 'PhantomJS':
            caps = DesiredCapabilities.PHANTOMJS
            caps[
                "phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
            self.browser = webdriver.PhantomJS(desired_capabilities=caps)
            self.browser.set_window_size(1400, 500)
        elif browser_type == 'Chrome':
            self.browser = webdriver.Chrome()

    def new_cookies(self, username, password):
        raise NotImplemented

    def set_cookies(self, account):
        """
        根据账户设置新的cookies
        :param account:
        :return:
        """
        result = self.new_cookies(account.get('username'), account.get('password'))
        if result:
            username, cookies = result
            print('Saving Cookies to Redis', username, cookies)
            self.cookies_db.set(username, cookies)

    def run(self):
        """
        运行，得到所有账户，然后顺次模拟登陆
        :return:
        """
        accounts = self.accounts_db.all()
        cookies = self.cookies_db.all()
        accounts = list(accounts)
        valid_users = [cookie.get('username') for cookie in cookies]
        print('Geting', len(accounts), 'accounts from Redis')
        if len(accounts):
            self._init_browser(browser_type=self.browser_type)
        for account in accounts:
            if account.get('username') not in valid_users:
                print('Getting Cookies of ', self.name, account.get('username'), account.get('password'))
                self.set_cookies(account)
        print('Generator Run Finished')

    def close(self):
        try:
            print('Closing browser')
            self.browser.close()
            del self.browser
        except TypeError:
            print('Browser not opened')


class WeiboCookiesGenerator(CookiesGenerator):
    def __init__(self, name='weibo', browser_type='DEFAULT_BROWSER'):
        CookiesGenerator.__init__(self, name, browser_type)
        self.name = name
        self.ydm = Yundama(YUNDAMA_USERNAME, YUNDAMA_PASSWORD, YUNDAMA_APP_ID, YUNDAMA_APP_KEY)

    def _success(self, username):
        wait = WebDriverWait(self.browser, 5)
        success = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'me_portrait_w')))
        if success:
            print('登陆成功')
            self.browser.get('http://weibo.cn')

            if '我的首页' in self.browser.title:
                print(self.browser.get_cookies())
                cookies = {}
                for cookie in self.browser.get_cookies():
                    cookies[cookie['name']] = cookie['value']
                print(cookies)
                print('成功获取到cookies')
                return (username, json.dumps(cookies))

    def new_cookies(self, username, password):
        """
        生成Cookies
        :param username: 用户名
        :param password: 密码
        :return: 用户名和Cookies
        """
        print('Generating Cookies of', username)
        self.browser.delete_all_cookies()
        self.browser.get('http://my.sina.com.cn/profile/unlogin')
        wait = WebDriverWait(self.browser, 20)

        try:
            login = wait.until(EC.visibility_of_element_located((By.ID, 'hd_login')))
            login.click()
            user = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginformlist input[name="loginname"]')))
            user.send_keys(username)
            psd = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginformlist input[name="password"]')))
            psd.send_keys(password)
            submit = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.login_btn')))
            submit.click()
            try:
                result = self._success(username)
                if result:
                    return result
            except TimeoutException:
                print('出现验证码，开始识别验证码')
                yzm = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginform_yzm .yzm')))
                url = yzm.get_attribute('src')
                cookies = self.browser.get_cookies()
                cookies_dict = {}
                for cookie in cookies:
                    cookies_dict[cookie.get('name')] = cookie.get('value')
                response = requests.get(url, cookies=cookies_dict)
                result = self.ydm.identify(stream=response.content)
                if not result:
                    print('验证码识别失败, 跳过识别')
                    return
                door = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginform_yzm input[name="door"]')))
                door.send_keys(result)
                submit.click()
                result = self._success(username)
                if result:
                    return result
        except WebDriverException as e:
            print(e.args)


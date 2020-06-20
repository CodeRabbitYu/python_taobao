# -*- coding: UTF-8 -*-

import pyautogui
import logging
import time
import random
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import ActionChains
import re
from bs4 import BeautifulSoup
import json
import pandas as pd
import os

from selenium.webdriver.support.ui import WebDriverWait  # 导入selenium加载判断


# 淘宝商品excel文件保存路径
GOODS_EXCEL_PATH = 'taobao_goods.xlsx'

pyautogui.PAUSE = 0.5
# pyautogui.FAILSAFE = False

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# wait = WebDriverWait(browser, 10)


class TaoBao():
    def __init__(self):

        # options = webdriver.ChromeOptions()
        # options.add_experimental_option(
        #     'excludeSwitches', ['enable-automation'])  # 切换到开发者模式

        # self.browser = webdriver.Chrome(
        #     "/Users/Rabbit/Downloads/Compressed/chromedriver")
        self.browser = webdriver.Firefox()
        # 最大化窗口
        self.browser.maximize_window()
        self.browser.implicitly_wait(5)
        self.domain = 'http://www.taobao.com'
        self.action_chains = ActionChains(self.browser)

    def login(self, username, password):
        while True:
            self.browser.get(self.domain)
            time.sleep(1)

            # 会xpath可以简化这几步
            # self.browser.find_element_by_class_name('h').click()
            # self.browser.find_element_by_id('fm-login-id').send_keys(username)
            # self.browser.find_element_by_id('fm-login-password').send_keys(password)
            self.browser.find_element_by_xpath(
                '//*[@id="J_SiteNavLogin"]/div[1]/div[1]/a[1]').click()
            self.browser.find_element_by_xpath(
                '//*[@id="fm-login-id"]').send_keys(username)
            self.browser.find_element_by_xpath(
                '//*[@id="fm-login-password"]').send_keys(password)
            time.sleep(1)

            try:
                # 出现验证码，滑动验证
                slider = self.browser.find_element_by_xpath(
                    "//span[contains(@class, 'btn_slide')]")
                if slider.is_displayed():
                    # 拖拽滑块
                    self.action_chains.drag_and_drop_by_offset(
                        slider, 258, 0).perform()
                    time.sleep(0.5)
                    # 释放滑块，相当于点击拖拽之后的释放鼠标
                    self.action_chains.release().perform()

                    '''
                    因为不知名原因，导致我的截图都无法识别，所以，使用 "自带的" 截图工具，大致查看登录按钮的坐标，用来模拟点击登录
                    谷歌浏览器和火狐浏览器，登录按钮的坐标不一样，需要手动更改
                    切换到开发者模式后，y轴高度需要减少50
                    如果出现滑块验证码，那么高度相应增加了100，如果没有滑块验证吗，会走下面的except中的方法
                    '''
                    # pyautogui.click(x=1160, y=650, duration=1)
                    pyautogui.click(x=1160, y=600)

            except (NoSuchElementException, WebDriverException):
                logger.info('未出现登录验证码')
                # pyautogui.click(x=1160, y=550, duration=1)
                pyautogui.click(x=1160, y=550)
            # 会xpath可以简化点击登陆按钮，但都无法登录，需要使用 pyautogui 完成点击事件
            # self.browser.find_element_by_class_name('password-login').click()
            # self.browser.find_element_by_xpath('//*[@id="login-form"]/div[4]/button').click()

            '''
            如果想要使用图片搜索模式，可以将下面的代码打开。
            '''
            # try:
            # # 图片地址
            #     coords = pyautogui.locateOnScreen(
            #         '/Users/Rabbit/Desktop/Python/淘宝/login.png')
            #     x, y = pyautogui.center(coords)
            #     # print(x, y)
            #     pyautogui.leftClick(x, y)
            # except TypeError:
            #     print('没有找到图片')

            nickname = self.get_nickname()
            if nickname:
                logger.info('登录成功，呢称为:' + nickname)

                return True
            logger.debug('登录出错，5s后继续登录')
            time.sleep(5)

    def search(self, searchKey, page):
        # self.browser.get(self.domain)
        # time.sleep(1)
        self.browser.find_element_by_xpath(
            '//*[@id="q"]').send_keys(searchKey)
        pyautogui.press('enter')
        time.sleep(2)

        # 写入数据前先清空之前的数据
        if os.path.exists(GOODS_EXCEL_PATH):
            os.remove(GOODS_EXCEL_PATH)

        try:
            for i in range(1, page + 1):
                print('正在爬取第%d页...' % i)
                if i > 1:
                    self.next_page()
                    # 设置一个时间间隔
                    time.sleep(random.randint(3, 5))
                self.spider('bs')
            self.browser.close()
        except TypeError:
            print('循环出错了？')
            self.search(searchKey, page)

    def spider(self, type):
        if type == 'bs':
            self.spiderWithBS()
        elif type == 'json':
            self.spiderWithJson()

    def spiderWithJson(self):
        soup = BeautifulSoup(
            self.browser.page_source, "html.parser")
        pageConfig = soup.find(
            'script', text=re.compile('g_page_config'))

        neededColumns = ['category', 'comment_count', 'item_loc',
                         'nick', 'raw_title', 'view_price', 'view_sales']
        PageConfig = re.search(
            'g_page_config = (.*?);\n', pageConfig.string)
        pageConfigJson = json.loads(PageConfig.group(1))
        items = pageConfigJson['mods']['itemlist']['data']['auctions']
        pageItemsJson = json.dumps(items)
        # pageData = pd.read_json(pageItemsJson)
        # neededData = pageData[Paser.neededColumns]
        # print(pageItemsJson)
        print('-' * 100)
        for item in items:
            print(item['raw_title'])
            print(item['view_price'])

    def spiderWithBS(self):
        soup = BeautifulSoup(
            self.browser.page_source, "html.parser")
        items = soup.select("#mainsrp-itemlist .items .item")

        print('*' * 100)

        goods_list = []

        for item in items:
            title = item.select('.title')[0].text.strip()
            price = item.select('.price')[0].text.strip()
            shop_img = item.select('.pic .img')[0].attrs['data-src']
            goods_url = item.select('.pic a')[0].attrs['href']
            dealCount = item.select('.deal-cnt')[0].text.strip()
            shop = item.select('.shop')[0].text.strip()
            location = item.select('.location')[0].text.strip()
            mailFrees = item.select('.ship')
            isMailFree = '是' if len(mailFrees) > 0 else '否'
            icons = item.select('.icons')
            for icon in icons:
                isTmall = '是' if len(icon.select(
                    '.icon-service-tianmao')) > 0 else '否'
                isActivity = '是' if len(icon.select(
                    '.icon-2020618kuanghuanB')) > 0 else '否'
            goods = {
                '标题': title,
                '价格': price,
                '店铺': shop,
                '销量': dealCount,
                '店铺位置': location,
                '是否包邮': isMailFree,
                '是否是天猫': isTmall,
                '是否参加活动': isActivity,
                '商品图片': shop_img,
                '商品地址': goods_url,
            }
            goods_list.append(goods)
        self.saveExcel(goods_list)

    def saveExcel(self, goods_list):
        """
        将json数据生成excel文件
        :param goods_list: 商品数据
        :param startrow: 数据写入开始行
        :return:
        """
        # pandas没有对excel没有追加模式，只能先读后写
        if os.path.exists(GOODS_EXCEL_PATH):
            df = pd.read_excel(GOODS_EXCEL_PATH)
            df = df.append(goods_list)
        else:
            df = pd.DataFrame(goods_list)

        writer = pd.ExcelWriter(
            GOODS_EXCEL_PATH)  # pylint: disable=abstract-class-instantiated
        # columns参数用于指定生成的excel中列的顺序
        df.to_excel(excel_writer=writer, columns=['标题', '价格', '店铺', '销量', '店铺位置', '是否包邮', '是否是天猫', '是否参加活动', '商品地址',  '商品图片'], index=False,
                    encoding='utf-8', sheet_name='Sheet')
        writer.save()
        writer.close()

    def next_page(self):
        time.sleep(3)
        next_button = self.browser.find_element_by_css_selector(
            'li.item.next')           # 翻页按钮
        if 'next-disabled' not in next_button.get_attribute('class'):
            next_button.click()
        return self.browser.current_url

    def get_nickname(self):
        '''
        如果账号未在电脑登陆过，会出现验证页面，这里的时间没办法确定。
        '''
        time.sleep(10)

        self.browser.get(self.domain)
        time.sleep(0.5)
        try:
            return self.browser.find_element_by_class_name('site-nav-user').text
        except NoSuchElementException:
            return ''


if __name__ == '__main__':
    # 填入自己的用户名，密
    username = '13940476277'
    password = 'abc87342521'
    searchKey = '防晒衣'
    page = 20
    tb = TaoBao()
    isLogin = tb.login(username, password)
    if isLogin:
        print('登陆成功')
        # tb.main()
        tb.search(searchKey, page)

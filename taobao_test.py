# -*- coding: UTF-8 -*-
import os
import re
import json
import time
import random

import requests


# 关闭警告
requests.packages.urllib3.disable_warnings()
# 登录与爬取需使用同一个Session对象
req_session = requests.Session()


class GoodsSpider:

    def __init__(self, q):
        self.q = q
        # 超时
        self.timeout = 15
        self.goods_list = []
        # 淘宝登录
        # tbl = TaoBaoLogin(req_session)
        # tbl.login()

    def spider_goods(self, page):
        """
        :param page: 淘宝分页参数
        :return:
        """
        s = page * 44
        # 搜索链接，q参数表示搜索关键字，s=page*44 数据开始索引
        # search_url = 'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q={self.q}&suggest=history_1&_input_charset=utf-8&wq=biyunt&suggest_query=biyunt&source=suggest&bcoffset=4&p4ppushleft=%2C48&s={s}&data-key=s&data-value={s + 44}'
        # search_url = 'https://s.taobao.com/search?q={self.q}&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20200605&ie=utf8&s={s}&data-key=s&data-value={s + 44}'
        search_url = 'https://s.taobao.com/search?q=python&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20200605&ie=utf8'

        # 代理ip，网上搜一个，猪哥使用的是 站大爷：http://ip.zdaye.com/dayProxy.html
        # 尽量使用最新的，可能某些ip不能使用，多试几个。后期可以考虑做一个ip池
        # 爬取淘宝ip要求很高，西刺代理免费ip基本都不能用，如果不能爬取就更换代理ip
        proxies = {'http': '112.250.107.37:53281'}

        # 请求头
        headers = {
            'referer': 'https://www.taobao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        response = req_session.get(search_url, headers=headers, proxies=proxies,
                                   verify=False, timeout=self.timeout)

        print(response.text)

        goods_match = re.search('g_page_config = (.*?)}};', response.text)
        print(goods_match)


gs = GoodsSpider('python')
gs.spider_goods(1)

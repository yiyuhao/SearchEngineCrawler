#
#      File: config.py
#   Project: payunion
#    Author: Yi Yuhao
#
#   Copyright (c) 2018 麦禾互动. All rights reserved.

from random import randint


class RequestPriorityConfig:

    @property
    def search_engine_pages(self):
        """搜索引擎结果页"""
        return randint(301, 400)

    @property
    def website_contact(self):
        """网站联系我们页面"""
        return randint(201, 300)

    @property
    def website_homepage(self):
        """网站首页"""
        return randint(101, 200)

    @property
    def website_next_page_url(self):
        """网站二级页面"""
        return randint(1, 100)


request_priority_config = RequestPriorityConfig()


class Todo:
    todo = [
        '根据request id结束爬虫(redis中删除request)',
        '突破反爬',
        '重构zrem, zadd等系列逻辑'
    ]

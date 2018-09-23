#
#      File: config.py
#   Project: payunion
#    Author: Yi Yuhao
#
#   Copyright (c) 2018 麦禾互动. All rights reserved.


class RequestPriorityConfig:
    search_engine_pages = 1000
    website_contact = 800
    website_homepage = 600
    website_next_page_url = 400


class Todo:
    todo = [
        '根据request id结束爬虫(redis中删除request)',
        '突破反爬',
        '重构zrem, zadd等系列逻辑'
    ]

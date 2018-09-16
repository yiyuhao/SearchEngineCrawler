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
        'bug: scrapy request 去重(不同request爬取了相同网站时，第二个会被过滤掉), 暂时设置redis中url为zset 通过score设置timestamp来存TTL',
        '根据request id结束爬虫(redis中删除request)',
        '突破反爬',
    ]

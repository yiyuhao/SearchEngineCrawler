#
#      File: config.py
#   Project: payunion
#    Author: Yi Yuhao
#
#   Copyright (c) 2018 麦禾互动. All rights reserved.


class RequestPriorityConfig:
    search_engine_pages = 1000  # 搜索引擎结果页
    website_contact = 800  # 网站联系我们页面
    website_homepage = 600  # 网站首页
    website_next_page_url = 400  # 网站二级页面


class Todo:
    todo = [
        '根据request id结束爬虫(redis中删除request)',
        '突破反爬',
        '重构zrem, zadd等系列逻辑'
    ]

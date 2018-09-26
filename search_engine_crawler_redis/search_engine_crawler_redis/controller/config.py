from random import randint


class RequestPriorityConfig:

    @property
    def website_contact(self):
        """网站联系我们页面"""
        return randint(601, 900)

    @property
    def search_engine_pages(self):
        """搜索引擎结果页"""
        return randint(401, 600)

    @property
    def website_homepage(self):
        """网站首页"""
        return randint(301, 501)

    @property
    def website_next_page_url(self):
        """网站二级页面"""
        return randint(1, 300)


request_priority_config = RequestPriorityConfig()


class CrawConfig:
    MAX_ITEM_PER_PAGE = 20


class Todo:
    todo = [
        # '根据request id结束爬虫(redis中删除request)',
        '突破google反爬, fake_user_agent, proxy ip',
        '重构zrem, zadd等系列逻辑',
        '百度搜索结果地址包含在js中因此无法获取到网站首页url'
    ]

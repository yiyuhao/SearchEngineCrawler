import scrapy

from .search_engine import SearchEngine


class Rule:

    def __init__(self, spider, engine: str, search_keywords: str, width: int = 1):
        self.spider = spider
        self.engine = SearchEngine(engine)
        self.search_keywords = search_keywords
        self.width = width

    @property
    def page_urls(self):
        return self.engine.page_urls(search_num=self.width, search_keywords=self.search_keywords)

    @property
    def scrapy_requests(self):
        """all search engine page"""

        scrapy_requests = (
            scrapy.Request(
                url=url,
                callback=self.spider.parse_search_result_page,
                meta=dict(engine_selector=self.engine.result_selector))
            for url in self.page_urls
        )

        return scrapy_requests

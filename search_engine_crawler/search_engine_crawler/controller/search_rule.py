import scrapy
from scrapy.linkextractor import LinkExtractor

from .search_engine import SearchEngine


class Rule:

    def __init__(self, engine: str, search_keywords: str, width: int=21):
        self.engine = SearchEngine(engine)
        self.search_keywords = search_keywords
        self.width = width
        self.link_extractor = LinkExtractor(restrict_css=self.engine.result_selector)

    @property
    def start_urls(self):
        return self.engine.start_urls(search_num=self.width, search_keywords=self.search_keywords)

    @property
    def scrapy_requests(self):
        """all search engine page"""

        def craw_website(response):
            """www.miqilin.com"""

            # todo: match phone num and limit depth
            pass

        def parse_search_result_page(response):
            """www.google.com"""
            print('download finished')
            links = self.link_extractor.extract_links(response)
            for link in links:
                yield scrapy.Request(url=link.url, callback=craw_website)

        scrapy_requests = (scrapy.Request(url=url, callback=parse_search_result_page) for url in self.start_urls)
        return scrapy_requests

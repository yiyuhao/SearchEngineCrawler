from urllib.parse import urlparse

import scrapy
from scrapy.linkextractor import LinkExtractor
from scrapy_redis.spiders import RedisSpider

from controller.take_scheduler import Scheduler
from controller.item_builder import ItemBuilder
from utils import search_contact_us, need_ignoring


class SearchEngineSpider(RedisSpider):
    name = "search_engine_spider"
    redis_key = 'search_engine_spider:start_urls'

    def __init__(self, *args, **kwargs):
        super(SearchEngineSpider, self).__init__(*args, **kwargs)
        self.task_scheduler = Scheduler(self)

    @staticmethod
    def _find_search_engine_result_links(response):
        link_extractor = LinkExtractor(restrict_css=response.meta['engine_selector'])
        links = link_extractor.extract_links(response)
        return links

    @staticmethod
    def _find_all_links(response):
        site_domain = urlparse(response.url).netloc

        link_extractor = LinkExtractor(allow_domains=(site_domain,))
        links = link_extractor.extract_links(response)
        return links

    def next_requests(self):
        """Returns a request to be scheduled or none."""

        request_num = 0
        while request_num < self.redis_batch_size:
            scrapy_requests = self.task_scheduler.fetch_requests()

            if not scrapy_requests:
                break

            for request in scrapy_requests:
                print(f'send a crawl request.. {request.url}')
                yield request
                request_num += 1

        if request_num:
            self.logger.debug("Read %s requests", request_num)

    def parse_search_engine_result_page(self, response):
        """parse search engine result"""

        links = self._find_search_engine_result_links(response)

        for link in links:
            if not need_ignoring(link.url):
                print(f'yield a search engine link: {link.url}')
                yield scrapy.Request(url=link.url, callback=self.craw_website, meta=response.meta)

    def craw_website(self, response):

        item_builder = ItemBuilder(response)

        # filter website by filter_words or inclusion_words
        if item_builder.need_search:

            if response.meta['depth'] <= 1:  # need follow all urls in this page

                contact_page_urls = search_contact_us(response.text)

                # if contact-us page existed, only search contact-us page
                if contact_page_urls:
                    for url in contact_page_urls:
                        print(f'find contact-us page, yield a site link: {url}')
                        yield response.follow(url=url, callback=self.craw_website, meta=response.meta)

                # else find result, then search all pages
                else:

                    for search_result_item in item_builder.build_items():
                        yield search_result_item

                    # follow url
                    links = self._find_all_links(response)

                    for link in links:
                        print(f'yield a site link: {link.url}')
                        yield scrapy.Request(url=link.url, callback=self.craw_website, meta=response.meta)
            else:
                for search_result_item in item_builder.build_items():
                    yield search_result_item

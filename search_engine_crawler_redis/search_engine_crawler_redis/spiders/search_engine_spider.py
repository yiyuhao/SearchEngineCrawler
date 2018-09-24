import logging
from urllib.parse import urlparse

import scrapy
from scrapy.linkextractor import LinkExtractor

from controller.config import request_priority_config
from controller.item_builder import ItemBuilder
from controller.task_scheduler import Scheduler
from scrapy_redis.spiders import RedisSpider
from utils import search_contact_us, need_ignoring

logger = logging.getLogger(__name__)


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
            scrapy_request = self.task_scheduler.fetch_one_request()

            if not scrapy_request:
                break

            logger.info(f'yield a search engine page ({scrapy_request.url})')
            yield scrapy_request
            request_num += 1

        if request_num:
            logger.info("read %s requests", request_num)

    def parse_search_engine_result_page(self, response):
        """parse search engine result, yield website homepage"""

        links = self._find_search_engine_result_links(response)

        for link in links:
            if not need_ignoring(link.url):
                logger.info(f'yield a website homepage request ({link.url}) from ({response.url})')
                yield scrapy.Request(url=link.url,
                                     callback=self.craw_website,
                                     meta=response.meta,
                                     priority=request_priority_config.website_homepage)
            else:
                logger.info(f'skip a url because it contains baidu|wiki|baike|alibaba|amazon: ({link.url})')

    def craw_website(self, response):

        item_builder = ItemBuilder(response)

        # filter website by filter_words or inclusion_words
        if item_builder.need_search:

            if response.meta['depth'] <= 1:  # need follow all urls in this page

                contact_page_urls = search_contact_us(response.text)

                # if contact-us page existed, only search contact-us page
                if contact_page_urls:
                    for url in contact_page_urls:
                        logger.info(f'yield a contact-us page ({url}) from ({response.url})')
                        yield response.follow(url=url,
                                              callback=self.craw_website,
                                              meta=response.meta,
                                              priority=request_priority_config.website_contact)

                # else find result, then search all pages
                else:

                    for search_result_item in item_builder.build_items():
                        yield search_result_item

                    # follow url
                    links = self._find_all_links(response)

                    # filter online retailers website
                    if len(links) < 50:
                        for link in links:
                            logger.info(f'yield a next-level page ({link.url}) from ({response.url})')
                            yield scrapy.Request(url=link.url,
                                                 callback=self.craw_website,
                                                 meta=response.meta,
                                                 priority=request_priority_config.website_next_page_url)
                    else:
                        logger.warning(f'the website will be skip '
                                       f'because of too many({len(links)}) urls found in its homepage: {response.url}')

            else:
                for search_result_item in item_builder.build_items():
                    yield search_result_item

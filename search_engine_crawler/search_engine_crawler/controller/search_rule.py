from urllib.parse import urlparse

import scrapy
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat, format_number, Leniency
from scrapy.linkextractor import LinkExtractor

from .search_engine import SearchEngine
from utils import match_email


class Rule:

    def __init__(self, engine: str, search_keywords: str, width: int = 1):
        self.engine = SearchEngine(engine)
        self.search_keywords = search_keywords
        self.width = width
        self.link_extractor = LinkExtractor(
            # deny_domains=[self.engine.base_url],
            restrict_css=self.engine.result_selector)

    @property
    def start_urls(self):
        return self.engine.start_urls(search_num=self.width, search_keywords=self.search_keywords)

    @property
    def scrapy_requests(self):
        """all search engine page"""

        def craw_website(response):
            """www.miqilin.com"""

            page_text = response.text

            # match phone number
            # todo  clean html   delete element src, href and so on
            for match in PhoneNumberMatcher(page_text, region='US', leniency=Leniency.POSSIBLE):
                phone_number = format_number(match.number, PhoneNumberFormat.INTERNATIONAL)
                print(phone_number)

            # match email
            for email in match_email(page_text):
                print(email)

            # follow url
            site_domain = urlparse(response.url).netloc

            # todo extract url from href
            link_extractor = LinkExtractor(allow_domains=(site_domain,))
            links = link_extractor.extract_links(response)

            for link in links:
                yield scrapy.Request(url=link.url, callback=craw_website)

        def parse_search_result_page(response):
            """www.google.com"""
            print('download finished')

            links = self.link_extractor.extract_links(response)

            for link in links:
                yield scrapy.Request(url=link.url, callback=craw_website)

        scrapy_requests = (scrapy.Request(url=url, callback=parse_search_result_page) for url in self.start_urls)
        return scrapy_requests

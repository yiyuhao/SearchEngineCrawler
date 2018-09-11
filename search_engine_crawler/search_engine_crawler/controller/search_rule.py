from urllib.parse import urlparse

import scrapy
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat, format_number, Leniency
from scrapy.linkextractor import LinkExtractor

from .search_engine import SearchEngine
from utils import search_email, strip_tags, search_contact_us


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

            def find_information():
                # clean html(script, style, html tags)
                page_text = strip_tags(response.text)

                # match phone number
                for match in PhoneNumberMatcher(page_text, region='US', leniency=Leniency.POSSIBLE):
                    phone_number = format_number(match.number, PhoneNumberFormat.INTERNATIONAL)
                    print(f'find phone: {phone_number}')
                    meta['phone_number'].add(phone_number)

                # match email
                for email in search_email(page_text):
                    print(f'find email: {email}')
                    meta['email'].add(email)

            need_follow = response.meta['depth'] <= 1

            # meta save the site information
            meta = dict(
                phone_number=response.meta.get('phone_number', set()),
                email=response.meta.get('email', set())
            )

            if need_follow:

                contact_page_urls = search_contact_us(response.text)

                # first, search contact-us page
                if contact_page_urls:
                    for url in contact_page_urls:
                        print(f'yield a site link: {url}')
                        yield response.follow(url=url, callback=craw_website)

                # else fallow all urls
                else:

                    find_information()

                    # follow url
                    site_domain = urlparse(response.url).netloc

                    link_extractor = LinkExtractor(allow_domains=(site_domain,))
                    links = link_extractor.extract_links(response)

                    # limit depth(each website url is only allowed to follow once)
                    if response.meta['depth'] <= 1:
                        for link in links:
                            print(f'yield a site link: {link.url}')
                            yield scrapy.Request(url=link.url, callback=craw_website, meta=meta)
            else:
                find_information()

        def parse_search_result_page(response):
            """www.google.com"""
            links = self.link_extractor.extract_links(response)

            for link in links:
                print(f'yield a baidu link: {link.url}')
                yield scrapy.Request(url=link.url, callback=craw_website)
                break

        scrapy_requests = (scrapy.Request(url=url, callback=parse_search_result_page) for url in self.start_urls)
        return scrapy_requests

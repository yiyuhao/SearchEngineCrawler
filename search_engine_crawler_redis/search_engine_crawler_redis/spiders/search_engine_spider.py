from urllib.parse import urlparse

import scrapy
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat, format_number, Leniency
from scrapy.linkextractor import LinkExtractor
from scrapy_redis.spiders import RedisSpider

from controller.take_scheduler import Scheduler
from utils import match_email, strip_tags, search_contact_us, need_ignoring


class SearchEngineSpider(RedisSpider):
    name = "search_engine_spider"
    redis_key = 'search_engine_spider:start_urls'

    def __init__(self, *args, **kwargs):
        super(SearchEngineSpider, self).__init__(*args, **kwargs)
        self.task_scheduler = Scheduler(self)

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

    def parse_search_result_page(self, response):
        """parse search engine result"""

        link_extractor = LinkExtractor(restrict_css=response.meta['engine_selector'])
        links = link_extractor.extract_links(response)

        for link in links:
            if not need_ignoring(link.url):
                print(f'yield a search engine link: {link.url}')
                yield scrapy.Request(url=link.url, callback=self.craw_website)

    def craw_website(self, response):

        def find_information():
            # clean html(script, style, html tags)
            page_text = strip_tags(response.text)

            # match phone number
            for match in PhoneNumberMatcher(page_text, region='US', leniency=Leniency.POSSIBLE):
                phone_number = format_number(match.number, PhoneNumberFormat.INTERNATIONAL)
                print(f'find phone: {phone_number} from {response.url}')
                meta['phone_number'].add(phone_number)

            # match email
            for email in match_email(page_text):
                email = email.group()
                print(f'find email: {email} from {response.url}')
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
                    print(f'find contact-us page, yield a site link: {url}')
                    yield response.follow(url=url, callback=self.craw_website)

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
                        yield scrapy.Request(url=link.url, callback=self.craw_website, meta=meta)
        else:
            find_information()

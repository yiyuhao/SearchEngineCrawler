import scrapy

from controller.search_engine import SearchEngine
from controller.config import RequestPriorityConfig


class Rule:

    def __init__(self, spider, country_id, search_request_id,
                 search_keywords, collection_number,
                 filter_words, inclusion_words,
                 email_collection, phone_collection, url_collection,
                 facebook_collection, company_name_collection, company_profile_collection):

        self.spider = spider
        self.engine = SearchEngine(country_id)
        self.search_request_id = search_request_id
        self.search_keywords = search_keywords
        self.collection_number = collection_number
        self.filter_words = filter_words or None
        self.inclusion_words = inclusion_words or None
        self.email_collection = True if email_collection else False
        self.phone_collection = True if phone_collection else False
        self.url_collection = True if url_collection else False
        self.facebook_collection = True if facebook_collection else False
        self.skype_collection = True
        self.company_name_collection = True if company_name_collection else False
        self.company_profile_collection = True if company_profile_collection else False

    @property
    def page_urls(self):
        return self.engine.page_urls(search_num=self.collection_number, search_keywords=self.search_keywords)

    @property
    def scrapy_requests(self):
        """all search engine page"""

        scrapy_requests = (
            scrapy.Request(
                url=url,
                callback=self.spider.parse_search_engine_result_page,
                meta=dict(
                    engine_selector=self.engine.result_selector,
                    search_request_id=self.search_request_id,
                    filter_words=self.filter_words,
                    inclusion_words=self.inclusion_words,
                    email_collection=self.email_collection,
                    phone_collection=self.phone_collection,
                    url_collection=self.url_collection,
                    facebook_collection=self.facebook_collection,
                    skype_collection=self.skype_collection,
                    company_name_collection=self.company_name_collection,
                    company_profile_collection=self.company_profile_collection,
                ),
                priority=RequestPriorityConfig.search_engine_pages,
            )
            for url in self.page_urls
        )

        return scrapy_requests

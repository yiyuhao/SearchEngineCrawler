import scrapy

from .search_engine import SearchEngine


class Rule:

    def __init__(self, spider, engine,
                 search_keywords,
                 collection_number=1,
                 collect_abroad=True, collect_domestic=True,
                 filter_words=None, inclusion_words=None,
                 email_collection=True, phone_collection=True, url_collection=True,
                 facebook_collection=True, company_name_collection=True, company_profile_collection=True):

        self.spider = spider
        self.engine = SearchEngine(engine)
        self.search_keywords = search_keywords
        self.collection_number = collection_number
        self.collect_abroad = collect_abroad
        self.collect_domestic = collect_domestic
        self.filter_words = filter_words
        self.inclusion_words = inclusion_words
        self.email_collection = email_collection
        self.phone_collection = phone_collection
        self.url_collection = url_collection
        self.facebook_collection = facebook_collection
        self.company_name_collection = company_name_collection
        self.company_profile_collection = company_profile_collection

    @property
    def page_urls(self):
        return self.engine.page_urls(search_num=self.collection_number, search_keywords=self.search_keywords)

    @property
    def scrapy_requests(self):
        """all search engine page"""

        scrapy_requests = (
            scrapy.Request(
                url=url,
                callback=self.spider.parse_search_result_page,
                meta=dict(
                    engine_selector=self.engine.result_selector,
                    collect_abroad=self.collect_abroad,
                    collect_domestic=self.collect_domestic,
                    filter_words=self.filter_words,
                    inclusion_words=self.inclusion_words,
                    email_collection=self.email_collection,
                    phone_collection=self.phone_collection,
                    url_collection=self.url_collection,
                    facebook_collection=self.facebook_collection,
                    company_name_collection=self.company_name_collection,
                    company_profile_collection=self.company_profile_collection,
                ))
            for url in self.page_urls
        )

        return scrapy_requests

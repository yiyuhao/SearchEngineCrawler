import random

from controller.db_manager import SearchRequestDBManager
from controller.search_rule import Rule


class Scheduler:

    def __init__(self, spider):
        self.spider = spider
        self.scrapy_requests = []

    def fetch_one_request(self):
        if not self.scrapy_requests:

            db_manager = SearchRequestDBManager()
            db_query_result = db_manager.fetch_all()

            for search_request in db_query_result:
                rule = Rule(self.spider, *search_request)
                for req in rule.scrapy_requests:
                    self.scrapy_requests.append(req)

            random.shuffle(self.scrapy_requests)

        return self.scrapy_requests.pop()

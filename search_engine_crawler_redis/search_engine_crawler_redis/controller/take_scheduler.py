from .search_rule import Rule
from controller.db_manager import SearchRequestDBManager


class Scheduler:

    def __init__(self, spider):
        self.spider = spider
        self.db_manager = SearchRequestDBManager()

    def fetch_requests(self):
        scrapy_requests = []
        db_query_result = self.db_manager.fetch_all()
        for search_request in db_query_result:
            rule = Rule(self.spider, *search_request)
            scrapy_requests.extend(rule.scrapy_requests)

        return scrapy_requests

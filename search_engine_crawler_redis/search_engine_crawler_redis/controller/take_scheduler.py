from .search_rule import Rule
from controller.db_manager import SearchRequestDBManager


class Scheduler:

    def __init__(self, spider):
        self.spider = spider
        self.db_manager = SearchRequestDBManager()

    def _fetch_rules(self):
        rules = []
        db_query_result = self.db_manager.fetch_all()
        for search_request in db_query_result:
            rules.append(Rule(self.spider, *search_request))

        # todo build requests

    def fetch_requests(self):
        # 轴承：Bearing
        # 办公家具：office furniture
        # Led
        # 机械配件：Machinery Parts
        # 手机配件：Mobile phone accessories
        rule = Rule(self.spider, 1,
                    search_request_id=10, search_keywords='Mobile phone accessories', collection_number=1)

        scrapy_requests = [] if self.database_is_empty else rule.scrapy_requests
        self.database_is_empty = True
        return scrapy_requests

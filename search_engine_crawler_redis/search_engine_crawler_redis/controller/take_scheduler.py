from .search_rule import Rule


class Scheduler:

    def __init__(self, spider):
        self.spider = spider

    database_is_empty = False

    def fetch_requests(self):
        rule = Rule(self.spider, 'google', '汇泽丰(北京)餐饮管理有限公司')

        scrapy_requests = [] if self.database_is_empty else rule.scrapy_requests
        self.database_is_empty = True
        return scrapy_requests

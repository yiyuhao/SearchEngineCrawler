from .search_rule import Rule


class Scheduler:

    def __init__(self, spider):
        self.spider = spider

    database_is_empty = False

    def fetch_requests(self):
        # 轴承：Bearing
        # 办公家具：office furniture
        # Led
        # 机械配件：Machinery Parts
        # 手机配件：Mobile phone accessories
        rule = Rule(self.spider, 'bing',
                    search_request_id=10, search_keywords='轴承', collection_number=1)

        scrapy_requests = [] if self.database_is_empty else rule.scrapy_requests
        self.database_is_empty = True
        return scrapy_requests

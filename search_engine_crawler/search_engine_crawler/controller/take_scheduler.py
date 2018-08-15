from .search_rule import Rule


class Scheduler:
    database_is_empty = False

    def fetch_request(self):
        rule = Rule('baidu', '米其林轮胎')

        scrapy_requests = [] if self.database_is_empty else rule.scrapy_requests
        self.database_is_empty = not self.database_is_empty
        return scrapy_requests

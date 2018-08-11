from .scrapy_request_builder import ScrapyRequest


class Scheduler:
    database_is_empty = False

    def fetch_request(self):
        url = 'http://www.baidu.com/'
        keywords = '猫'

        if self.database_is_empty:
            self.database_is_empty = not self.database_is_empty
            return None

        scrapy_request = ScrapyRequest(url, keywords)

        self.database_is_empty = not self.database_is_empty

        return scrapy_request

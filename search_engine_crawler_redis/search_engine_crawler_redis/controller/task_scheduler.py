import time

from controller.db_manager import SearchRequestDBManager
from controller.search_rule import Rule


class Scheduler:

    def __init__(self, spider):
        self.spider = spider
        self.scrapy_requests = {}
        self.cur_request_id = None
        self.request_updated_time = time.time()

    @property
    def scrapy_requests_length(self):
        return len(self.scrapy_requests)

    @property
    def next_request_id(self):
        if not self.scrapy_requests:
            return None

        if self.cur_request_id is None:
            result = next(iter(self.scrapy_requests.keys()))  # first elem of self.requests
        else:
            found = False
            for id_ in self.scrapy_requests.keys():
                if found is True:
                    result = id_
                    break
                if self.cur_request_id == id_:
                    found = True
            else:
                result = next(iter(self.scrapy_requests.keys()))

        self.cur_request_id = result

        return result

    def _append_request(self, request):
        id_ = request.meta['search_request_id']
        request_list = self.scrapy_requests.get(id_)
        if not request_list:
            self.scrapy_requests[id_] = []

        self.scrapy_requests[id_].append(request)

    def _fetch_one(self):
        if not self.scrapy_requests:
            return None

        next_id = self.next_request_id

        request = self.scrapy_requests[next_id].pop()

        if not self.scrapy_requests[next_id]:
            del self.scrapy_requests[next_id]

        return request

    def update_request(self):

        if time.time() - self.request_updated_time < 1:
            return

        db_manager = SearchRequestDBManager()
        db_query_result = db_manager.fetch_all()

        if db_query_result:
            for search_request in db_query_result:
                rule = Rule(self.spider, *search_request)
                for req in rule.scrapy_requests:
                    self._append_request(req)

        self.request_updated_time = time.time()

    def fetch_one_request(self):
        self.update_request()
        return self._fetch_one()

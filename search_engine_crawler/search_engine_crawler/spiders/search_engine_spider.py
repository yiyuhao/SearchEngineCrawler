import scrapy
from time import sleep

from controller.take_scheduler import Scheduler

scheduler = Scheduler()


class SearchEngineSpider(scrapy.Spider):
    name = "start_spider"

    def start_requests(self):

        while True:
            scrapy_requests = scheduler.fetch_request()
            for request in scrapy_requests:
                print(f'send a crawl request.. {request.url}')
                yield request

    def parse(self, response):
        pass

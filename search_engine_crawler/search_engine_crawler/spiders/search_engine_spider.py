import scrapy
from time import sleep

from controller.take_scheduler import Scheduler

scheduler = Scheduler()


class SearchEngineSpider(scrapy.Spider):
    name = "start_spider"

    def start_requests(self):

        while True:
            scrapy_request = scheduler.fetch_request()
            if scrapy_request is None:
                print('database is empty, now wait..')
                sleep(1)
            else:
                print('send a crawl request..')
                yield scrapy_request

    def parse(self, response):
        a = 1
        pass

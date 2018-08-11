import scrapy

from .parser import Parser


class ScrapyRequest:

    def __new__(cls, url, keywords, *args, **kwargs):
        parser = Parser(keywords)
        return scrapy.Request(url=url, callback=parser)

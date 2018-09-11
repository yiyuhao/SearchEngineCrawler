from urllib.parse import urlparse
from math import ceil

from utils import get_search_engine_config
#
# class Item:
#     def __new__(
#             cls,
#             search_url: str,
#             result_selector: str = 'h3 > a',
#             page_size: int = 10,
#             page_param: str = '{}*10'
#     ):
#         return dict(
#             search_url=search_url,
#             result_selector=result_selector,
#             page_size=page_size,
#             page_param=page_param,
#         )
#
#     def __getattr__(self, item):
#         return self.__getitem__(item)
#
#
# class SearchEngineConfig:
#     config_dict = {
#         0: Item(
#             search_url='https://www.google.com/search?q={keywords}&start={page_param}',
#         ),
#
#         1: Item(
#             search_url='http://www.bing.com/search?q={keywords}&first={page_param}',
#             result_selector='h2 > a',
#         ),
#
#         2: Item(
#             search_url='http://www.baidu.com/s?wd={keywords}&pn={page_param}',
#         ),
#
#         3: Item(
#             search_url='https://search.yahoo.com/search;?p={keywords}&b={page_param}',
#             page_param='{}*10 + 1'
#         )
#     }

search_engine_config = get_search_engine_config()


class SearchEngine:

    def __init__(self, country_id):
        if country_id not in search_engine_config:
            raise ValueError(f'no search engine found by country_id: {country_id}')

        engine = search_engine_config[country_id]

        self.search_url = engine['search_url']
        self.result_selector = engine['result_selector']
        self.page_size = engine['page_size']
        self.page_param = engine['page_param']

        self.base_url = urlparse(self.search_url).netloc

    def __str__(self):
        return self.base_url

    def page_urls(self, search_num: int, search_keywords: str):
        """
        :param search_num: depth
        :param search_keywords: keywords
        :return: (Iter) urls for crawling
        """
        max_page = int(ceil(search_num / 10))
        page_params = (eval(self.page_param.format(page)) for page in range(max_page))

        return (
            self.search_url.format(
                keywords=search_keywords,
                page_param=page_param
            )
            for page_param in page_params
        )

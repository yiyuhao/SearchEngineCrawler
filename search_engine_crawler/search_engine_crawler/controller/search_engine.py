from math import ceil


class Item:
    def __new__(
            cls,
            search_url: str,
            result_selector: str = 'h3 > a',
            page_size: int = 10,
            page_param: str = '{}*10'
    ):
        return dict(
            search_url=search_url,
            result_selector=result_selector,
            page_size=page_size,
            page_param=page_param,
        )

    def __getattr__(self, item):
        return self.__getitem__(item)


class SearchEngineConfig:
    google = Item(
        search_url='https://www.google.com/search?q={keywords}&start={page_param}',
    )

    bing = Item(
        search_url='http://www.bing.com/search?q={keywords}&first={page_param}',
        result_selector='h2 > a',
    )

    baidu = Item(
        search_url='http://www.baidu.com/s?wd={keywords}&pn={page_param}',
    )

    yahoo = Item(
        search_url='https://search.yahoo.com/search;?p={keywords}&b={page_param}',
        page_param='{}*10 + 1'
    )


class SearchEngine:

    def __init__(self, name: str):
        if not hasattr(SearchEngineConfig, name):
            raise ValueError(f'no search engine named {name}')

        self.name = name
        self.item = getattr(SearchEngineConfig, name)

        for key, value in self.item.items():
            setattr(self, key, value)

    def start_urls(self, search_num: int, search_keywords: str):
        """
        :param search_num: depth
        :param search_keywords: keywords
        :return: (Iter) urls for crawling
        """
        max_page = int(ceil(search_num / 10))
        page_params = (eval(self.page_param.format(page)) for page in range(1, max_page + 1))

        return (
            self.search_url.format(
                keywords=search_keywords,
                page_param=page_param
            )
            for page_param in page_params
        )

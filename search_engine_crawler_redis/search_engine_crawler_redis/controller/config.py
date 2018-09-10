#
#      File: config.py
#   Project: payunion
#    Author: Yi Yuhao
#
#   Copyright (c) 2018 麦禾互动. All rights reserved.


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



class Parser:

    def __new__(cls, keywords, *args, **kwargs):
        def parse_fun(response):
            page = response.url.split("/")[-2]
            print(f'crawled data: {keywords}')
            print(page)
        return parse_fun

import os
import sys

from scrapy.cmdline import execute

search_engine_crawler_redis_dir = os.path.dirname(os.path.abspath(__file__))
scrapy_redis_dir = os.path.dirname(search_engine_crawler_redis_dir)

sys.path.append(search_engine_crawler_redis_dir)
sys.path.append(scrapy_redis_dir)

if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'search_engine_spider'])

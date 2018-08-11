import os
import sys

from scrapy.cmdline import execute

scrapy_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(scrapy_dir)


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'start_spider'])

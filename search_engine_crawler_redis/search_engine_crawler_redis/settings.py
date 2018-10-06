# -*- coding: utf-8 -*-

# Scrapy settings for search_engine_crawler_redis project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'search_engine_crawler_redis'

SPIDER_MODULES = ['search_engine_crawler_redis.spiders']
NEWSPIDER_MODULE = 'search_engine_crawler_redis.spiders'

# Enables scheduling storing requests queue in redis.
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
             "AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/61.0.3163.100 Safari/537.36"

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# Specify the host and port to use when connecting to Redis (optional).
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

REDIS_ENCODING = 'utf-8'

# mysql
MYSQL_HOST = 'localhost'
MYSQL_DATABASE = 'ses'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'search_engine_crawler_redis.pipelines.DuplicatesPipeline': 100,
    'search_engine_crawler_redis.pipelines.MysqlTwistedPipeline': 200,
    'search_engine_crawler_redis.pipelines.SearchEngineCrawlerRedisPipeline': 300,
}

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# TTL of request fingerprint (url dupefilter) in redis sorted set.
# url fingerprint 去重TTL
FINGERPRINT_TTL = 30 * 60
# item 去重TTL
SEARCH_RESULT_ITEM_TTL = 30 * 60
# 已停止search_request_id去重TTL
STOPPED_SEARCH_REQUEST_TTL = 60 * 60

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs

DOWNLOAD_DELAY = 0.1

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'search_engine_crawler_redis.middlewares.SearchEngineCrawlerRedisSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'search_engine_crawler_redis.middlewares.SearchEngineCrawlerRedisDownloaderMiddleware': 100,
    # 'search_engine_crawler_redis.middlewares.RandomUserAgentDownloadMiddleware': 200,
    # 'search_engine_crawler_redis.middlewares.RandomProxyIpDownloadMiddleware': 300,
}

DOWNLOAD_TIMEOUT = 60

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# fake-useragent config
RANDOM_USER_AGENT_TYPE = 'chrome'

email_regex = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'

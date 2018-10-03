import json
import re
import time
from html.parser import HTMLParser
from time import sleep

import requests
import logging
from lxml.html.clean import Cleaner
from scrapy.crawler import Settings

from controller.db_manager import NationalConfigurationDBManager, SearchRequestDBManager
from scrapy_redis.connection import get_redis_from_settings
from settings import email_regex, SEARCH_RESULT_ITEM_TTL, STOPPED_SEARCH_REQUEST_TTL

cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True

pattern_a_tag = re.compile(r'(<a.*?</a>)', re.IGNORECASE)
pattern_contact_up = re.compile(r'contact|联系|about|关于', re.IGNORECASE)
pattern_facebook = re.compile(r'href=.*facebook\.com', re.IGNORECASE)
pattern_skype = re.compile(r'href=.*(skype|callto):', re.IGNORECASE)
pattern_href = re.compile(r'<a.*?href=[\'"](.*?)[\'"].*</a>', re.IGNORECASE)
pattern_title = re.compile(r'<title>(.*?)</title>', re.IGNORECASE)
pattern_description = re.compile(r'<meta.*?name=[\'"]description[\'"].*?content=[\'"](.*?)[\'"].*?>', re.IGNORECASE)

# the result of search engine that needed filter
pattern_ignore = re.compile(r'wiki|baike|alibaba|amazon')

logger = logging.getLogger(__name__)


class HTMLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d.strip())

    def get_data(self):
        return '*'.join(self.fed)


class SearchResultDupefilter:

    def __init__(self):
        self.server = get_redis_from_settings(Settings())
        self.key = f'search_result_item_dupefilter'

    def seen(self, item):
        """check if item already existed"""

        now = time.time()
        expired_time = now + SEARCH_RESULT_ITEM_TTL

        # clear expired item
        self.server.zremrangebyscore(self.key, 0, now)

        item = dict(item)
        del item['website_title']

        added = self.server.zadd(self.key, expired_time, json.dumps(item))

        return added == 0


class DefaultProxyIpApi:

    def __init__(self):
        self.url = 'http://api.66daili.cn/API/GetSecretProxy/?orderid=2761436131801403645' \
                   '&num=20' \
                   '&token=66daili' \
                   '&format=json' \
                   '&line_separator=win' \
                   '&protocol=http' \
                   '&region=overseas'

    def pull_ips(self):
        try:
            result = requests.get(self.url)
            ips = [f'http://{ip}' for ip in json.loads(result.text)['proxies']]
            logger.debug(f'pull proxy ips: {ips}')
            assert ips
            return ips
        except Exception as e:
            logger.critical(f'can not get proxy ip: {e}')
            return []


class ProxyIpPool:

    def __init__(self):

        self.proxy_ip_api = DefaultProxyIpApi()

        # ip列表
        self.ips = []
        self.cur_index = 0
        self.fetch_datetime = time.time() - 1000  # need to pull ips

    @staticmethod
    def is_effective(ip):
        """检查ip是否可用"""
        try:
            res = requests.get('https://www.bing.com/', proxies={'http': ip})
        except:
            logger.debug(f'invalid proxy ip {ip}')
            return False
        else:
            code = res.status_code
            is_effective = True if 200 <= code < 300 else False

            if not is_effective:
                logger.debug(f'invalid proxy ip {ip}')

            return is_effective

    def update_ips(self):
        self.ips = self.proxy_ip_api.pull_ips()
        self.fetch_datetime = time.time()
        self.cur_index = 0

    @property
    def next_ip(self):
        if time.time() - self.fetch_datetime > 120:
            self.update_ips()

        if not self.ips:
            return None

        next_index = 0
        if self.cur_index + 1 < len(self.ips):
            next_index = self.cur_index + 1

        next_ip = self.ips[next_index]

        if self.is_effective(next_ip):
            self.cur_index = next_index
            return next_ip

        del self.ips[next_index]
        return self.next_ip


def strip_tags(html_text):
    # remove javascript code
    cleaned_text = cleaner.clean_html(html_text)
    s = HTMLStripper()
    s.feed(cleaned_text)
    return s.get_data()


def search_title(text):
    match = pattern_title.search(text)
    title = match.group(1) if match else 'No title'
    return title


def search_description(text):
    match = pattern_description.search(text)
    description = match.group(1) if match else 'No title'
    return description


def search_email(text):
    pattern = re.compile(email_regex)
    return pattern.finditer(text)


def search_contact_us(text) -> set:
    """return all urls that match the condition: html <a> tag contains word 'contact"""

    text = re.sub('\s', '', text)

    # find all <a></a>
    a_tags = pattern_a_tag.findall(text)

    contact_a_tags = set()

    for a_tag in a_tags:
        if pattern_contact_up.search(a_tag):
            match_href = pattern_href.match(a_tag)
            if match_href:
                contact_a_tags.add(match_href.group(1))

    return contact_a_tags


def search_facebook(text) -> set:
    text = re.sub('\s', '', text)

    # find all <a></a>
    a_tags = pattern_a_tag.findall(text)

    facebook_a_tags = set()

    for a_tag in a_tags:
        if pattern_facebook.search(a_tag):
            match_href = pattern_href.match(a_tag)
            if match_href:
                facebook_a_tags.add(match_href.group(1))

    return facebook_a_tags


def search_skype(text) -> set:
    text = re.sub('\s', '', text)

    # find all <a></a>
    a_tags = pattern_a_tag.findall(text)

    skype_a_tags = set()

    for a_tag in a_tags:
        if pattern_skype.search(a_tag):
            match_href = pattern_href.match(a_tag)
            if match_href:
                skype_a_tags.add(match_href.group(1))

    return skype_a_tags


def need_ignoring(url):
    """filter search engine result url, exclude baike, wiki and so on"""
    return True if pattern_ignore.search(url) else False


def get_search_engine_config():
    db = NationalConfigurationDBManager()
    query_result = db.fetch()

    config = {}

    for engine in query_result:
        country_id, search_engine_address, page_size, page_param, result_selector = engine
        config[country_id] = dict(
            search_url=search_engine_address,
            page_size=page_size,
            page_param=page_param,
            result_selector=result_selector,
        )

    return config


def has_stopped(request):
    search_request_id = json.dumps(request.meta['search_request_id'])

    # check redis if request has been stopped
    server = get_redis_from_settings(Settings())
    key = f'search_request_stopped_id_zset'
    now = time.time()
    expired_time = now + STOPPED_SEARCH_REQUEST_TTL
    server.zremrangebyscore(key, 0, now)  # clear expired request and add
    added = server.zadd(key, expired_time, search_request_id)

    if not added:  # already cached in redis
        return True

    # else search db, if not stopped then del id in zset
    db = SearchRequestDBManager()
    if not db.has_stopped(request.meta['search_request_id']):
        server.zrem(key, search_request_id)
        return False
    else:
        return True

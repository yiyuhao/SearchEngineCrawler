import json
import re
import time
from html.parser import HTMLParser

from lxml.html.clean import Cleaner
from scrapy_redis.connection import get_redis_from_settings
from scrapy.crawler import Settings

from controller.db_manager import NationalConfigurationDBManager
from settings import email_regex, SEARCH_RESULT_ITEM_TTL

cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True

pattern_a_tag = re.compile(r'(<a.*?</a>)', re.IGNORECASE)
pattern_contact_up = re.compile(r'contact|联系', re.IGNORECASE)
pattern_href = re.compile(r'<a.*?href=[\'"](.*?)[\'"].*</a>', re.IGNORECASE)

# the result of search engine that needed filter
pattern_ignore = re.compile(r'baidu|wiki|baike')


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


def strip_tags(html_text):
    # remove javascript code
    cleaned_text = cleaner.clean_html(html_text)
    s = HTMLStripper()
    s.feed(cleaned_text)
    return s.get_data()


def match_email(text):
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

        added = self.server.zadd(self.key, expired_time, json.dumps(dict(item)))

        return added == 0

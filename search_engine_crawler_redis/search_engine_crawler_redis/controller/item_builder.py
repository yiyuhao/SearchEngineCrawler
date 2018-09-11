#
#      File: item_builder.py
#   Project: payunion
#    Author: Yi Yuhao
#
#   Copyright (c) 2018 麦禾互动. All rights reserved.

import re
from urllib.parse import urlparse

from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat, format_number, Leniency
from scrapy.contrib.loader import ItemLoader

from items import SearchResultItem
from utils import search_email, search_title, search_facebook, strip_tags


class ItemBuilder:
    def __init__(self, response):
        """
        :param response: spider.response
        :return (iter) items:  items filter by search_request condition in response.data
        """
        self.items_set = set()

        self.response = response
        self.page_text = strip_tags(self.response.text)  # clean html(script, style, html tags)

        self.search_request_id = self.response.meta['search_request_id']
        self.filter_words = self.response.meta['filter_words']
        self.inclusion_words = self.response.meta['inclusion_words']
        self.email_collection = self.response.meta['email_collection']
        self.phone_collection = self.response.meta['phone_collection']
        self.url_collection = self.response.meta['url_collection']
        self.facebook_collection = self.response.meta['facebook_collection']
        self.company_name_collection = self.response.meta['company_name_collection']
        self.company_profile_collection = self.response.meta['company_profile_collection']

        self.domain_url = urlparse(response.url).netloc
        self.title = search_title(self.response.text)

    def build_items(self):
        """@property will cause unexpected error"""

        self.build_email_items()
        self.build_phone_items()
        self.build_company_name_items()
        self.build_company_profile_items()
        self.build_facebook_items()
        self.build_skype_items()
        return self.items_set

    def response_contain_words(self, words):
        pattern = re.compile(words)
        return pattern.findall(self.page_text)

    @property
    def need_search(self):

        if self.filter_words:
            # 含有过滤词
            if self.response_contain_words(self.filter_words):
                return False
        if self.inclusion_words:
            # 含有包含词
            if not self.response_contain_words(self.inclusion_words):
                return False

        return True

    def produce_item(self, field_name, value):

        item_loader = ItemLoader(item=SearchResultItem(), response=self.response)
        item_loader.add_value('search_request_id', self.search_request_id)
        item_loader.add_value('domain_name', self.domain_url)
        item_loader.add_value('website_title', self.title)
        item_loader.add_value(field_name, value)
        item = item_loader.load_item()

        print(f'build item: {item}')
        self.items_set.add(item)

    def build_email_items(self):

        if not self.email_collection:
            return

        for email in search_email(self.page_text):
            email = email.group()
            self.produce_item('mailbox', email)

    def build_phone_items(self):
        if not self.phone_collection:
            return
        for match in PhoneNumberMatcher(self.page_text, region='US', leniency=Leniency.POSSIBLE):
            phone_number = format_number(match.number, PhoneNumberFormat.INTERNATIONAL)
            self.produce_item('phone', phone_number)

    def build_company_name_items(self):
        if not self.company_name_collection:
            return

    def build_company_profile_items(self):
        if not self.company_profile_collection:
            return

    def build_facebook_items(self):
        if not self.facebook_collection:
            return

        for facebook_url in search_facebook(self.response.text):
            self.produce_item('facebook', facebook_url)

    def build_skype_items(self):
        return

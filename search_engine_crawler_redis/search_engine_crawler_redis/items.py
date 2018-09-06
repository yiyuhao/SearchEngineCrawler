# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SearchEngineCrawlerRedisItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class SearchResultItem(scrapy.Item):
    search_request_id = scrapy.Field()
    domain_name = scrapy.Field()
    mailbox = scrapy.Field()
    phone = scrapy.Field()
    website_title = scrapy.Field()
    website_ntroduction = scrapy.Field()
    facebook = scrapy.Field()
    skype = scrapy.Field()

    @property
    def sql(self):
        insert_sql = '''
            insert into search_details(search_request_id, domain_name, mailbox, 
            phone, website_title, website_ntroduction, 
            facebook, skype) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        params = (
            self['search_request_id'], self.get('domain_name', None), self.get('mailbox', None),
            self.get('phone', None), self.get('website_title', None), self.get('website_ntroduction', None),
            self.get('facebook', None), self.get('skype', None)
        )

        return insert_sql, params

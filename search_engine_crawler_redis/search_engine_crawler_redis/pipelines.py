# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import MySQLdb.cursors
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi


class SearchEngineCrawlerRedisPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlTwistedPipeline(object):
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_settings(cls, settings):
        params = dict(
            host=settings['MYSQL_HOST'],
            database=settings['MYSQL_DATABASE'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )

        db_pool = adbapi.ConnectionPool('MySQLdb', **params)

        return cls(db_pool)

    @staticmethod
    def _do_insert(cursor, item):
        """
            根据不同item构建不同sql，执行具体的插入
        """

        insert_sql, sql_params = item.sql
        cursor.execute(insert_sql, sql_params)

    def process_item(self, item, spider):
        """async SQL insert with Twisted"""
        query = self.db_pool.runInteraction(self._do_insert, item)
        query.addErrback(self.handle_error, item, spider)
        return item

    def handle_error(self, failure, item, spider):
        """处理异步插入的异常"""
        print(failure)


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['id'])
            return item

# todo redis pipeline
# search_request_collection_number: {request_id: number}

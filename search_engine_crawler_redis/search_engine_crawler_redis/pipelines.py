# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import MySQLdb.cursors
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
from twisted.python import log

from utils import SearchResultDupefilter


class SearchEngineCrawlerRedisPipeline(object):
    def process_item(self, item, spider):
        return item


class ReconnectingPool(adbapi.ConnectionPool):
    def _runInteraction(self, interaction, *args, **kw):
        try:
            return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)
        except MySQLdb.OperationalError as e:
            if e[0] not in (2006, 2013):
                raise
            log.err("Lost connection to MySQL, retrying operation.  If no errors follow, retry was successful.")
            conn = self.connections.get(self.threadID())
            self.disconnect(conn)
            return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)


class DuplicatesPipeline(object):

    def __init__(self):
        self.dupefilter = SearchResultDupefilter()

    def process_item(self, item, spider):
        if self.dupefilter.seen(item):
            raise DropItem("Duplicate item found: %s" % item)
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
            cp_reconnect=True,
        )

        db_pool = ReconnectingPool('MySQLdb', **params)

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

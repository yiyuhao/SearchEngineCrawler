from time import time

import MySQLdb
import MySQLdb.cursors
from DBUtils.PooledDB import PooledDB
from twisted.enterprise import adbapi
from twisted.python import log

from settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, CLUSTER_NUM, SELF_NO
from settings import PING_DB_SERVER_INTERVAL


class DBPool:
    def __init__(self):
        self.pool = PooledDB(MySQLdb, 5, host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD,
                             database=MYSQL_DATABASE, port=3306)

    def connection(self):
        return self.pool.connection()


db_pool = DBPool()


class ReconnectingPool(adbapi.ConnectionPool):
    def __init__(self, *args, **kwargs):
        super(ReconnectingPool, self).__init__(*args, **kwargs)
        self.last_ping = time()

    @staticmethod
    def _do_select_ping(cursor):

        cursor.execute('SELECT 1;')

    def _runInteraction(self, interaction, *args, **kw):
        try:
            return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)
        except MySQLdb.OperationalError as e:
            log.err("Lost connection to MySQL, retrying operation.  If no errors follow, retry was successful. ")
            log.err(e)
            conn = self.connections.get(self.threadID())
            self.disconnect(conn)
            return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)

    def keep_connection_please(self):
        now = time()
        if now - self.last_ping > PING_DB_SERVER_INTERVAL:
            self.runInteraction(self._do_select_ping)
            self.last_ping = time()


params = dict(
    host=MYSQL_HOST,
    database=MYSQL_DATABASE,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    charset='utf8',
    cursorclass=MySQLdb.cursors.DictCursor,
    use_unicode=True,
    cp_reconnect=True,
)

async_db_pool = ReconnectingPool('MySQLdb', **params)


class DBConnection:

    @classmethod
    def get_connection(cls):
        return db_pool.connection()

    def __new__(cls):
        cls.instance = cls.get_connection()
        return cls.instance


class NationalConfigurationDBManager:
    query_sql = '''
        SELECT id, search_engine_address, page_size, page_param, result_selector
        FROM national_configuration;
    '''

    def __init__(self):
        self.conn = DBConnection()
        # print('\n\n\n###########################n select from national_configuration')
        # self.conn.cursor().execute('SELECT id FROM national_configuration;')

    def fetch(self):
        with self.conn.cursor() as cursor:
            cursor.execute(self.query_sql)
            result = cursor.fetchall()
        self.conn.close()
        return result


class SearchRequestDBManager:
    query_sql = f'''
        SELECT b.national_configuration_id AS country_id, a.id, a.key_word, a.collection_number,
            a.filter_words,a.inclusion_words, a.email_collection,a.phone_collection, a.url_collection,
            a.facebook_collection, a.company_name_collection, a.company_profile_collection
        FROM search_request a INNER JOIN search_country_relationship b
        ON a.id = b.search_request_id AND a.del_flag = 0
        where mod(a.id, {CLUSTER_NUM})={SELF_NO}
        ORDER BY 'create_date';
    '''

    def __init__(self):
        self.conn = DBConnection()

    @staticmethod
    def get_mark_fetched_request_sql(query_result):
        ids = list(set([item[1] for item in query_result]))
        format_strings = ','.join(['%s'] * len(ids))
        sql = f'''
            UPDATE search_request
            SET del_flag = 1
            WHERE id IN ({format_strings});
        '''
        return sql, ids

    def fetch_all(self):
        with self.conn.cursor() as cursor:
            cursor.execute(self.query_sql)
            result = cursor.fetchall()

            # mark data fetched
            if result:
                mark_fetched_sql, ids = self.get_mark_fetched_request_sql(result)
                cursor.execute(mark_fetched_sql, ids)
        self.conn.close()

        return result

    def has_stopped(self, search_request_id):
        sql = '''
            SELECT 1
            FROM search_request
            WHERE id='%s' AND DATE_ADD(update_date,INTERVAL 10 SECOND) < NOW();
        '''

        with self.conn.cursor() as cursor:
            has_stopped = cursor.execute(sql, [search_request_id])
        self.conn.close()

        return True if has_stopped else False

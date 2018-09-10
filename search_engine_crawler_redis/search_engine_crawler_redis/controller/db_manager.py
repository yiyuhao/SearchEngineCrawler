#
#      File: db_manager.py
#   Project: payunion
#    Author: Yi Yuhao
#
#   Copyright (c) 2018 麦禾互动. All rights reserved.


import MySQLdb

from settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

conn = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, charset='utf8')


class NationalConfigurationDBManager:
    query_sql = '''
        SELECT id, search_engine_address, page_size, page_param, result_selector
        FROM national_configuration;
    '''

    def __init__(self):
        self.conn = conn

    def fetch(self):
        with conn.cursor() as cursor:
            cursor.execute(self.query_sql)
            result = cursor.fetchall()
            return result


class SearchRequestDBManager:
    query_sql = '''
        SELECT b.id AS country_id, a.id, a.key_word, a.collection_number,
            a.filter_words,a.inclusion_words, a.email_collection,a.phone_collection, a.url_collection,
            a.facebook_collection, a.company_name_collection, a.company_profile_collection
        FROM search_request a INNER JOIN search_country_relationship b
        ON a.id = b.search_request_id AND a.del_flag = 0
        ORDER BY 'create_date';
    '''

    def __init__(self):
        self.conn = conn

    @staticmethod
    def get_mark_fetched_request_sql(query_result):
        ids = list(set([id_ for id_ in query_result[1]]))
        format_strings = ','.join(['%s'] * len(ids))
        sql = f'''
            UPDATE search_request
            SET del_flag = 1
            WHERE key_word IN ({format_strings});
        '''
        return sql, ids

    def fetch_all(self):
        with conn.cursor() as cursor:
            cursor.execute(self.query_sql)
            result = cursor.fetchall()

            # mark data fetched
            mark_fetched_sql, ids = self.get_mark_fetched_request_sql(result)
            # todo
            # cursor.execute(mark_fetched_sql, ids)
            # cursor.commit()

            return result


if __name__ == '__main__':
    manager = NationalConfigurationDBManager()
    print(manager.fetch())

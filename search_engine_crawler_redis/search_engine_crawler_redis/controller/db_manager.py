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


if __name__ == '__main__':
    manager = NationalConfigurationDBManager()
    print(manager.fetch())

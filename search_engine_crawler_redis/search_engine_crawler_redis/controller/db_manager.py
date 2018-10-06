import MySQLdb

from settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


class DBConnection:

    @classmethod
    def get_connection(cls):
        return MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, charset='utf8')

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

    def fetch(self):
        with self.conn.cursor() as cursor:
            cursor.execute(self.query_sql)
            result = cursor.fetchall()
            return result


class SearchRequestDBManager:
    query_sql = '''
        SELECT b.national_configuration_id AS country_id, a.id, a.key_word, a.collection_number,
            a.filter_words,a.inclusion_words, a.email_collection,a.phone_collection, a.url_collection,
            a.facebook_collection, a.company_name_collection, a.company_profile_collection
        FROM search_request a INNER JOIN search_country_relationship b
        ON a.id = b.search_request_id AND a.del_flag = 0
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

            return result

    def has_stopped(self, search_request_id):
        sql = '''
            SELECT 1
            FROM search_request
            WHERE id='%s' AND DATE_ADD(update_date,INTERVAL 10 SECOND) < NOW();
        '''

        with self.conn.cursor() as cursor:
            has_stopped = cursor.execute(sql, [search_request_id])
            return True if has_stopped else False

import os
import sqlite3
from sqlite3.dbapi2 import Error

import pandas as pd
from finsent.constants import DATA_DIR, STOCKS_DIR
import logging

class BaseDB:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self._init_connection()

    def __del__(self):
        self.connection.close()
    
    def _init_connection(self, dbname="stonks.db"):
        try:
            self.connection = sqlite3.connect(os.path.join(self.data_dir, dbname))
        except Error as e:
            logging.error("Exception in DB connect")
            logging.error(e)
    
    def _get_entries(self, params_dict, table_name):
        cursor = self.connection.cursor()
        res = None
        try:
            query = """SELECT * FROM {table_name}""".format(table_name=table_name)
            if params_dict:
                query += " WHERE "
                query += " AND ".join(["{key}=:{key}".format(key=key) for key in params_dict])
                cursor.execute(query, params_dict)
            else:
                cursor.execute(query,)
            res = cursor.fetchall()
        except Error as e:
            logging.error("Exception in _check_entry")
            logging.error(e)
        finally:
            cursor.close()

        return res
    
    def _check_entry(self, params_dict, table_name):
        entries = self._get_entries(params_dict, table_name)

        if entries and len(entries)>=1:
            return True

        return False
    
    def _insert_row(self, insertion_dict, table_name):
        assert isinstance(insertion_dict, dict), "Error: need dict"

        cursor = self.connection.cursor()
        try:
            query = """INSERT INTO {table_name}({params}) VALUES (""".format(
                table_name = table_name,
                params = ", ".join(list(insertion_dict.keys())))
            
            query += ", ".join([":{key}".format(key=i) for i in insertion_dict.keys()])
            query += ")"

            cursor.execute(query, insertion_dict)

        except Error as e:
            logging.error("Exception in _insert_row")
            logging.error(e)
            return False
        finally:
            cursor.close()

        return True

    def _insert_generator(self, generator, keys, table_name):
        cursor = self.connection.cursor()
        try:
            query = """INSERT INTO {table_name}({params}) VALUES (""".format(
                table_name = table_name,
                params = ", ".join(keys))
            
            query += ", ".join([":{key}".format(key=i) for i in keys])
            query += ")"

            cursor.executemany(query, generator)
            #self.connection.commit()

        except Error as e:
            logging.error("Exception in _insert_generator")
            logging.error(e)
            return False
        finally:
            cursor.close()

        return True
    
    def _execute_select_query(self, query, data):
        cursor = self.connection.cursor()
        res = None
        try:
            cursor.execute(query, data)
            field_names = [i[0] for i in cursor.description]
            res = cursor.fetchall()
        except Error as e:
            logging.error("Exception in _execute_select_query")
            logging.error(e)
        finally:
            cursor.close()

        return res, field_names
    
    def _pandafy_select(self, query, query_data=None):
        query_data = () if query_data is None else query_data

        data, columns = self._execute_select_query(query, query_data)

        df = pd.DataFrame(data, columns=columns)

        return df
    
class DataDB(BaseDB):
    def __init__(self, data_dir = DATA_DIR):
        super().__init__(data_dir)
    
    def _init_connection(self, dbname="stonks.db"):
        try:
            self.connection = sqlite3.connect(os.path.join(self.data_dir, dbname), check_same_thread=False)
        except Error as e:
            logging.error("Exception in DB connect")
            logging.error(e)

    def get_init_stonks(self):
        query = "SELECT * FROM stonks_static"
        return self._pandafy_select(query)
    
    def get_init_dfs(self):
        query = "SELECT DISTINCT(date) AS date FROM stonks"
        return self._pandafy_select(query)['date'].sort_values().to_list()
    
    def daily_get_df(self, date):
        query = "SELECT * FROM stonks WHERE date=?"
        query_data = (date,)
        return self._pandafy_select(query, query_data).drop('date', axis=1)

    def stonk_get_full_df(self, symbol):
        query = "SELECT date AS Date, avg_sentiment_score AS Score, positive, neutral, negative FROM stonks WHERE Symbol=?"
        query_data = (symbol,)
        return self._pandafy_select(query, query_data)

    def stonk_article_df(self, symbol, date):
        query = "SELECT * FROM articles WHERE date=? AND Symbol=?"
        query_data = (date, symbol, )
        return self._pandafy_select(query, query_data).drop(['date', 'Symbol'], axis=1)

if __name__=="__main__":
    db_helper = DataDB()
    #print(db_helper.get_init_dfs())
    #print(db_helper.get_init_stonks())
    #print(db_helper.daily_get_df("2021-11-01"))


        

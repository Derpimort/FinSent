import os
import sqlite3
from sqlite3.dbapi2 import Error

import pandas as pd
from finsent.constants import DATA_DIR, STOCKS_DIR
import logging

ARTICLES_KEYS = ['Symbol', 'date', 'title', 'description', 'url', 'publishedAt', 'prediction', 'sentiment_score']
STONKS_KEYS = ['Symbol', 'date', 'avg_sentiment_score', 'articles', 'negative', 'neutral', 'positive']
ARTICLES_TABLENAME = "articles"
STONKS_TABLENAME = "stonks"

class DBHelper:
    def __init__(self, data_dir = DATA_DIR):
        self.data_dir = data_dir
        self._init_connection()
        self.create_tables()
    
    def __del__(self):
        self.connection.close()
    
    def _init_connection(self, dbname="stonks.db"):
        try:
            self.connection = sqlite3.connect(os.path.join(self.data_dir, dbname))
        except Error as e:
            logging.error("Exception in DB connect")
            logging.error(e)
    
    def create_tables(self):
        cursor = self.connection.cursor()
        try:
            query = """
            CREATE TABLE IF NOT EXISTS articles(
                Symbol text NOT NULL,
                date date NOT NULL,
                title text NOT NULL,
                description text,
                url text NOT NULL,
                publishedAt datetime NOT NULL,
                prediction text DEFAULT 'neutral',
                sentiment_score real DEFAULT 0);
            
            CREATE TABLE IF NOT EXISTS stonks(
                Symbol text NOT NULL,
                date date NOT NULL,
                avg_sentiment_score real NOT NULL,
                articles integer NOT NULL,
                negative real NOT NULL,
                neutral real NOT NULL,
                positive real NOT NULL);
                """
            cursor.executescript(query)
        except Error as e:
            logging.error("Exception in _check_entry")
            logging.error(e)
        finally:
            cursor.close()

    def _get_entry(self, params_dict, table_name):
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
        entries = self._get_entry(params_dict, table_name)

        if entries and len(entries)>=1:
            return True

        return False
    
    def check_article(self, article_dict):
        return self._check_entry(article_dict, ARTICLES_TABLENAME)
    
    def check_stock_entry(self, stock_dict):
        return self._check_entry(stock_dict, STONKS_TABLENAME)
    
    def _insert_row(self, insertion_dict, table_name):
        assert isinstance(insertion_dict, dict), "Error: need dict"

        cursor = self.connection.cursor()
        try:
            query = """INSERT INTO {table_name}({params}) VALUES (""".format(
                table_name = table_name,
                params = ", ".join(list(insertion_dict.keys())))
            
            query += ", ".join(["?" for key in insertion_dict])
            query += ")"

            cursor.execute(query, insertion_dict.values())

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
    
    @staticmethod
    def generator_wrap(generator, dict):
        for index, i in generator:
            i = i.to_dict()
            i.update(dict)
            yield i

    def insert_articles(self, generator, symbol, date):
        return self._insert_generator(
            generator = DBHelper.generator_wrap(generator, {"Symbol": symbol, "date": date}),
            keys = ARTICLES_KEYS,
            table_name = ARTICLES_TABLENAME
        )
    
    def insert_stonks(self, generator, date):
        return self._insert_generator(
            generator = DBHelper.generator_wrap(generator, {"date": date}),
            keys = STONKS_KEYS,
            table_name = STONKS_TABLENAME
        )
    
if __name__=="__main__":
    db_helper = DBHelper()
    dfs = []
    stonks = []
    for file in os.listdir(STOCKS_DIR):
        if file.endswith("csv"):
            dfs.append(file)
        elif os.path.isdir(os.path.join(STOCKS_DIR, file)):
            stonks.append(file)

    for df in dfs:
        date = df.split(".")[0]
        exists = db_helper.check_stock_entry({
            'date': date
            })
        if exists:
            continue
        df_pd = pd.read_csv(os.path.join(STOCKS_DIR, df))
        db_helper.insert_stonks(df_pd.iterrows(), date=date)
    
    for stonk in stonks:
        path = os.path.join(STOCKS_DIR, stonk)
        for df in os.listdir(path):
            if df=="full.csv":
                continue
            date = df.split(".")[0]
            exists = db_helper.check_article({
                'date': date,
                'Symbol': stonk
            })
            if exists:
                continue
            df_pd = pd.read_csv(os.path.join(path, df))
            db_helper.insert_articles(df_pd.iterrows(), symbol=stonk, date=date)
    db_helper.connection.commit()


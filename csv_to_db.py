import os
import sqlite3
from sqlite3.dbapi2 import Error

import pandas as pd
from finsent.constants import DATA_DIR, NIFTY_FILE, STOCKS_DIR
import logging

from finsent.db_helper import BaseDB

ARTICLES_KEYS = ['Symbol', 'date', 'title', 'description', 'url', 'publishedAt', 'prediction', 'sentiment_score']
STONKS_KEYS = ['Symbol', 'date', 'avg_sentiment_score', 'articles', 'negative', 'neutral', 'positive']
ARTICLES_TABLENAME = "articles"
STONKS_TABLENAME = "stonks"
STONKS_STATIC_TABLENAME = "stonks_static"

class DBHelper(BaseDB):
    def __init__(self, data_dir = DATA_DIR):
        super().__init__(data_dir = data_dir)
        self.create_tables()
    
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
            
            CREATE TABLE IF NOT EXISTS stonks_static(
                Symbol text NOT NULL,
                Company_Name text,
                Industry text,
                Series text,
                ISIN_Code text,
                keywords text
            )
                """
            cursor.executescript(query)
        except Error as e:
            logging.error("Exception in _check_entry")
            logging.error(e)
        finally:
            cursor.close()
    
    def check_article(self, article_dict):
        return self._check_entry(article_dict, ARTICLES_TABLENAME)

    def check_stock_static_entry(self, stock_static_dict):
        return self._check_entry(stock_static_dict, STONKS_STATIC_TABLENAME)
    
    def check_stock_entry(self, stock_dict):
        return self._check_entry(stock_dict, STONKS_TABLENAME)

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
    
    def insert_stonk_static(self, stonk_static_dict):
        exists = self.check_stock_static_entry({
            "Symbol": stonk_static_dict['Symbol']
        })
        if not exists:
            return self._insert_row(stonk_static_dict, STONKS_STATIC_TABLENAME)

    
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
    df = pd.read_csv(os.path.join(DATA_DIR, NIFTY_FILE))
    keywords = pd.read_csv(os.path.join(DATA_DIR, "keywords.csv"), index_col=[0])
    df = df.merge(keywords, on="Symbol")

    for index, data in df.iterrows():
        db_helper.insert_stonk_static(data.to_dict())

    db_helper.connection.commit()


import pandas as pd
import numpy as np
import os
import logging
from finsent.constants import ALL_COLUMNS, NIFTY_FILE, STONK_COLUMNS
from finsent.db_helper import DataDB
from finsent.stock import Stock

class BaseData:
    def __init__(self, data_dir, stonks_dir, use_sqlite):
        self.data_dir = data_dir
        self.stonks_dir = stonks_dir
        self.use_sqlite = use_sqlite
        if use_sqlite:
            self.db_helper = DataDB(data_dir)

        self._init_stonks()
        self._init_dfs()
        self._init_data()
    
    def _init_data(self, *args, **kwargs):
        raise NotImplementedError("Please Implement this method")

    def _get_stonks(self):
        if self.df is not None:
            return self.df['Symbol'].tolist()  
        else:
            return self.stocks['Symbol'].tolist()
    
    def get_stonks_dict(self):
        return [{'value': i, 'label':i} for i in self._get_stonks()]

    def _init_stonks(self):
        if self.use_sqlite:
            self.stocks = self.db_helper.get_init_stonks()
        else:
            self.stocks = pd.read_csv(self.data_dir+NIFTY_FILE)

    def _init_dfs(self):
        if self.use_sqlite:
            self.dfs = self.db_helper.get_init_dfs()
        else:
            # Get all data files
            dfs = []
            for file in os.listdir(self.stonks_dir):
                if file.endswith("csv"):
                    dfs.append(file.split(".")[0])
            dfs.sort()
            self.dfs = dfs
            self.df = None

        self.dfs_pd = pd.Series(pd.to_datetime(self.dfs).astype(np.int64))
    
    def get_df_df(self, df):
        if self.use_sqlite:
            return self.db_helper.daily_get_df(df)
        else:
            return pd.read_csv(os.path.join(self.stonks_dir, "%s.csv" % df))

class DailyData(BaseData):
    def __init__(self, data_dir, stonks_dir, use_sqlite=False):
        super().__init__(data_dir, stonks_dir, use_sqlite)
        
    def _init_data(self):
        if len(self.dfs) == 0:
            logging.error("No csv files found, Please run main.py atleast once before running dashboards")
            # exit(0)
        elif len(self.dfs) < 2:
            logging.error("Only one csv found, delta metrics won't be available")
            self.get_df(self.dfs[-1])
        else:
            self.get_df(self.dfs[-1], self.dfs[-2])

    def get_df(self, df, prev_df=None, reprocess=True):
        """ Return df with delta metrics if prev_df is not None """

        if (not reprocess) and (self.df is not None):
            return self.df

        df = self.get_df_df(df)

        if prev_df:
            prev_df = self.get_df_df(prev_df)

            # Get stock industries
            
            df = self.stocks[['Symbol','Industry']].merge(df, on="Symbol")

            # Compare last 2 scores to get delta
            df = df.merge(prev_df.set_index('Symbol')[
                        'avg_sentiment_score'], on='Symbol')
            df['delta'] = ((df['avg_sentiment_score_x'] -
                            df['avg_sentiment_score_y'])/df['avg_sentiment_score_x'])*100
            df = df.drop('avg_sentiment_score_y', axis=1)
            df['delta_status'] = df['delta'].apply(
                lambda x: 'Increased' if x > 0 else 'Stable' if x == 0 else 'Decreased')

        df = df.round(2)
        df.columns = ALL_COLUMNS
        self.df = df.copy()

        return df
    
    def get_timestamps(self):
        return list(self.dfs_pd[1::(len(self.dfs_pd)//20)+1])
    
    def get_dates(self):
        return ["%s -> %s"%(self.dfs[i], self.dfs[i-1]) for i in range(len(self.dfs)-1,0,-1)]

class StonkData(BaseData):
    def __init__(self, data_dir, stonks_dir, use_sqlite=False):
        super().__init__(data_dir, stonks_dir, use_sqlite)
        self.updated = False
        self.stonk = None

    def _init_data(self):
        if len(self.dfs) != 0:
            self.df = self.get_df_df(self.dfs[-1])
        else:
            logging.error("No csv files found, Please run main.py atleast once before running dashboards")
            # exit(0)
            
    def get_df(self, symbol=None, name=None, reupdate=True):
        if reupdate or not self.updated:
            stock_row = None
            if symbol is not None and symbol != "":
                stock_row = self.stocks[self.stocks['Symbol'].str.contains(symbol)].iloc[0]
            elif name is not None and name != "":
                stock_row = self.stocks[self.stocks['Company Name'].str.contains(name)].iloc[0]
            else:
                stock_row = self.stocks.iloc[0]

            self.symbol = stock_row['Symbol']
            self.name = stock_row['Company Name']

            self.updated = True
            
            return self.get_stonk(cached=False), self.stonk_df

    def get_stonk_data_df(self):
        if self.use_sqlite:
            return self.db_helper.stonk_get_full_df(self.symbol)
        else:
            return pd.read_csv(os.path.join(self.stonks_dir, "%s/full.csv" % self.symbol))
    
    def get_latest_article_df(self, date):
        if self.use_sqlite:
            return self.db_helper.stonk_article_df(self.symbol, date)
        else:
            return pd.read_csv(os.path.join(
                self.stonks_dir, "%s/%s.csv" % (self.symbol, date)))

    def get_stonk(self, cached=True):
        if not self.updated:
            return None
        if cached and self.stonk_df is not None:
            return self.stonk

        data_df = self.get_stonk_data_df()
        self.stonk_df = data_df.sort_values('Date')

        # Read latest available data
        latest = data_df.iloc[-1]
        self.latest_df = self.get_latest_article_df(latest['Date'])

        # Get ticker data and sentiment
        self.stonk = Stock(self.symbol, self.name, sentiment=self.latest_df, ticker=True)
        # df = self.stonk.getStockData()
        # sentiments = self.stonk.getSentiment()
        return self.stonk
        

if __name__=="__main__":
    data_helper = DailyData("data/", "data/Stonks")
    print(data_helper.df)
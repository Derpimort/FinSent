import pandas as pd
import numpy as np
import os
import logging

class BaseData:
    pass

class DailyData(BaseData):
    def __init__(self, data_dir, stonks_dir):
        self.data_dir = data_dir
        self.stonks_dir = stonks_dir
        # Get all data files
        dfs = []
        for file in os.listdir(self.stonks_dir):
            if file.endswith("csv"):
                dfs.append(file.split(".")[0])
        dfs.sort()
        self.dfs = dfs
        self.df = None
        self._init_data()
        #dfs_pd = pd.to_datetime(dfs).astype(np.int64)

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

        df = pd.read_csv(os.path.join(self.stonks_dir, "%s.csv" % df))

        if prev_df:
            prev_df = pd.read_csv(os.path.join(self.stonks_dir, "%s.csv" % prev_df))

            # Get stock industries
            stocks = pd.read_csv(self.data_dir+"ind_nifty500list.csv")
            df = stocks[['Symbol','Industry']].merge(df, on="Symbol")

            # Compare last 2 scores to get delta
            df = df.merge(prev_df.set_index('Symbol')[
                        'avg_sentiment_score'], on='Symbol')
            df['delta'] = ((df['avg_sentiment_score_x'] -
                            df['avg_sentiment_score_y'])/df['avg_sentiment_score_x'])*100
            df = df.drop('avg_sentiment_score_y', axis=1)
            df['delta_status'] = df['delta'].apply(
                lambda x: 'Increased' if x > 0 else 'Stable' if x == 0 else 'Decreased')
        
        self.df = df

        return df

if __name__=="__main__":
    data_helper = DailyData("data/", "data/Stonks")
    print(data_helper.df)
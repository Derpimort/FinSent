"""
 Created on Sun Sep 06 2020 21:22:57

 @author: Derpimort
"""

import os
import sys
import numpy as np
import string
import random
import pandas as pd
from tqdm import tqdm

from finsent.api import Api
from finsent.stock import Stock
from finsent.sentiment_analysis import get_sentiment

import yfinance as yf

from pytorch_pretrained_bert.modeling import BertForSequenceClassification
from pytorch_pretrained_bert.tokenization import BertTokenizer
from finsent.constants import DATA_DIR, MODEL_DIR

def create_dirs(df, data_dir):
    """ Create all stock symbols and data directories """
    flag = False
    for symbol in df['Symbol']:
        dirname = os.path.join(data_dir, symbol)
        # Create a consolidated score csv if not exists
        if not os.path.exists(dirname):
            flag = True
            os.makedirs(dirname)
            with open(os.path.join(dirname, "full.csv"), "w") as f:
                f.write("Date,Score,positive,neutral,negative\n")
    return flag



def main(stonks, data_dir, MODEL_DIR=MODEL_DIR, date=None, prev_10=False):
    """ 
    Process all stocks and write data to data_dir. 
    Will process data till 10 days prior to given date on the first run
    
    Parameters
    -----------
    stonks: pd.DataFrame
            df containing stock symbols, names and keywords
    data_dir:   str
                target directory to write the data to, Change the data_dir in the dashboard files if you change it here
    MODEL_DIR:  str
                directory containing finbert sentiment model, Default: defined in constants.py
    date:   str
            date to process data for (yyyy-mm-dd). Default: today's date
    
    Output
    -------
    Prints directory containing all the output files:
        1. individual stockwise data
        2. consodilated sentiment data of all stocks for given date
        3. consodilated sentiment data of each stock for all processed dates
    """

    # Get today's date if date param not provided
    date = pd.to_datetime('today') if not date else pd.to_datetime(date)
    dates=[]
    # check output directories
    if create_dirs(df, data_dir) or prev_10:
        dates = [date - pd.DateOffset(days=i) for i in range(9,-1,-1)]
    else:
        dates = [date]
    
    # Get finbert model, newsapi client and tokenizer
    model = BertForSequenceClassification.from_pretrained(MODEL_DIR, num_labels=3, cache_dir=None)
    # apikey = ""
    # with open("newsapi.key", "r") as apikey_f:
    #     apikey = apikey_f.read().strip("\n")
    api = Api("newsapi.key")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    print("Started, processing data for last %d day(s)"%len(dates))
    for index, curr_date in enumerate(dates):
        result = []
        not_processed = []
        curr_date = str(curr_date.date())
        print("Day %d date: %s"%(index+1, curr_date))
        for index, (symbol, name, keywords) in tqdm(df[['Symbol', 'Company Name', 'keywords']].iterrows(), total=len(df)):
            try:
                # Articles df containing newsapi output
                articles = pd.DataFrame(api.get_topn(keywords, curr_date))[['title', 'description', 'url', 'publishedAt']]
                articles = articles.dropna()

                # Create sentences for each articles using title and description
                # Modify this if title or desc not needed
                sentences = (articles['title'] + ". " + articles['description']).values

                # Get finbert output and create a Stock class
                stock = Stock(symbol, name, get_sentiment(sentences, model, tokenizer))

                # Write stock sentiment output and append score to consolidated df
                stock.write_csv(os.path.join(data_dir,"%s/%s.csv"%(symbol,curr_date)), articles)
                sentiment = stock.getSentiment()
                result.append(sentiment)

                # Write current stock data to stock's individual consolidated df
                with open(os.path.join(data_dir, "%s/full.csv"%symbol), "a") as f:
                    f.write("%s,%f,%f,%f,%f\n"%(curr_date, sentiment['avg_sentiment_score'],sentiment['positive'], sentiment['neutral'], sentiment['negative']))
            except Exception as e:
                not_processed.append((symbol, e))

        if len(not_processed)>0:
            print("Following stocks not processed due to no articles or errors")
            for stock_sym, exception in not_processed:
                print(stock_sym, exception)
        print("Writing results to", os.path.join(data_dir, "%s.csv"%curr_date))
        result_df = pd.DataFrame(result)
        result_df.to_csv(os.path.join(data_dir, "%s.csv"%curr_date), index=False)



if __name__=="__main__":
    stonks = pd.read_csv(DATA_DIR+"ind_nifty500list.csv")
    keywords = pd.read_csv(DATA_DIR+"keywords.csv")
    df = stonks.merge(keywords, on='Symbol')

    # date = input("Enter date(YYYY-MM-DD), leave empty if today: ")
    # date = None if date=="" else date
    # Get date from cmdline args
    date = sys.argv[1] if len(sys.argv)>1 else None

    ## Comment the following two lines to process all stocks instead of just select 3
    selected_stocks=["ADANIPOWER", "TCS", "RELIANCE", "IDEA", "LTI", "INFY"]
    df = df[df['Symbol'].isin(selected_stocks)]

    main(df, os.path.join(DATA_DIR,"Stonks/"), date=date, prev_10=True)

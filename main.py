import os
import sys
import numpy as np
import string
import random
import pandas as pd
from tqdm import tqdm

from api import Api
from stock import Stock
from sentiment_analysis import get_sentiment

import yfinance as yf

from pytorch_pretrained_bert.modeling import BertForSequenceClassification
from pytorch_pretrained_bert.tokenization import BertTokenizer
from constants import DATA_DIR, MODEL_DIR

def create_dirs(df, data_dir):
    flag = False
    for symbol in df['Symbol']:
        dirname = os.path.join(data_dir, symbol)
        if not os.path.exists(dirname):
            flag = True
            os.makedirs(dirname)
            with open(os.path.join(dirname, "full.csv"), "w") as f:
                f.write("Date,Score,positive,neutral,negative\n")
    return flag



def main(stonks, data_dir, MODEL_DIR=MODEL_DIR, date=None):
    date = pd.to_datetime('today') if not date else pd.to_datetime(date)
    dates=[]
    if create_dirs(df, data_dir):
        dates = [date - pd.DateOffset(days=i) for i in range(9,-1,-1)]
    else:
        dates = [date]
    model = BertForSequenceClassification.from_pretrained(MODEL_DIR, num_labels=3, cache_dir=None)
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
                articles = pd.DataFrame(api.get_topn(keywords, curr_date))[['title', 'description', 'url', 'publishedAt']]
                articles = articles.dropna()
                sentences = (articles['title'] + ". " + articles['description']).values
                stock = Stock(symbol, name, get_sentiment(sentences, model, tokenizer))
                stock.write_csv(os.path.join(data_dir,"%s/%s.csv"%(symbol,curr_date)), articles)
                sentiment = stock.getSentiment()
                result.append(sentiment)
                with open(os.path.join(data_dir, "%s/full.csv"%symbol), "a") as f:
                    f.write("%s,%f,%f,%f,%f\n"%(curr_date, sentiment['avg_sentiment_score'],sentiment['positive'], sentiment['neutral'], sentiment['negative']))
            except Exception as e:
                not_processed.append(symbol)

        if len(not_processed)>0:
            print("Following stocks not processed due to no articles or errors")
            for i in not_processed:
                print(i)
        print("Writing results to", os.path.join(data_dir, "%s.csv"%curr_date))
        result_df = pd.DataFrame(result)
        result_df.to_csv(os.path.join(data_dir, "%s.csv"%curr_date), index=False)



if __name__=="__main__":
    stonks = pd.read_csv(DATA_DIR+"ind_nifty500list.csv")
    keywords = pd.read_csv(DATA_DIR+"keywords.csv")
    df = stonks.merge(keywords, on='Symbol')

    # date = input("Enter date(YYYY-MM-DD), leave empty if today: ")
    # date = None if date=="" else date
    date = sys.argv[1] if len(sys.argv)>1 else None

    ## Comment the following two lines to process all stocks instead of just select 3
    selected_stocks=["ADANIPOWER", "TCS", "RELIANCE"]
    df = df[df['Symbol'].isin(selected_stocks)]

    main(df, os.path.join(DATA_DIR,"Stonks/"), date=date)

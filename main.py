import os
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

DATA_DIR="data/"

def create_dirs(df, data_dir):
    for symbol in df['Symbol']:
        dirname = os.path.join(data_dir, symbol)
        if not os.path.exists(dirname):
            os.makedirs(dirname)



def main(stonks, data_dir, MODEL_DIR="finbert/models/sentiment/base", date=None):
    create_dirs(df, data_dir)
    date = str(pd.to_datetime('today').date()) if not date else date
    model = BertForSequenceClassification.from_pretrained(MODEL_DIR, num_labels=3, cache_dir=None)
    api = Api("newsapi.key")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    result = []
    not_processed = []
    print("Started")
    for index, (symbol, name, keywords) in tqdm(df[['Symbol', 'Company Name', 'keywords']].iterrows()):
        try:
            articles = pd.DataFrame(api.get_topn(keywords, date))[['title', 'description', 'url', 'publishedAt']]
            sentences = (articles['title'] + ". " + articles['description']).values
            stock = Stock(symbol, name, get_sentiment(sentences, model, tokenizer))
            stock.write_csv(os.path.join(data_dir,"%s/%s.csv"%(symbol,date)), articles)
            result.append(stock.getSentiment())
        except Exception as e:
            not_processed.append(symbol)

    if len(not_processed)>0:
        print("Following stocks not processed due to no articles or errors")
        for i in not_processed:
            print(i)
    print("Writing results to", os.path.join(data_dir, "%s.csv"%date))
    result_df = pd.DataFrame(result)
    result_df.to_csv(os.path.join(data_dir, "%s.csv"%date), index=False)



if __name__=="__main__":
    stonks = pd.read_csv(DATA_DIR+"ind_nifty500list.csv")
    keywords = pd.read_csv(DATA_DIR+"keywords.csv")
    df = stonks.merge(keywords, on='Symbol')

    selected_stocks=["ADANIPOWER", "TCS", "RELIANCE"]
    df = df[df['Symbol'].isin(selected_stocks)]
    main(df, os.path.join(DATA_DIR,"Stonks/"), date="2020-08-31")
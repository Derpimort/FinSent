import os
import numpy as np
import string
import random
import pandas as pd

from api import Api
from stock import Stock
from sentiment_analysis import get_sentiment

import yfinance as yf

from pytorch_pretrained_bert.modeling import BertForSequenceClassification
from pytorch_pretrained_bert.tokenization import BertTokenizer

DATA_DIR="data/"


def main(stonks, MODEL_DIR="finbert/models/sentiment/base"):
    model = BertForSequenceClassification.from_pretrained(MODEL_DIR, num_labels=3, cache_dir=None)
    api = Api("newsapi.key")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    tickers = yf.Tickers(" ".join(stonks['Symbol'].values)).tickers
    # result = pd.DataFrame(columns=['stock', 'predictions', 'avg_sentiment_score', 'last_month_recomms', 'last_year_recomms', 'monthly_tick'])

    for symbol, name in stonks.values:
        stock = Stock(symbol, name, get_sentiment(list(api.get_topn(name)), model, tokenizer))
        stock.setTicker(getattr(tickers, symbol))
        try:
            stock.setRecommendations(getattr(tickers, symbol).recommendations)
        except Exception as e:
            pass
        yield stock


if __name__=="__main__":
    nasdaq = pd.read_csv(DATA_DIR+"NASDAQ.csv")
    selected_stocks = nasdaq[:10]
    for stock in main(selected_stocks):
        print(stock)
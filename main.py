import pandas as pd
from api import Api
import yfinance as yf
import random

DATA_DIR="data/"

def placeholder(x):
    return random.random(), random.random(), random.random()

def main(stonks):
    sentiment_analyzer = placeholder
    tickers = yf.Tickers(" ".join(stonks['Symbol'].values)).tickers
    for symbol, name in stonks.values:
        sentiment = sentiment_analyzer(name)
        recommendations = None
        try:
            recommendations = getattr(tickers, symbol).recommendations
            recommendations = recommendations.loc[pd.to_datetime('today') - pd.DateOffset(months=1):]
        except Exception as e:
            pass
        yield sentiment, recommendations


if __name__=="__main__":
    nasdaq = pd.read_csv(DATA_DIR+"NASDAQ.csv")
    selected_stocks = nasdaq[:10]
    print(list(main(selected_stocks)))
import pandas as pd
import yfinance as yf

class Stock:
    name=""
    symbol=""
    sentiment=None
    avg_score=0
    history=None
    monthly_recommendations=None
    yearly_recommendations=None
    

    def __init__(self, symbol, name, sentiment=None):
        # Will inherit from yfinance Ticker later for efficient usage... might not need to though.
        self.symbol = symbol
        self.name = name
        if sentiment is not None:
            self.setSentiment(sentiment)
        self.ticker = yf.Ticker(symbol)
        
    
    def setSentiment(self, sentiment):
        self.sentiment = sentiment
        self.avg_score = sentiment['sentiment_score'].mean()

    def setTicker(self, ticker):
        self.ticker = ticker

    def setRecommendations(self, recommendations):
        self.monthly_recommendations = (recommendations.loc[pd.to_datetime('today') - 
                                        pd.DateOffset(months=1):]['To Grade']
                                        .value_counts(normalize=True) * 100).to_dict()
        self.yearly_recommendations = (recommendations.loc[pd.to_datetime('today') - 
                                        pd.DateOffset(years=1):]['To Grade']
                                        .value_counts(normalize=True) * 100).to_dict()
    
    def write_csv(self, fname, articles=None):
        if articles is None:
            self.sentiment.to_csv(fname, index=False)
        else:
            articles.join(self.sentiment[['prediction', 'sentiment_score']]).to_csv(fname, index=False)

    def getStockData(self, period="1y"):
        return self.ticker.history(period=period)

    def getSentiment(self):
        sentiment_dict={'Symbol':self.symbol,
                        'negative':0,
                        'neutral':0,
                        'positive':0,
                        'avg_sentiment_score':self.avg_score}
        sentiment_dict.update((self.sentiment['prediction'].value_counts(normalize=True) * 100).to_dict())
            
        return sentiment_dict

    def __str__(self):
        return  "\n".join([
                "Name: %s"%self.name,
                "Symbol: %s"%self.symbol,
                "Sentiment: %s"%str(self.sentiment),
                "Avg_sentiment: %f"%self.avg_score])

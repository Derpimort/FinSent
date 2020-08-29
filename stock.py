import pandas as pd

class Stock:
    name=""
    symbol=""
    sentiment=None
    avg_score=0
    history=None
    monthly_recommendations=None
    yearly_recommendations=None
    

    def __init__(self, symbol, name, sentiment=None):
        # Will inherit from yfinance Ticker later for efficient usage
        self.symbol = symbol
        self.name = name
        if sentiment is not None:
            self.setSentiment(sentiment)
    
    def setSentiment(self, sentiment):
        self.sentiment = (sentiment['prediction'].value_counts(normalize=True) * 100).to_dict()
        self.avg_score = sentiment['sentiment_score'].mean()

    def setTicker(self, ticker):
        self.history = ticker.history(period="1mo")['Close']

    def setRecommendations(self, recommendations):
        self.monthly_recommendations = (recommendations.loc[pd.to_datetime('today') - 
                                        pd.DateOffset(months=1):]['To Grade']
                                        .value_counts(normalize=True) * 100).to_dict()
        self.yearly_recommendations = (recommendations.loc[pd.to_datetime('today') - 
                                        pd.DateOffset(years=1):]['To Grade']
                                        .value_counts(normalize=True) * 100).to_dict()

    def __str__(self):
        return  "\n".join([
                "Name: %s"%self.name,
                "Symbol: %s"%self.symbol,
                "Sentiment: %s"%str(self.sentiment),
                "Avg_sentiment: %f"%self.avg_score])

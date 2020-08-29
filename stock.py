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

    def getStockData(self, period="1y"):
        return self.ticker.history(period=period)

    def getSentiment(self, dataframe=True):
        if dataframe:
            df = pd.DataFrame(self.sentiment['prediction'].value_counts(normalize=True) * 100).reset_index()
            df.columns = ['Sentiment', 'percentage']
            df['Articles']=''
            return df, self.avg_score
        else:
            sentiment_dict = (self.sentiment['prediction'].value_counts(normalize=True) * 100).to_dict()
            return sentiment_dict, self.avg_score

    def __str__(self):
        return  "\n".join([
                "Name: %s"%self.name,
                "Symbol: %s"%self.symbol,
                "Sentiment: %s"%str(self.sentiment),
                "Avg_sentiment: %f"%self.avg_score])

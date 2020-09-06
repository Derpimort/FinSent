"""
 Created on Sun Sep 06 2020 22:42:46

 @author: Derpimort
"""

import pandas as pd
import yfinance as yf

class Stock:
    """ 
    Class to store stock data for each symbol, easier accesibility for post processing funcs and data
    
    ...

    Attributes
    -----
    symbol: str
            Stock symbol
    name:   str
            Stock name
    sentiment:  pd.DataFrame
                result df from getSentiment function of sentiment_analysis.py
    avg_score:  int
                Average sentiment score of sentiment df
    ticker: yf.Ticker
            Yahoo finance ticker for given stock, useful in getting market history
    recommendations:    dict
                        Recommendations status acquired from yf.Ticker... not too reliable or updated


    Methods
    --------
    write_csv(self, fname, articles=None)
        write sentiment df to given file
    
    Getters and Setters for sentiment df, ticker data
    """

    def __init__(self, symbol, name, sentiment=None, ticker=False):
        """
        Parameters
        -----------
        symbol: str
                stock symbol
        name:   str
                stock name
        sentiment:  pd.DataFrame (Optional)
                    result df from getSentiment function of sentiment_analysis.py
        ticker: bool
                if True, will automatically get ticker from yahoo finance api using stock symbol.
                By default append .NS for indian stocks. Default False
        """
        self.sentiment=None
        self.avg_score=0
        self.ticker=None
        self.monthly_recommendations=None
        self.yearly_recommendations=None
        # Will inherit from yfinance Ticker later for efficient usage... might not need to though.
        self.symbol = symbol
        self.name = name
        if sentiment is not None:
            self.setSentiment(sentiment)
        if ticker:
            self.ticker = yf.Ticker(symbol+".NS")
        
    
    def setSentiment(self, sentiment):
        """
        Parameters
        -----------
        sentiment:  pd.DataFrame (Optional)
                    result df from getSentiment function of sentiment_analysis.py
        """
        self.sentiment = sentiment
        self.avg_score = sentiment['sentiment_score'].mean()

    def setTicker(self, ticker):
        """
        If you dont wanna explicitly set this then just pass ticker=True during initialization
        Parameters
        -----------
        ticker: yf.Ticker
            Yahoo finance ticker for given stock, useful in getting market history.
            
        """
        self.ticker = ticker

    def setRecommendations(self, recommendations):
        """
        Parameters
        -----------
        recommendations:    dict
                            Recommendations df from yf.Ticker.recommendations

        """
        self.monthly_recommendations = (recommendations.loc[pd.to_datetime('today') - 
                                        pd.DateOffset(months=1):]['To Grade']
                                        .value_counts(normalize=True) * 100).to_dict()
        self.yearly_recommendations = (recommendations.loc[pd.to_datetime('today') - 
                                        pd.DateOffset(years=1):]['To Grade']
                                        .value_counts(normalize=True) * 100).to_dict()
    
    def write_csv(self, fname, articles=None):
        """
        Parameters
        -----------
        fname:  str
                destination csv filename
        articles:   pd.DataFrame (Optional)
                    Dataframe containing articles. If not providied then will just write sentiment df
        """
        if articles is None:
            self.sentiment.to_csv(fname, index=False)
        else:
            articles.join(self.sentiment[['prediction', 'sentiment_score']]).to_csv(fname, index=False)

    def getStockData(self, period="1y"):
        """
        Parameters
        -----------
        period: str
                period for getting stock ticker data. See yf.Ticker documentation for acceptable values.
                Default = 1y
        """
        return self.ticker.history(period=period)

    def getSentiment(self):
        """
        Returns
        --------
        sentiment_dict: dict
                        dictionary containing aggregated sentiment data.
        """
        sentiment_dict={'Symbol':self.symbol,
                        'avg_sentiment_score':self.avg_score,  
                        'articles': len(self.sentiment),
                        'negative':0,
                        'neutral':0,
                        'positive':0}
        sentiment_dict.update((self.sentiment['prediction'].value_counts(normalize=True) * 100).to_dict())
            
        return sentiment_dict

    def __str__(self):
        return  "\n".join([
                "Name: %s"%self.name,
                "Symbol: %s"%self.symbol,
                "Sentiment: %s"%str(self.sentiment),
                "Avg_sentiment: %f"%self.avg_score])

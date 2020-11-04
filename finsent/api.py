"""
 Created on Sun Sep 06 2020 19:18:27

 @author: Derpimort
"""

from newsapi import NewsApiClient


class Api(NewsApiClient):
    """ 
    Override NewsApi class to support apikey from file and a custom news getter function

    ...

    Attributes
    -----
    apikey: str
            apikey for NewsAPI

    Methods
    --------
    get_topn(keywords, date)
        get top100 articles from the NewsApi
    """

    def __init__(self, apikey):
        """
        Parameters
        -----------
        apikey: str
                apikey or filename which contains the apikey
        """
        if len(apikey.split(".")) > 1:
            with open(apikey, "r") as apikeyf:
                apikey = apikeyf.readline().strip()

        super().__init__(api_key=apikey)

    def get_topn(self, keywords, date):
        """
        Parameters
        -----------
        keywords:   str
                    comma separated keywords to be searched for
        date:   str
                Date for which to fetch the articles (yyyy-mm-dd)

        Returns
        --------
        articles:   list
                    List of dict of articles fetched
        """
        query = " OR ".join(keywords.split(","))

        top_news = super().get_everything(q=query,
                                          from_param=date,
                                          to=date,
                                          sort_by='relevancy',
                                          page_size=100)

        return top_news['articles']

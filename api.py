from newsapi import NewsApiClient

class Api(NewsApiClient):
    def __init__(self, apikey):
        if len(apikey.split(".")) > 1:
            with open(apikey, "r") as apikeyf:
                apikey = apikeyf.readline()

        super().__init__(api_key=apikey)
    
    def get_topn(self, query):
        top_headlines = super().get_everything(qintitle=query, language='en', sort_by="publishedAt")

        assert top_headlines['status']=='ok', "Error, fetching news from api"

        for article in top_headlines['articles']:
            yield article['title']
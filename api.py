from newsapi import NewsApiClient

class Api(NewsApiClient):
    def __init__(self, apikey):
        if len(apikey.split(".")) > 1:
            with open(apikey, "r") as apikeyf:
                apikey = apikeyf.readline()

        super().__init__(api_key=apikey)
    
    def get_topn(self, keywords, date):
        query = " OR ".join(keywords.split(","))
        top_news = super().get_everything(q=query,
                        from_param=date,
                        to=date,
                        sort_by='relevancy',
                        page_size=100)

        assert top_news['status']=='ok', "Error, fetching news from api"

        return top_news['articles']
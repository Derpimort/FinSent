import os

DATA_DIR = "data/"
MODEL_DIR = "finbert/models/sentiment/base"
STOCKS_DIR = os.path.join(DATA_DIR, "Stonks/")

NIFTY_FILE = "ind_nifty500list.csv"
KEYWORDS_FILE = "keywords.csv"

ALL_COLUMNS = ["Symbol", "Industry", "Sentiment", "Articles", "Negative", "Neutral", "Positive", "Delta", "Delta Status"]
DAILY_COLUMNS = ["Symbol", "Industry", "Sentiment", "Articles", "Delta", "Delta Status"]
DAILY_COLUMNS_HEADER = ["Symbol", "Industry", "Sentiment", "Articles", "Delta", "Status"]
# Financial-Sentiment-Analysis

## Setup

1. Install dependencies `conda env create -f environment.yml`
2. Create a file `newsapi.key` and paste your news API key in the first line.
3. Download model from [link](https://prosus-public.s3-eu-west-1.amazonaws.com/finbert/finbert-sentiment/pytorch_model.bin) and put it in default models directory `finbert/models/sentiment/base/`

## Run

1. `conda activate finbert`
2. `python3 main.py` Input date if manual else it'll fetch data for today.
3. `python3 app.py` for Dashboard 1.
4. `python3 app1.py` for Dashboard 2.

Note : The terminal will output the url for each dashboard

### Screenshots
![Home](resources/Stock.png)
![Main](resources/Main.png)

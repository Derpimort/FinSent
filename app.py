import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import yfinance as yf
from api import Api
from stock import Stock
from sentiment_analysis import get_sentiment

from pytorch_pretrained_bert.modeling import BertForSequenceClassification
from pytorch_pretrained_bert.tokenization import BertTokenizer

DATA_DIR = "data/"
MODEL_DIR = "finbert/models/sentiment/base"
model = BertForSequenceClassification.from_pretrained(MODEL_DIR, num_labels=3, cache_dir=None)
api = Api("newsapi.key")
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
reference_score = 0

stocks = pd.read_csv(DATA_DIR+"stocks.csv")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Financial sentiment analysis'),

    html.P(children='''
        Analyze stock news sentiment with FinBERT.
    '''),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='select_stock',
                options=[{'label': name, 'value': sym} for sym, name in stocks.values],
                value='GOOGL'
            )
        ], className="six columns")
    ], className="row"),
    html.Div([
        html.Div([
            html.H3(id='stock_name_header'),
            html.P(id='stock_name_details'),
            dcc.Graph(id='stock_sentiment_bargraph')
        ], className="six columns"),
        html.Div([
            dcc.Graph(id='stock_sentiment_guage'),
        ], className="six columns"),
    ], className="row"),
    html.Div([
        dcc.Graph(id='stock_data_graph')
    ])
])

@app.callback(
    [Output('stock_data_graph', 'figure'),
    Output('stock_sentiment_bargraph', 'figure'),
    Output('stock_sentiment_guage', 'figure'),
    Output('stock_name_header', 'children'),
    Output('stock_name_details', 'children'),],
    [Input('select_stock', 'value')]
)
def update(symbol):
    symbol = 'GOOGL' if not symbol else symbol
    name = stocks[stocks['Symbol']==symbol]['Name'].iloc[0]

    stock = Stock(symbol, name, get_sentiment(list(api.get_topn(name)), model, tokenizer))
    df = stock.getStockData()
    sentiment_df, avg_sentiment = stock.getSentiment()

    stock_fig = stock_graph(df, symbol)
    sentiment_fig = sentiment_graph(sentiment_df)
    avg_sentiment_fig = avg_sentiment_graph(avg_sentiment)

    return stock_fig, sentiment_fig, avg_sentiment_fig, symbol, name

def stock_graph(df, symbol):
    fig = px.line(df, y=['Open', 'High', 'Low', 'Close'], title='%s stock'%symbol, hover_data=['Volume', 'Dividends', 'Stock Splits'])

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    return fig

def sentiment_graph(sentiment_df):
    fig = px.bar(sentiment_df, 
        x='percentage', 
        y='Articles', 
        color='Sentiment', 
        orientation='h', 
        hover_data=['Sentiment', 'percentage'],
        color_discrete_sequence=["#c44e52", "#f4e08a", "#55a868"],
        height=240)
    return fig

def avg_sentiment_graph(avg_sentiment):
    global reference_score
    fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = avg_sentiment,
        mode = "gauge+number+delta",
        title = {'text': "Average Sentiment Score"},
        delta = {'reference': reference_score},
        gauge = {'axis': {'range': [-1, 1]},
                'bar': {'color': "#4878d0"},
                'steps' : [
                    {'range': [-1, -0.3], 'color': "#ff9f9b"},
                    {'range': [-0.3, 0.3], 'color': "#fffea3"},
                    {'range': [0.3, 1], 'color': "#8de5a1"}],
                #'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 490}
                }))
    reference_score = avg_sentiment
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
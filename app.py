import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import yfinance as yf

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = yf.Ticker('GOOGL').history(period="1y")

fig = px.line(df, y=['Open', 'High', 'Low', 'Close'], title='Google stock', hover_data=['Volume', 'Dividends', 'Stock Splits'])

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

app.layout = html.Div(children=[
    html.H1(children='Financial sentiment analysis'),

    html.Div(children='''
        Analyze stock news sentiment with FinBERT.
    '''),

    dcc.Graph(
        id='Stock data',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
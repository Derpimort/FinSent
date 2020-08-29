import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import yfinance as yf

DATA_DIR = "data/"

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
            ),
            html.H3(id='stock_name_header'),
            html.P(id='stock_name_details')
        ], className="six columns"),

        html.Div([
            dcc.Graph(
        id='stock_data_graph')
        ], className="six columns"),
    ], className="row"),
])

@app.callback(
    [Output('stock_data_graph', 'figure'),
    Output('stock_name_header', 'children'),
    Output('stock_name_details', 'children'),],
    [Input('select_stock', 'value')]
)
def stock_graph(symbol):
    symbol = 'GOOGL' if not symbol else symbol

    df = yf.Ticker(symbol).history(period="1y")
    name = stocks[stocks['Symbol']==symbol]['Name']
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

    return fig, symbol, name

if __name__ == '__main__':
    app.run_server(debug=True)
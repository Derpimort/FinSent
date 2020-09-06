"""
 Created on Sun Sep 06 2020 19:30:34

 @author: Derpimort
"""


import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from stock import Stock

# Data dir containing stock list and preprocessed data
from constants import DATA_DIR, STOCKS_DIR


# stocks list
stocks = pd.read_csv(DATA_DIR+"ind_nifty500list.csv")[['Symbol', 'Company Name']]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Dashboard components layout
app.layout = html.Div(children=[
    html.H1(children='Financial sentiment analysis'),

    html.P(children='''
        Analyze news sentiment with FinBERT.
    '''),
    html.Div([
        html.Div([
            html.H4(id="stock_symbol", children="RELIANCE"),
            html.P(id="stock_name", children="Reliance Industries")
        ], className="four columns"),
        html.Div([
            html.Div([
                html.H5("Select stock"),
                dcc.Dropdown(
                id='select_stock',
                options=[{'label': "%s - %s"%(sym, name), 'value': sym} for sym, name in stocks.values],
                value='RELIANCE'
            )
            ]),
        ], className="six columns")
    ], className="row"),
    html.Div([
        html.Div([
            dcc.Graph(id='stock_data_graph')
        ], className="eight columns"),
        html.Div([
            dcc.Graph(id='stock_sentiment_guage')
        ], className="four columns"),
    ], className="row"),
    dash_table.DataTable(
        id='stock_data_table',
        style_cell={
        # all three widths are needed
        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
        'height': 'auto',
        'whiteSpace': 'normal'
    },
    
        columns = [{"name": i, "id": i, "presentation": "markdown"} for i in ['title', 'publishedAt', 'prediction',
       'sentiment_score']]
    )
])

# Update function on stock selection from dropdown
@app.callback(
    [Output('stock_data_graph', 'figure'),
    Output('stock_sentiment_guage', 'figure'),
    Output('stock_data_table', 'data'),
    Output('stock_symbol', 'children'),
    Output('stock_name', 'children')],
    [Input('select_stock', 'value')]
)
def update(dropdown):
    
    symbol = 'RELIANCE' if not dropdown else dropdown
    name = stocks[stocks['Symbol']==symbol]['Company Name'].iloc[0]

    return get_graphs(symbol, name)

def get_graphs(symbol, name):
    """
        Parameters
        -----------
        symbol: str
                stock symbol
        name:   str
                stock name
        
        Returns
        --------
        stock_fig:  plotly.graph_objects.Figure
                    line plot with stock sentiment and close value over time
        avg_sentiment_fig:  plotly.graph_objects.Figure
                            guage chart with stock sentiment score and delta value
        latest_df:  dict
                    dictionary containing latest articles records
        symbol: str
                stock symbol
        name:   str
                stock name
    """
    # get stock symbol from either symbol or name
    stock = None
    if symbol is not None and symbol != "":
        stock = stocks[stocks['Symbol'].str.contains(symbol)].iloc[0]
    else:
        stock = stocks[stocks['Company Name'].str.contains(name)].iloc[0]
    symbol = stock['Symbol']
    name = stock['Company Name']
    
    # read dataframes
    data_df = pd.read_csv(os.path.join(STOCKS_DIR, "%s/full.csv"%symbol))
    data_df = data_df.sort_values('Date')

    # Read latest available data
    latest = data_df.iloc[-1]
    latest_df = pd.read_csv(os.path.join(STOCKS_DIR, "%s/%s.csv"%(symbol,latest['Date'])))

    # Get ticker data and sentiment
    stock = Stock(symbol, name, sentiment=latest_df, ticker=True)
    df = stock.getStockData()
    sentiments = stock.getSentiment()

    # get graphs and tabledata
    stock_fig = stock_graph(df, symbol, data_df)
    avg_sentiment_fig = avg_sentiment_graph(stock.avg_score, data_df.iloc[-2]['Score'])
    latest_df['title'] = '[' + latest_df['title'].astype(str) + '](' + latest_df['url'].astype(str) + ')'

    return stock_fig, avg_sentiment_fig, latest_df.drop(['description', 'url'], axis=1).to_dict('records'), symbol, name

def stock_graph(df, symbol, data_df):
    data_df['Date'] = pd.to_datetime(data_df['Date'])
    data_df = data_df.join(df['Close'], on='Date')
    x = data_df['Date'].dt.date
    #df = df[df.index.isin(x)]
    # x =
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=x, y=data_df['positive'],
        mode='lines',
        line=dict(width=0.5, color='rgb(111, 231, 219)'),
        stackgroup='one',
        name="positive",
        groupnorm='percent' # sets the normalization for the sum of the stackgroup
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x, y=data_df['neutral'],
        mode='lines',
        line=dict(width=0.5, color='rgb(233, 241, 206)'),
        stackgroup='one',
        name='neutral'
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x, y=data_df['negative'],
        mode='lines',
        line=dict(width=0.5, color='rgb(233, 169, 170)'),
        stackgroup='one',
        name='negative'
    ), secondary_y=False)

    fig.add_trace(go.Scatter(x=x, y=data_df['Close'],
                        mode='lines+markers',
                        name='Close',
                        connectgaps=True), secondary_y=True)

    fig.update_layout(
        showlegend=True,
        xaxis_type='category',
        yaxis=dict(
            type='linear',
            range=[1, 100],
            ticksuffix='%'))

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


def avg_sentiment_graph(avg_sentiment, reference_score):
    fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = avg_sentiment,
        mode = "gauge+number+delta",
        title = {'text': "Average Sentiment Score w/ Delta"},
        delta = {'reference': reference_score},
        gauge = {'axis': {'range': [-1, 1]},
                'bar': {'color': "#4878d0"},
                'steps' : [
                    {'range': [-1, -0.3], 'color': "#ff9f9b"},
                    {'range': [-0.3, 0.3], 'color': "#fffea3"},
                    {'range': [0.3, 1], 'color': "#8de5a1"}],
                #'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 490}
                }),
                )

    return fig

if __name__ == '__main__':
    # host 0.0.0.0 for docker
    app.run_server(host='0.0.0.0',debug=True)

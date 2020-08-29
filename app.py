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


DATA_DIR = "data/"
STOCKS_DIR = os.path.join(DATA_DIR,"Stonks/")

button_clicks = 0

stocks = pd.read_csv(DATA_DIR+"ind_nifty500list.csv")[['Symbol', 'Company Name']]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Financial sentiment analysis'),

    html.P(children='''
        Analyze news sentiment with FinBERT.
    '''),
    html.Div([
        html.Div([
            html.Div([
                html.H5("Select stock"),
                dcc.Dropdown(
                id='select_stock',
                options=[{'label': name, 'value': sym} for sym, name in stocks.values],
                value='RELIANCE'
            )
            ]),
        ], className="three columns"),
        html.Div([
            html.Br(),
            html.P("---OR---")
        ], className="one columns"),
        html.Div([
            html.H5("Stock symbol"),
            dcc.Input(id="stock_symbol_input", value="RELIANCE", type="text")
            ], className="two columns"),
        html.Div([
            html.H5("News search term"),
            dcc.Input(id="stock_search_input", value="Reliance Industries", type="text")
            ], className="two columns offset-by-one column"),
        html.Div([
            html.Button("Search", id="stock_search_submit", n_clicks=0),
            html.P("")
        ], className="two columns offset-by-one column")

    ], className="row"),
    html.Div([
        html.Div([
            dcc.Graph(id='stock_data_graph')
        ], className="eight columns"),
        html.Div([
            dcc.Graph(id='stock_sentiment_guage'),
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
        columns = [{"name": i, "id": i} for i in ['title', 'url', 'publishedAt', 'prediction',
       'sentiment_score']]
    )
])

@app.callback(
    [Output('stock_data_graph', 'figure'),
    Output('stock_sentiment_guage', 'figure'),
    Output('stock_data_table', 'data')],
    [Input('stock_search_submit', 'n_clicks'),
    Input('select_stock', 'value'),
    State('stock_symbol_input', 'value'),
    State('stock_search_input', 'value')]
)
def update(n_clicks, dropdown, sym_input, searchq):
    global button_clicks #Probably bad practice but it'll do for now
    symbol=""
    name=""
    
    if n_clicks != button_clicks:
        symbol = sym_input
        name = searchq
        button_clicks = n_clicks
    else:
        symbol = 'RELIANCE' if not dropdown else dropdown
        name = stocks[stocks['Symbol']==symbol]['Company Name'].iloc[0]

    return get_graphs(symbol, name)

def get_graphs(symbol, name):
    stock = None
    if symbol is not None:
        stock = stocks[stocks['Symbol'].str.contains(symbol)].iloc[0]
    else:
        stock = stocks[stocks['Company Name'].str.contains(name)].iloc[0]
    symbol = stock['Symbol']
    name = stock['Company Name']
    
    data_df = pd.read_csv(os.path.join(STOCKS_DIR, "%s/full.csv"%symbol))
    latest = data_df.iloc[-1]
    latest_df = pd.read_csv(os.path.join(STOCKS_DIR, "%s/%s.csv"%(symbol,latest['Date'])))
    print(latest_df)
    stock = Stock(symbol, name, sentiment=latest_df, ticker=True)
    print("Passed")
    df = stock.getStockData()
    print("Passed")
    sentiments = stock.getSentiment()
    print("Passed")
    stock_fig = stock_graph(df, symbol, data_df)
    avg_sentiment_fig = avg_sentiment_graph(stock.avg_score, data_df.iloc[-2]['Score'])

    return stock_fig, avg_sentiment_fig, latest_df.drop('description', axis=1).to_dict('records')

def stock_graph(df, symbol, data_df):
    x=data_df['Date']

    df = df.loc[x]

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

    fig.add_trace(go.Scatter(x=x, y=df['Close'],
                        mode='lines',
                        name='Close'), secondary_y=True)

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

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
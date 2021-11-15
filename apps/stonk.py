"""
 Created on Sun Sep 06 2020 19:30:34

 @author: Derpimort
"""


import os
import dash
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from finsent.data_helpers import StonkData
from finsent.plot_helpers import StonkPlots

from finsent.stock import Stock

# Data dir containing stock list and preprocessed data
from finsent.constants import DATA_DIR, STOCKS_DIR

from app import app

stonk_helper = StonkData(data_dir=DATA_DIR, stonks_dir=STOCKS_DIR, use_sqlite=True)
stonk_plot_helper = StonkPlots(*stonk_helper.get_df())


# Dashboard components layout
layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='stonk-filter-stocks',
                    options=stonk_helper.get_stonks_dict(),
                    multi=False,
                    value=stonk_helper.symbol,
                    placeholder="Select Stock"
                )
            ], className="six columns"),
            html.Div([
                html.Button("Show me Da Powaa!", id='stonk-filter-submit', n_clicks=0, className="submit-button"),
            ], className="six columns")
        ], className="row"),
    ], className="navbar top-border"),
    html.Div([
        html.Div([
            html.H2("Stock Chart"),
            dcc.Loading([
                html.Div([
                    dcc.Graph(id="stock-line-chart", 
                    #figure=stonk_plot_helper.empty_plot(),
                    figure=stonk_plot_helper.get_stock_chart(),
                    )           
                ])
            ])
        ], className="eight columns graph-section"),
        html.Div([
            html.H2("Sentiment Guage"),
            dcc.Loading([
                html.Div([
                    dcc.Graph(id="sentiment-guage-chart", 
                    #figure=stonk_plot_helper.empty_plot(),
                    figure=stonk_plot_helper.get_sentiment_guage(),
                    )           
                ])
            ])
        ], className="four columns graph-section"),
    ], className="row m-4 mt-16"),
    html.Div([
            html.H2("Top Influential Articles "),
            stonk_plot_helper.generate_stock_header(),
            dcc.Loading([
                html.Div(
                    stonk_plot_helper.get_stock_rows(stonk_helper.latest_df)
                , id="stonk-data-table")
            ]),
    ], className="top-border left-border right-border graph-section m-4 mt-16 mb-16", id="stonk-data-container", )
])


@app.callback(
    [Output('stock-line-chart', 'figure'),
    Output('sentiment-guage-chart', 'figure'),
    Output('stonk-data-table', 'children')],
    [Input('stonk-filter-submit', 'n_clicks')],
    [State('stonk-filter-stocks', 'value')])
def update_charts(n_clicks, dropdown):
    if n_clicks==0 or dropdown is None:
        raise PreventUpdate("Invalid selection")

    stonk_plot_helper.update_instance(
        *stonk_helper.get_df(symbol=dropdown)
    )

    return (
        stonk_plot_helper.get_stock_chart(), 
        stonk_plot_helper.get_sentiment_guage(),
        stonk_plot_helper.get_stock_rows(stonk_helper.latest_df)
    )

if __name__ == '__main__':
    app.layout = layout
    # host 0.0.0.0 for docker
    app.run_server(host='0.0.0.0', debug=True)

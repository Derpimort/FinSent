"""
 Created on Sun Sep 06 2020 19:47:32

 @author: Derpimort
"""


import os
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from finsent.constants import DATA_DIR, STOCKS_DIR, DAILY_COLUMNS

from app import app
from finsent.data_helpers import DailyData
from finsent.plot_helpers import DailyPlots
from static_elements import generate_daily_stock_header


daily_helper = DailyData(data_dir=DATA_DIR, stonks_dir=STOCKS_DIR)
daily_plot_helper = DailyPlots(daily_helper.df)

layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                #html.P("Select Date"),
                dcc.Dropdown(
                    id='daily-filter-date',
                    options=[{'value': i, 'label':i} for i in daily_helper.get_dates()],
                    placeholder="Select Comparison Date"
                )
            ], className="six columns"),
            html.Div([
                #html.P("Select Stocks (Upto 10)"),
                dcc.Dropdown(
                    id='daily-filter-stocks',
                    options=daily_helper.get_stonks_dict(),
                    multi=True,
                    placeholder="Select Stocks (upto 10)"
                )
            ], className="six columns"),
        ], className="row"),
        html.Div([
            html.Div([
                html.Button("Show me Da Powaa!", id='daily-filter-submit', n_clicks=0),
            ], className="twelve columns")
        ], className="row")
    ], className="navbar top-border"),
    html.Div([
        dcc.Loading([
            html.Div([
                dcc.Graph(id="delta-bar-chart", figure=daily_plot_helper.empty_plot())           
            ])
        ])
    ], className="top-border left-border right-border"),
    html.Div([
            html.H2("Stock data"),
            generate_daily_stock_header(),
    ], className="top-border left-border right-border", id="stock-data-container", )
])

@app.callback(
    Output('delta-bar-chart', 'figure'),
    [Input('daily-filter-submit', 'n_clicks')],
    [State('daily-filter-stocks', 'value'),
    State('daily-filter-date', 'value')])
def update_charts(n_clicks, dropdown, daterange):
    if n_clicks==0 or dropdown is None or daterange is None or len(dropdown)>10:
        raise PreventUpdate("Invalid selection")
    df = daily_helper.get_df(*daterange.split(" -> "))
    daily_plot_helper.update_instance(df, dropdown)

    return daily_plot_helper.get_delta_bar()

@app.callback(
    Output("daily-filter-stocks", "options"),
    Input("daily-filter-date", "value")
)
def update_stocks(daterange):
    if daterange is None:
        raise PreventUpdate("Date range not selected")
    daily_helper.get_df(*daterange.split(" -> "))
    
    return daily_helper.get_stonks_dict()

if __name__ == '__main__':
    app.layout = layout
    app.run_server(host='0.0.0.0', debug=True, port=8051)

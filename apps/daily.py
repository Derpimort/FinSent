"""
 Created on Sun Sep 06 2020 19:47:32

 @author: Derpimort
"""


import os
import dash
from dash.dependencies import Input, Output
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


daily_helper = DailyData(data_dir=DATA_DIR, stonks_dir=STOCKS_DIR)
daily_plot_helper = DailyPlots(daily_helper.df)

layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                #html.P("Select Stocks (Upto 10)"),
                dcc.Dropdown(
                    id='daily-filter-stocks',
                    options=[{'value': i, 'label':i} for i in daily_helper.get_stonks()],
                    multi=True,
                    placeholder="Select Stocks (upto 10)"
                )
            ], className="six columns"),
            html.Div([
                #html.P("Select Date"),
                dcc.Dropdown(
                    id='daily-filter-date',
                    options=[{'value': i, 'label':i} for i in daily_helper.get_dates()],
                    placeholder="Select Comparison Date"
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
        dcc.Graph(id="delta-bar-chart", figure=daily_plot_helper.empty_plot(title="Delta Bar Chart"))
    ])
])


if __name__ == '__main__':
    app.layout = layout
    app.run_server(host='0.0.0.0', debug=True, port=8051)

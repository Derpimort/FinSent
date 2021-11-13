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
from finsent.data_helpers import StonkData

from finsent.stock import Stock

# Data dir containing stock list and preprocessed data
from finsent.constants import DATA_DIR, STOCKS_DIR

from app import app

stonk_helper = StonkData(data_dir=DATA_DIR, stonks_dir=STOCKS_DIR)

# Dashboard components layout
layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='stonk-filter-stocks',
                    options=stonk_helper.get_stonks_dict(),
                    multi=False,
                    placeholder="Select Stock"
                )
            ], className="six columns"),
            html.Div([
                html.Button("Show me Da Powaa!", id='stonk-filter-submit', n_clicks=0, className="submit-button"),
            ], className="six columns")
        ], className="row"),
    ], className="navbar top-border"),
])


if __name__ == '__main__':
    app.layout = layout
    # host 0.0.0.0 for docker
    app.run_server(host='0.0.0.0', debug=True)

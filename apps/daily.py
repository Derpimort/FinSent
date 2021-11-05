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
from finsent import data_helpers
from finsent.constants import DATA_DIR, STOCKS_DIR, DAILY_COLUMNS

from app import app
from finsent.data_helpers import DailyData
from finsent.plot_helpers import DailyPlots


daily_helper = DailyData(data_dir=DATA_DIR, stonks_dir=STOCKS_DIR)
daily_plot_helper = DailyPlots(daily_helper.df)

layout = html.Div([
])


if __name__ == '__main__':
    app.layout = layout
    app.run_server(host='0.0.0.0', debug=True, port=8051)

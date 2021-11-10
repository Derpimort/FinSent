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

from finsent.stock import Stock

# Data dir containing stock list and preprocessed data
from finsent.constants import DATA_DIR, STOCKS_DIR

from app import app


# Dashboard components layout
layout = html.Div(children=[])


if __name__ == '__main__':
    app.layout = layout
    # host 0.0.0.0 for docker
    app.run_server(host='0.0.0.0', debug=True)

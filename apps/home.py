import os
import dash
import dash_core_components as dcc
import dash_html_components as html

from app import app

layout = html.Div( 
    [
    dcc.Link("Daily report", href="/daily"),
    html.P("--- OR ---"),
    dcc.Link("Individual stock analysis", href="/stonk")
    ],
    style={"height":"100vh", "padding-top":"50px", "text-align":"center"}
)
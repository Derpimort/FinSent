import os
import dash
import dash_core_components as dcc
import dash_html_components as html

from app import app

layout = html.Div(
    [
        dcc.Link("Daily report", href="/daily", className="button"),
        html.P("--- OR ---", style={"margin": "20px"}),
        dcc.Link("Individual stock analysis",
                 href="/stonk", className="button")
    ],
    className="dark-container"
)

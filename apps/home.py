import os
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from app import app

layout = dbc.Container( 
    [
        dbc.Row(
            dbc.Col(
                [
                dbc.Button(dcc.Link("Daily report", href="/daily")),
                html.P("--- OR ---"),
                dbc.Button(dcc.Link("Individual stock analysis", href="/stonk"))
                ],
                width="auto",
                align="center",
                style={"height": "100%"},
            ),
            justify="center",
            align="center",
            className="h-75"
    )
    ],
    style={"height":"100vh", "padding-top":"50px"}
)
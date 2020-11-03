import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import home, stonk, daily

# Epic guy -> https://codepen.io/scanfcode/pen/MEZPNd
footer = html.Footer([
            html.Div([
                html.Div([
                    html.H6("By Derpimort")
                ], className="row center"),
                html.Hr(),
                html.Div([
                    html.H6("FinBERT Links")
                ], className="row center")
            ], className="container")
        ], className="site-footer")

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content'),
    footer
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/daily':
        return daily.layout
    elif pathname == '/stonk':
        return stonk.layout
    else:
        return home.layout

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=8050)
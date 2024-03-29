import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import home, stonk, daily

from static_elements import footer, header

server = app.server


app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Header(id="header", className="site-header"),
    html.Div(id='page-content'),
    footer
])


@app.callback([Output('page-content', 'children'),
                Output('header', 'children'),],
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/daily':
        return daily.layout, header("daily")
    elif pathname == '/stonk':
        return stonk.layout, header("stonk")
    else:
        return home.layout, header()


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=8050)

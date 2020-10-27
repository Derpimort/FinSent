import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import stonk, daily


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/daily':
        return daily.layout
    elif pathname == '/stonk':
        return stonk.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=8050)
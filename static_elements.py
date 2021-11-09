import dash_core_components as dcc
import dash_html_components as html
from app import app
from finsent.constants import DAILY_COLUMNS

HEADERS = {
    "home":("FinSent", "A plotly-dash based stock financial sentiment analysis dashboard"),
    "daily":("Daily Report", "Analyze average sentiment scores & its changes across time for multiple stocks"),
    "stonk":("Individual Stock", "An in-depth analysis of stock performance & it's sentiments across time with all affecting factors detailed"),
    
}

LOGO = app.get_asset_url('Spacebar_logo_circle.png')

# Epic guy -> https://codepen.io/scanfcode/pen/MEZPNd
footer = html.Footer([
    html.Div([
        html.Div([
            html.H6("By Derpimort"),
            html.Ul([
                html.Li(
                    html.A(
                        html.I(className="fa fa-github"),
                        href="https://github.com/Derpimort",
                        target="_blank",
                        className="github"
                    )
                ),
                html.Li(
                    html.A(
                        html.I(className="fa fa-linkedin"),
                        href="https://www.linkedin.com/in/derpimort/",
                        target="_blank",
                        className="linkedin"
                    )
                )
            ], className="social-icons")
        ], className="row center"),
        html.Hr(),
        html.Div([
            html.H6("FinBERT"),
            html.Ul([
                html.Li(
                    html.A(
                        html.I(className="fa fa-github"),
                        href="https://github.com/ProsusAI/finBERT",
                        target="_blank",
                        className="github"
                    )
                )], className="social-icons")
        ], className="row center")
    ], className="container")
], className="site-footer")


def header(page="home"):
    heading, info = HEADERS[page]
    return html.Div([
            html.Div([
                html.Img(src=LOGO),
            ], className="oneh columns"),
            html.Div([
                html.Div([
                    html.H1(heading),
                ], className="row left"),
                html.Hr(),
                html.Div([
                    html.H4(info),
                ], className="row left")
            ], className="ten columns")
        ], className="row")


# From https://github.com/dkrizman/dash-manufacture-spc-dashboard
def generate_daily_stock_row(id, style, col1, col2, col3, col4, col5, col6):
    if style is None:
        style = {
            'height': '100px',
            'width': '100%',
        }
    return html.Div(
        id=id,
        className='row metric-row',
        style=style,
        children=[
            html.Div(
                id=col1['id'],
                style={
                    'text-align': 'center',
                    'font-weight': 'bold'
                },
                className='one columns',
                children=col1['children']
            ),
            html.Div(
                id=col2['id'],
                style={'textAlign': 'center'},
                className='two columns',
                children=col2['children']
            ),
            html.Div(
                id=col3['id'],
                style={
                    'height': '100%',
                },
                className='three columns',
                children=col3['children']
            ),
            html.Div(
                id=col4['id'],
                style={},
                className='one columns',
                children=col4['children']
            ),
            html.Div(
                id=col5['id'],
                style={
                    'height': '100%',

                },
                className='three columns',
                children=col5['children']
            ),
            html.Div(
                id=col6['id'],
                style={
                    'display': 'flex',
                    'justifyContent': 'center'
                },
                className='one columns',
                children=col6['children']
            )
        ]
    )

def generate_daily_stock_header():
    cols = DAILY_COLUMNS
    return generate_daily_stock_row(
        'daily-stock-data-table-header',
        {

            'margin': '10px 0px',
            'textAlign': 'center'
        },
        *[{
            'id': "m_header_%s"%i,
            'children': html.Div(cols[i])
        } for i in range(len(cols))])
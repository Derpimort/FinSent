import dash_core_components as dcc
import dash_html_components as html
from app import app

HEADERS = {
    "home":("FinSent", "A plotly-dash based stock financial sentiment analysis dashboard"),
    "daily":("Daily Report", "Analyze average sentiment scores & it's changes across time for multiple stocks"),
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

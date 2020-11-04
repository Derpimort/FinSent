import dash_core_components as dcc
import dash_html_components as html

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

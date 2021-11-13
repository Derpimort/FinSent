"""
 Created on Sun Sep 06 2020 19:47:32

 @author: Derpimort
"""

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from finsent.constants import DATA_DIR, STOCKS_DIR, DAILY_COLUMNS

from app import app
from finsent.data_helpers import DailyData
from finsent.plot_helpers import DailyPlots
from static_elements import generate_daily_stock_header


daily_helper = DailyData(data_dir=DATA_DIR, stonks_dir=STOCKS_DIR)
daily_plot_helper = DailyPlots(daily_helper.df)

layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                #html.P("Select Date"),
                dcc.Dropdown(
                    id='daily-filter-date',
                    options=[{'value': i, 'label':i} for i in daily_helper.get_dates()],
                    placeholder="Select Comparison Date"
                )
            ], className="six columns"),
            html.Div([
                #html.P("Select Stocks (Upto 10)"),
                dcc.Dropdown(
                    id='daily-filter-stocks',
                    options=daily_helper.get_stonks_dict(),
                    multi=True,
                    placeholder="Select Stocks (upto 10)"
                )
            ], className="six columns"),
        ], className="row"),
        html.Div([
            html.Div([
                html.Button("Show me Da Powaa!", id='daily-filter-submit', n_clicks=0, className="submit-button mt-16"),
            ], className="twelve columns")
        ], className="row")
    ], className="navbar top-border"),
    html.Div([
        html.Div([
            html.H2("Delta Chart"),
            dcc.Loading([
                html.Div([
                    dcc.Graph(id="delta-bar-chart", figure=daily_plot_helper.empty_plot())           
                ])
            ])
        ], className="six columns graph-section"),
        html.Div([
            html.H2("Scatter 3D"),
            dcc.Loading([
                html.Div([
                    dcc.Graph(id="scatter-3d-chart", figure=daily_plot_helper.empty_plot())           
                ])
            ])
        ], className="six columns graph-section"),
    ], className="row m-4 mt-16"),
    html.Div([
            html.H2("Stock data"),
            generate_daily_stock_header(),
            dcc.Loading([
                html.Div([
                    dcc.Graph(figure=daily_plot_helper.empty_plot()) 
                ], id="daily-stock-data-table")
            ]),
    ], className="top-border left-border right-border graph-section m-4 mt-16 mb-16", id="daily-stock-data-container", )
])

@app.callback(
    [Output('delta-bar-chart', 'figure'),
    Output('daily-stock-data-table', 'children'),
    Output('scatter-3d-chart', 'figure')],
    [Input('daily-filter-submit', 'n_clicks')],
    [State('daily-filter-stocks', 'value'),
    State('daily-filter-date', 'value')])
def update_charts(n_clicks, dropdown, daterange):
    if n_clicks==0 or dropdown is None or daterange is None or len(dropdown)>10:
        raise PreventUpdate("Invalid selection")
    df = daily_helper.get_df(*daterange.split(" -> "))
    daily_plot_helper.update_instance(df, dropdown)

    return (
        daily_plot_helper.get_delta_bar(), 
        daily_plot_helper.get_stock_rows(), 
        daily_plot_helper.get_scatter_3d()
    )

@app.callback(
    Output("daily-filter-stocks", "options"),
    Input("daily-filter-date", "value")
)
def update_stocks(daterange):
    if daterange is None:
        raise PreventUpdate("Date range not selected")
    daily_helper.get_df(*daterange.split(" -> "))
    
    return daily_helper.get_stonks_dict()

if __name__ == '__main__':
    app.layout = layout
    app.run_server(host='0.0.0.0', debug=True, port=8051)

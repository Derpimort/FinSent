"""
 Created on Sun Sep 06 2020 19:47:32

 @author: Derpimort
"""


import os
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from finsent.constants import DATA_DIR, STOCKS_DIR

def get_df(df, prev_df=None):
    """ Return df with delta metrics if prev_df is not None """
    df = pd.read_csv(os.path.join(STOCKS_DIR, "%s.csv"%df))

    if prev_df:
        prev_df = pd.read_csv(os.path.join(STOCKS_DIR, "%s.csv"%prev_df))

        # Get stock industries
        stocks = pd.read_csv(DATA_DIR+"ind_nifty500list.csv")
        df = stocks[['Symbol','Industry']].merge(df, on="Symbol")

        # Compare last 2 scores to get delta
        df = df.merge(prev_df.set_index('Symbol')['avg_sentiment_score'], on='Symbol')
        df['delta'] = ((df['avg_sentiment_score_x']-df['avg_sentiment_score_y'])/df['avg_sentiment_score_x'])*100
        df=df.drop('avg_sentiment_score_y', axis=1)
        df['delta_status'] = df['delta'].apply(lambda x: 'Increased' if x>0 else 'Stable' if x==0 else 'Decreased')
    
    return df

def empty_plot(label_annotation):
    '''
    Returns an empty plot with a centered text.
    '''

    trace1 = go.Scatter(
        x=[],
        y=[]
    )

    data = [trace1]

    layout = go.Layout(
        showlegend=False,
        xaxis=dict(
            autorange=True,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False
        ),
        yaxis=dict(
            autorange=True,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False
        ),
        annotations=[
            dict(
                x=0,
                y=0,
                xref='x',
                yref='y',
                text=label_annotation,
                showarrow=True,
                arrowhead=7,
                ax=0,
                ay=0
            )
        ]
    )

    fig = go.Figure(data=data, layout=layout)
    # END
    return fig

# Get all data files
dfs = []
for file in os.listdir(STOCKS_DIR):
    if file.endswith("csv"):
        dfs.append(file.split(".")[0])
dfs.sort()
dfs_pd = pd.to_datetime(dfs).astype(np.int64)
df = None

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Bar chart depicting stock sentiment delta
colors = {
    'Increased':"#55a868",
    'Decreased':"#c44e52",
    'Stable': "#000000"
}
fig = empty_plot("Delta bar chart")

if len(dfs) == 0 :
    print("No csv files found, Please run main.py atleast once before running dashboards")
    exit(0)
elif len(dfs) < 2:
    print("Only one csv found, delta metrics won't be available")
    df = get_df(dfs[-1])
else:
    df = get_df(dfs[-1], dfs[-2])
    fig = px.bar(df, y='Symbol', x='delta', color='delta_status', orientation='h', color_discrete_map=colors)


app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
    ),
    html.Div([
        dcc.Slider(
            id='date-slider',
            min=dfs_pd.min(),
            max=dfs_pd.max(),
            value=dfs_pd.max(),
            marks={(i):{'label': pd.to_datetime(i).strftime('%d-%m'), "style": {"transform": "rotate(45deg)"}} for i in dfs_pd[1::(len(dfs_pd)//20)+1]},
            step=None
        )
    ]),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Div(id='datatable-interactivity-container'),
    html.Div([
        dcc.Graph(figure=fig)
    ])
])

@app.callback(
    Output('datatable-interactivity', 'data'),
    [Input('date-slider', 'value')]
)
def update_table(selected_date):
    """ Update dashboard according to selected date """
    selected_date = str(pd.to_datetime(selected_date).date())
    selected_index = dfs.index(selected_date)
    df = get_df(dfs[selected_index], dfs[selected_index-1])
    return df.to_dict('records')

@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    [Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncrasy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]
    graphs = []
    index = 0
    N_COLS = 6
    N_COLS_str = "two" # 12//N_COLS
    current_row=[]
    # ["Industry", "negative", "neutral", "positive", "articles", "avg_sentiment_score_x", 'delta']
    for column in ["negative", "neutral", "positive", "articles", "avg_sentiment_score_x", 'delta']:
        if column in dff:
            if index%N_COLS==0 and index!=0:
                row = html.Div(current_row[index-N_COLS:index], className="row")
                graphs.append(row)
            
            current_row.append(
                html.Div([
                    dcc.Graph(
                        id=column,
                        figure={
                            "data": [
                                {
                                    "x": dff["Symbol"],
                                    "y": dff[column],
                                    "type": "bar",
                                    "marker": {"color": colors},
                                }
                            ],
                            "layout": {
                                "xaxis": {"automargin": True},
                                "yaxis": {
                                    "automargin": True,
                                    "title": {"text": column}
                                },
                                "height": 250,
                                "margin": {"t": 10, "l": 10, "r": 10},
                            },
                        },
                    )
                ], className="%s columns"%N_COLS_str)
                
            )
            index+=1
    if not graphs:
        row = html.Div(current_row[index-N_COLS:index], className="row")
        graphs.append(row)
    return graphs



if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=8051)

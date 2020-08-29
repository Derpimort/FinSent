import os
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from constants import DATA_DIR

# Read main csv
date = pd.to_datetime('today')
csv_path=DATA_DIR+"Stonks/%s.csv"%date.date()
while not os.path.exists(csv_path):
    inp=input("Data not found for %s use data from previous date[y/n]?"%date.date())
    if inp=="y":
        date = date - pd.DateOffset(days=1)
        csv_path=DATA_DIR+"Stonks/%s.csv"%date.date()
    else:
        exit(0)
df = pd.read_csv(csv_path)

# Read prev date csv
date = date - pd.DateOffset(days=1)
csv_path=DATA_DIR+"Stonks/%s.csv"%date.date()
while not os.path.exists(csv_path):
    inp = input("Data not found for %s use data from previous date[y/n]?"%date.date())
    if inp=="y":
        date = date - pd.DateOffset(days=1)
        csv_path = DATA_DIR+"Stonks/%s.csv"%date.date()
    else:
        exit(0)
prev_df = pd.read_csv(csv_path)
df = df.merge(prev_df.set_index('Symbol')['avg_sentiment_score'], on='Symbol')
df['delta'] = ((df['avg_sentiment_score_x']-df['avg_sentiment_score_y'])/df['avg_sentiment_score_x'])*100
df=df.drop('avg_sentiment_score_y', axis=1)
df['delta_status'] = df['delta'].apply(lambda x: 'Increased' if x>0 else 'Stable' if x==0 else 'Decreased')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'Increased':"#55a868",
    'Decreased':"#c44e52",
    'Stable': "#000000"
}
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
    html.Div(id='datatable-interactivity-container'),
    html.Div([
        dcc.Graph(figure=fig)
    ])
])

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

    return [
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
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ["negative", "neutral", "positive", "articles", "avg_sentiment_score_x", 'delta'] if column in dff
    ]



if __name__ == '__main__':
    app.run_server(debug=True)
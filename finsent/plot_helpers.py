import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from finsent.constants import ALL_COLUMNS
from static_elements import generate_daily_stock_row
import dash_daq as daq
import dash_html_components as html

DEFAULT_STONKS = ["ADANIPOWER", "INFY", "RELIANCE", "TCS"]

class BasePlots:
    def __init__(self, template='plotly_dark', colorscale='Bluered'):
        self.template = template
        self.colorscale = colorscale
        self.table_col_classes = {i: ['two columns'] for i in range(6)}

    def _transparent_fig(self, fig, colorscale=False, **kwargs):
        fig.update_layout(template=self.template,
                            margin={"r":0,"t":0,"l":0,"b":0},
                            plot_bgcolor="rgba(0, 0, 0, 0)",
                            paper_bgcolor="rgba(0, 0, 0, 0)",
                            geo_bgcolor="rgba(0, 0, 0, 0)",
                            **kwargs)
        if not colorscale:
            fig.update(layout_coloraxis_showscale=False)
        return fig
    
    def empty_plot(self, label_annotation="Please select some data"):
        """
        Returns an empty plot with a centered text.
        """
        fig = go.Figure()
        fig.update_layout(
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": label_annotation,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28,
                        "color": "#ae966d"
                    }
                }
            ]
        )
        # END
        return self._transparent_fig(fig)
    
    def get_sentiment_bar(self, value, id):
        def scale(value):
            return (value+1)*10
        return daq.GraduatedBar(
                    id=id,
                    color={"gradient": True, "ranges": {"red": [0, 7], "yellow": [7, 13], "green": [13, 20]}},
                    showCurrentValue=True,
                    max=20,
                    value=scale(value)
                )
    
    def get_status_indicator(self, value, id):
        def get_color(value):
            if value < 0:
                value = -1
            elif value > 0:
                value = 1
            else:
                value = 0
            colors = {
                1: "#00FF00",
                0: "#FFFF00",
                -1:"#FF0000"
            }
            return colors[value]

        return daq.Indicator(
                id=id,
                value=True,
                color=get_color(value)
            )
    # From https://github.com/dkrizman/dash-manufacture-spc-dashboard
    def generate_stock_row(self, id, style, *args):
        if style is None:
            style = {
                'height': '100px',
                'width': '100%',
                'align-items': 'center'
            }
        assert len(args)>=1, "Need atleast one column to generate row"
        return html.Div(
            id=id,
            className='row metric-row',
            style=style,
            children=[
                html.Div(
                    id=args[0]['id'],
                    style={
                        'text-align': 'center',
                        'font-weight': 'bold',
                        'display': 'flex',
                        'justifyContent': 'center',
                    },
                    className=" ".join(self.table_col_classes[0]),
                    children=args[0]['children']
                ),
            ]+
            [html.Div(
                    id=args[i]['id'],
                    style={
                        'textAlign': 'center',
                        'display': 'flex',
                        'justifyContent': 'center',},
                    className=" ".join(self.table_col_classes[i]),
                    children=args[i]['children']
            ) for i in range(1, len(args))]
        )

class DailyPlots(BasePlots):
    def __init__(self, df, stonks=DEFAULT_STONKS):
        super().__init__()
        self.update_instance(df, stonks)
        self.table_col_classes = {
            0:['one columns'],
            1:['two columns'],
            2:['three columns'],
            3:['one columns'],
            4:['three columns'],
            5:['one columns'],
        }

    def update_instance(self, df, stonks):
        req_cols = ALL_COLUMNS

        # Filter 
        self.df = df[req_cols].copy()
        self.df = self.df[self.df['Symbol'].isin(stonks)]

    def generate_stock_header(self):
        cols = DAILY_COLUMNS_HEADER
        return self.generate_stock_row(
            'daily-stock-data-table-header',
            {

                'margin': '10px 0px',
                'textAlign': 'center'
            },
            *[{
                'id': "m_header_%s"%i,
                'children': html.Div(cols[i])
            } for i in range(len(cols))])
    
    def get_delta_bar(self):
        colors = {
            'Increased': "#55a868",
            'Decreased': "#c44e52",
            'Stable': "#000000"
        }
        
        fig = px.bar(self.df,
                        y='Symbol',
                        x='Delta',
                        color='Delta Status',
                        color_discrete_map=colors,
                        template=self.template)

        fig.update_yaxes(categoryorder="total ascending", showticklabels=False, title="")

        return self._transparent_fig(fig, showlegend=False)
    
    def get_scatter_3d(self):
        fig = px.scatter_3d(self.df, 
                            x="Positive", 
                            y="Negative", 
                            z="Neutral",
                            size="Articles", 
                            color="Sentiment", 
                            hover_name="Symbol", 
                            size_max=60, 
                            template=self.template
                        )
        
        return self._transparent_fig(fig, colorscale=True)

    
    def get_sentiment_bar(self, value, id):
        def scale(value):
            return (value+1)*10
        return daq.GraduatedBar(
                    id=id,
                    color={"gradient": True, "ranges": {"red": [0, 7], "yellow": [7, 13], "green": [13, 20]}},
                    showCurrentValue=True,
                    max=20,
                    value=scale(value)
                )
    
    def get_delta_status_indicator(self, value, id):
        def get_color(value):
            colors = {
                "Increased": "#00FF00",
                "Stable": "#FFFF00",
                "Decreased":"#FF0000"
            }
            return colors[value]

        return daq.Indicator(
                id=id,
                value=True,
                color=get_color(value)
            )

    def get_stock_rows(self, prefix="daily-stock-data-table-row"):
        rows = []
        for index, data in self.df.iterrows():
            rows.append(
                self.generate_stock_row(
                    prefix+"-%.2d"%index,
                    None,
                    {
                        'id': prefix+"-symbol-%.2d"%index,
                        'children': data.Symbol
                    },
                    {
                        'id': prefix+"-industry-%.2d"%index,
                        'children': data.Industry
                    },
                    {
                        'id': prefix+"-sentiment-%.2d_container"%index,
                        'children': self.get_sentiment_bar(data.Sentiment, prefix+"-sentiment-%.2d"%index)
                    },
                    {
                        'id': prefix+"-articles-%.2d"%index,
                        'children': data.Articles
                    },
                    {
                        'id': prefix+"-delta-%.2d"%index,
                        'children': data.Delta
                    },
                    {
                        'id': prefix+"-delta_status-%.2d_container"%index,
                        'children': self.get_status_indicator(data.Delta, prefix+"-delta_status-%.2d"%index)
                    }
                )

            )
        return rows
        
class StonkPlots(BasePlots):
    def __init__(self, stonk, df):
        super().__init__()
        self.update_instance(stonk, df)

    def update_instance(self, stonk, df):
        self.df = df
        self.stonk = stonk

        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df = self.df.join(self.stonk.getStockData()['Close'], on='Date')

    def get_stock_chart(self):
        x = self.df['Date'].dt.date

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Scatter(
            x=x, y=self.df['positive'],
            mode='lines',
            line=dict(width=2, color='#00cc96'),
            stackgroup='one',
            name="positive",
            groupnorm='percent'  # sets the normalization for the sum of the stackgroup
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=x, y=self.df['neutral'],
            mode='lines',
            line=dict(width=2, color='#efaf3b'),
            stackgroup='one',
            name='neutral'
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=x, y=self.df['negative'],
            mode='lines',
            line=dict(width=2, color='#EF553B'),
            stackgroup='one',
            name='negative'
        ), secondary_y=False)

        fig.add_trace(go.Scatter(x=x, y=self.df['Close'],
                                    mode='lines+markers',
                                    name='Close',
                                    connectgaps=True), secondary_y=True)

        fig.update_layout(
            showlegend=True,
            xaxis_type='category',
            yaxis=dict(
                type='linear',
                range=[1, 100],
                ticksuffix='%'))

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        return self._transparent_fig(fig)

    def get_sentiment_guage(self):
        avg_sentiment = self.stonk.avg_score
        reference_score = self.df.iloc[-2]['Score']
        fig = go.Figure(go.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=avg_sentiment,
            mode="gauge+number+delta",
            title={'text': "Average Sentiment Score w/ Delta"},
            delta={'reference': reference_score},
            gauge={'axis': {'range': [-1, 1]},
                'bar': {'color': "#f44336" if (avg_sentiment-reference_score)<=0 else "#4878d0"},
                'steps': [
                {'range': [-1, -0.3], 'color': "#ff9f9b"},
                {'range': [-0.3, 0.3], 'color': "#fffea3"},
                {'range': [0.3, 1], 'color': "#8de5a1"}],
                # 'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 490}
            }),
        )

        return self._transparent_fig(fig)

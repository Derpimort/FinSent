import plotly.express as px
import plotly.graph_objects as go

from finsent.constants import ALL_COLUMNS

DEFAULT_STONKS = ["ADANIPOWER", "INFY", "RELIANCE", "TCS"]

class BasePlots:
    def __init__(self, template='plotly_dark', colorscale='Bluered'):
        self.template = template
        self.colorscale = colorscale

    def _transparent_fig(self, fig, colorscale=False, **kwargs):
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                            plot_bgcolor="rgba(0, 0, 0, 0)",
                            paper_bgcolor="rgba(0, 0, 0, 0)",
                            geo_bgcolor="rgba(0, 0, 0, 0)",
                            **kwargs)
        if not colorscale:
            fig.update(layout_coloraxis_showscale=False)
        return fig
    
    def empty_plot(label_annotation):
        """
        Returns an empty plot with a centered text.
        """
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

class DailyPlots(BasePlots):
    def __init__(self, df, stonks=DEFAULT_STONKS):
        super().__init__()
        req_cols = ALL_COLUMNS

        # Filter 
        self.df = df[req_cols].copy()
        #self.df = self.df[self.df['Symbol'].isin(stonks)]
    
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
    

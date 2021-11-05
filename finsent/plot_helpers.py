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

class DailyPlots(BasePlots):
    def __init__(self, df, stonks=DEFAULT_STONKS):
        super().__init__()
        self.update_instance(df, stonks)

    def update_instance(self, df, stonks):
        req_cols = ALL_COLUMNS

        # Filter 
        self.df = df[req_cols].copy()
        self.df = self.df[self.df['Symbol'].isin(stonks)]
    
    def get_delta_bar(self):
        colors = {
            'Increased': "#55a868",
            'Decreased': "#c44e52",
            'Stable': "#000000"
        }
        print(self.df)
        fig = px.bar(self.df,
                        y='Symbol',
                        x='Delta',
                        color='Delta Status',
                        color_discrete_map=colors,
                        template=self.template)

        fig.update_yaxes(categoryorder="total ascending", showticklabels=False, title="")

        return self._transparent_fig(fig, showlegend=False)
    

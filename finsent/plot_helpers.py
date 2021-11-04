import plotly.express as px
import plotly.graph_objects as go

class BasePlots:
    def __init__(self, template='plotly_dark', colorscale='Bluered'):
        self.template = template
        self.colorscale = colorscale

    def _transparent_fig(self, fig, colorscale=False):
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                            plot_bgcolor="rgba(0, 0, 0, 0)",
                            paper_bgcolor="rgba(0, 0, 0, 0)",
                            geo_bgcolor="rgba(0, 0, 0, 0)")
        if not colorscale:
            fig.update(layout_coloraxis_showscale=False)
        return fig   

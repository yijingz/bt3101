import pandas as pd
import plotly.express as px
import plotly
import json


def px_line(df, x, y, width=400, height=300):
    line = px.line(df, x=x, y=y, width=width, height=height)
    line.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="white",
    )
    return line

def px_bar(df, x, y, width=700, height=400, text='', title_text='', color=None):
    fig = px.bar(df, x=x, y=y, width=width, height=height, text=text, color=color)
    fig.update_layout(title_text=title_text)
    return fig


def convert_chart_to_json(px_chart):
    return json.dumps(px_chart, cls=plotly.utils.PlotlyJSONEncoder)
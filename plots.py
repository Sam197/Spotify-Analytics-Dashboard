import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

POLAR_PLOTS_DEFULTS = {
    'hourly': {'dftitle': 'hourly_counts', 'theta': 'hour', 'r': 'count', 'title': "Listens by Hour of Day", 'labels': {'hour': 'Hour of Day', 'count': 'Number of Listens'}},
    'daily_week': {'dftitle': 'daily_counts_week', 'theta': 'day', 'r': 'count', 'title': "Listens by Day of Week", 'labels': {'day': 'Day of Week', 'count': 'Number of Listens'}},
    'daily_month': {'dftitle': 'daily_counts_month', 'theta': 'day', 'r': 'count', 'title': "Listens by Day of Month", 'labels': {'day': 'Day of Month', 'count': 'Number of Listens'}},
    'monthly': {'dftitle': 'monthly_counts', 'theta': 'month', 'r': 'count', 'title': "Listens by Month", 'labels': {'month': 'Month', 'count': 'Number of Listens'}}
}
TEMPLATE = "plotly_dark"
POLAR_BARGAP = 0
MARKER_LINE_WIDTH = 1
MARKER_LINE_COLOR = "black"

def make_polar_plot(df, theta, r, title, labels):
    fig = px.bar_polar(
        df,
        theta=theta,
        r=r,
        title=title,
        labels=labels,
        template=TEMPLATE
    )

    fig.update_layout(
        polar_bargap=POLAR_BARGAP,
        polar=dict(
            radialaxis=dict(showticklabels=False)
        )
    )
    fig.update_traces(marker_line_width=MARKER_LINE_WIDTH, marker_line_color=MARKER_LINE_COLOR)
    return fig

def make_polar_plots(dfs, config=POLAR_PLOTS_DEFULTS):
    plots = {}
    for key, params in config.items():
        df = dfs[params['dftitle']]
        fig = make_polar_plot(
            df,
            theta=params['theta'],
            r=params['r'],
            title=params['title'],
            labels=params['labels']
        )
        plots[key] = fig
    return plots

def plot_polar_plots(plots):
    cols = st.columns(len(plots))
    figs = list(plots.values())
    for i, col in enumerate(cols):
        with col:
            st.plotly_chart(figs[i], width='stretch', key=f'polar_plot_{i}')

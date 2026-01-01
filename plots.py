import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def make_polar_plots(dfs):
    
    fig_hour = px.bar_polar(
        dfs['hourly_counts'],
        theta='hour',
        r='count',
        title="Listens by Hour of Day",
        labels={'hour': 'Hour of Day', 'count': 'Number of Listens'},
        template="plotly_dark"
    )
    fig_hour.update_layout(
        polar_bargap=0,
        polar=dict(
            radialaxis=dict(showticklabels=False),
        )
    )
    fig_hour.update_traces(marker_line_width=1, marker_line_color="black")

    fig_daily_week = px.bar_polar(
        dfs['daily_counts_week'],
        theta='day',
        r='count',
        title="Listens by Day of Week",
        labels={'day': 'Day of Week', 'count': 'Number of Listens'},
        template="plotly_dark"
    )
    fig_daily_week.update_layout(
        polar_bargap=0,
        polar=dict(
            radialaxis=dict(showticklabels=False)
        )
    )
    fig_daily_week.update_traces(marker_line_width=1, marker_line_color="black")

    fig_daily_month = px.bar_polar(
        dfs['daily_counts_month'],
        theta='day',
        r='count',
        title="Listens by Day of Month",
        labels={'day': 'Day of Month', 'count': 'Number of Listens'},
        template="plotly_dark"
    )
    fig_daily_month.update_layout(
        polar_bargap=0,
        polar=dict(
            radialaxis=dict(showticklabels=False)
        )
    )
    fig_daily_month.update_traces(marker_line_width=1, marker_line_color="black")

    fig_monthly = px.bar_polar(
        dfs['monthly_counts'],
        theta='month',
        r='count',
        title="Listens by Month",
        labels={'month': 'Month', 'count': 'Number of Listens'},
        template="plotly_dark"
    )
    fig_monthly.update_layout(
        polar_bargap=0,
        polar=dict(
            radialaxis=dict(showticklabels=False)
        )
    )
    fig_monthly.update_traces(marker_line_width=1, marker_line_color="black")

    return {'hourly': fig_hour, 'daily_week': fig_daily_week, 'daily_month': fig_daily_month, 'monthly': fig_monthly}
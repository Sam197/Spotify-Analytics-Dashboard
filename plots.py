import streamlit as st
import plotly.express as px
from analyticsFuncs import MS_MIN_CONVERSION
import pandas as pd

POLAR_PLOTS_DEFULTS = {
    'hourly_counts': {'dftitle': 'hourly_counts', 'theta': 'hour', 'r': 'count', 'title': "Listens by Hour of Day", 'labels': {'hour': 'Hour of Day', 'count': 'Number of Listens'}},
    'daily_counts_week': {'dftitle': 'daily_counts_week', 'theta': 'day', 'r': 'count', 'title': "Listens by Day of Week", 'labels': {'day': 'Day of Week', 'count': 'Number of Listens'}},
    'daily_counts_month': {'dftitle': 'daily_counts_month', 'theta': 'day', 'r': 'count', 'title': "Listens by Day of Month", 'labels': {'day': 'Day of Month', 'count': 'Number of Listens'}},
    'monthly_counts': {'dftitle': 'monthly_counts', 'theta': 'month', 'r': 'count', 'title': "Listens by Month", 'labels': {'month': 'Month', 'count': 'Number of Listens'}}
}
TEMPLATE = "plotly_dark"
POLAR_BARGAP = 0
MARKER_LINE_WIDTH = 1
MARKER_LINE_COLOR = "black"
FREQ_MAP = {
    "Daily": "D",
    "Weekly": "W",
    "Monthly": "M",
    "Yearly": "Y"
    }
MINUTE_PLOT_LABELS = {'ts': 'Date', 'minutes': 'Minutes Played'}
STREAMS_PLOT_LABELS = {'ts': 'Date', 'streams': 'Number of Streams'}

def line_plot(df, x, y, title, labels):
    fig = px.line(
        df,
        x=x,
        y=y,
        title=title,
        labels=labels,
        template=TEMPLATE
    )
    fig.update_layout(hovermode="x unified")
    return fig

def make_mins_and_streams_plots(df):
        
    selected_label = st.select_slider(
        "Select Time Grain",
        options=["Daily", "Weekly", "Monthly", "Yearly"],
        value="Weekly"
    )
    freq_alias = FREQ_MAP[selected_label]
    resampled_df = df.set_index('ts').resample(freq_alias)['ms_played'].agg(['sum', 'size']).reset_index()
    resampled_df.columns = ['ts', 'ms_played', 'streams']
    resampled_df['minutes'] = resampled_df['ms_played'] / MS_MIN_CONVERSION

    start_data = resampled_df['ts'].iloc[0].date()
    end_data = resampled_df['ts'].iloc[-1].date()
    title = f"Total Minutes Listened ({selected_label}) between {start_data} and {end_data}"
    st.plotly_chart(line_plot(resampled_df, 'ts', 'minutes', title, MINUTE_PLOT_LABELS), width='stretch')

    peak_mins_t = resampled_df['minutes'].idxmax()
    peak_mins_freq = resampled_df['minutes'].max()
    peak_mins_t = resampled_df['ts'].iloc[peak_mins_t].date()
    st.write(f"Peak {selected_label}: {peak_mins_t} with {peak_mins_freq:.2f} mins")

    title = f"Total Streams ({selected_label}) between {start_data} and {end_data}"
    st.plotly_chart(line_plot(resampled_df, 'ts', 'streams', title, STREAMS_PLOT_LABELS), width='stretch')

    track_ts = df['ts'].dt.to_period(freq_alias)
    peak_t = track_ts.value_counts().idxmax()
    peak_t_count = track_ts.value_counts().max()

    st.write(f"Peak {selected_label}: {peak_t} with {peak_t_count} listnes")
    
    corr = resampled_df['minutes'].corr(resampled_df['streams'])
    st.write(f"Correlation between Minutes Played and Number of Streams: {corr:.4f}")

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

def make_polar_plots(data, config=POLAR_PLOTS_DEFULTS):
    plots = {}
    for time_period in data.__dataclass_fields__.keys():
        df = getattr(data, time_period)
        params = config[time_period]
        fig = make_polar_plot(
            df,
            theta=params['theta'],
            r=params['r'],
            title=params['title'],
            labels=params['labels']
        )
        plots[time_period] = fig
    return plots

def plot_polar_plots(plots):
    cols = st.columns(len(plots))
    figs = list(plots.values())
    for i, col in enumerate(cols):
        with col:
            st.plotly_chart(figs[i], width='stretch', key=f'polar_plot_{i}')

#TODO Refactor this into one function - best to do after sorted out the artist top songs top album mismatch
spotify_palette = [
    "#0C7230", '#8D67AB', '#19E3E0', '#E91E63', '#4587F7', 
    '#FF5722', '#00897B', '#F4C430', '#3F51B5', '#607D8B'
]

def make_pie_chart_track(df, max_elements = 10, album=False):
    if album:
        cols = ['Listens', 'Full Listens']
    else:
        cols = ['Listens', 'Full Listens', 'Album']
    df = df.drop(columns=cols)
    tot_mins = df['Total Minutes'].sum()
    df = df.sort_values('Total Minutes', ascending=False)
    if len(df) > max_elements:
        data = df.head(max_elements-1)
        other_row = {'Song': 'Others', 'Total Minutes': (tot_mins-data['Total Minutes'].sum())}
        data = pd.concat([data, pd.DataFrame([other_row])], ignore_index=True)
    else:
        data = df

    fig = px.pie(
        data,
        values = 'Total Minutes',
        names = 'Song',
        title = 'Listening Distribution by Song (by minutes listened to)',
        color_discrete_sequence=spotify_palette
    )
    fig.update_traces(textposition='inside', textinfo='percent+label', sort=False, rotation=0, direction='clockwise')
    return fig

def make_pie_chart_album(df, max_elements = 10):
    df = df.drop(columns=['unique_tracks', 'total_plays', 'plays_no_skips', 'mean_listen_mins', 'skip_percentage'])
    df = df.rename(columns={'album_name': 'Album',
                    'total_minutes': 'Total Minutes'})
    tot_mins = df['Total Minutes'].sum()
    df = df.sort_values('Total Minutes', ascending=False)

    if len(df) > max_elements:
        data = df.head(max_elements-1)
        other_row = {'Album': 'Others', 'Total Minutes': (tot_mins-data['Total Minutes'].sum())}
        data = pd.concat([data, pd.DataFrame([other_row])], ignore_index=True)
    else:
        data = df

    fig = px.pie(
        data,
        values = 'Total Minutes',
        names = 'Album',
        title = f'Listening Distribution by Album (by minutes listened to)',
    )
    fig.update_traces(textposition='inside', textinfo='percent+label', sort=False, rotation=0, direction='clockwise')
    return fig

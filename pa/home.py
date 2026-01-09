import streamlit as st
from utils.session_state import get_data, has_data
from components.filters import get_date_range_filter
from components.metrics import display_basic_stats, display_first_last_play
from components.tables import (
    display_top_songs_section,
    display_top_artists_section,
    display_top_albums_section
)
import analyticsFuncs
import plots

def render():
    if not has_data():
        st.warning("Please upload data first using the Upload page")
        st.stop()

    df = get_data()

    st.title("Whole Listening History Overview")
    st.divider()

    # Date range filter
    filtered_df, start_date, end_date = get_date_range_filter(df)

    # Basic statistics
    basic_stats = analyticsFuncs.basicStats(filtered_df)
    display_basic_stats(basic_stats)

    # First and last play
    first_last_play = analyticsFuncs.firstLastPlay(filtered_df)
    display_first_last_play(first_last_play)

    st.divider()

    # Time-based listening patterns
    st.subheader("When Do You Listen?")
    polar_plot_data = analyticsFuncs.get_data_for_polar_plots(filtered_df)
    polar_plots = plots.make_polar_plots(polar_plot_data)
    plots.plot_polar_plots(polar_plots)

    st.divider()

    # Minutes and streams over time
    st.subheader("Graph - Yippee")
    plots.make_mins_and_streams_plots(filtered_df)

    st.divider()

    # Track analytics
    col1, col2 = st.columns(2)
    with col1:
        st.title("Track Analytics")
    with col2:
        show_uri = st.checkbox("Show URIs?")

    top_songs = analyticsFuncs.top_songs(filtered_df, show_uri=show_uri)
    display_top_songs_section(top_songs, start_date, end_date, show_uri)

    st.divider()

    # Artist analytics
    top_artists = analyticsFuncs.top_artists(filtered_df)
    display_top_artists_section(top_artists, start_date, end_date)

    st.divider()

    # Album analytics
    top_albums = analyticsFuncs.top_albums(filtered_df)
    display_top_albums_section(top_albums, start_date, end_date)
import streamlit as st
from utils.session_state import get_data, has_data, reset_random_selection
from analytics import analytics_funcs
from UI import markdown, plots
import models

def render():
    if not has_data():
        st.warning("Please upload data first using the Upload page")
        st.stop()

    df = get_data()

    st.title("Looking for a Specific Album?")

    search_keyword = st.text_input(
        "Start Searching for an Album",
        placeholder="Enter an Album Name",
        on_change=reset_random_selection
    )

    album_hist = None

    col1, col2 = st.columns(2)

    with col1:
        exact = st.checkbox("Exact Match?")

    with col2:
        if st.button(
            'Surprise Me!',
            help="Choose a random Song that you have listened to to look at! Biased towards number of plays"
        ):
            st.session_state.previous_rand = analytics_funcs.random_play(df)

    # Handle random selection
    if st.session_state.previous_rand:
        _, _, album = st.session_state.previous_rand
        search_keyword = album
        exact = True

    # Search for album
    if search_keyword != "":
        album_hist = analytics_funcs.get_album_hist(df, search_keyword, exact=exact)
        
        if album_hist is not None:
            album_sum_stats = analytics_funcs.artist_album_sum_stats(album_hist, album=True)
            markdown.summary_artist_album_markdown(album_sum_stats, album=True)

    # Show all songs if there are many
    if album_hist is not None and album_sum_stats.unique_songs > models.Config.top_n:
        see_all_songs = st.checkbox(f"See all songs? ({album_sum_stats.unique_songs})")
        if see_all_songs:
            st.dataframe(album_sum_stats.full_hist, hide_index=True)

    # Display visualizations and patterns
    if album_hist is not None:
        # Track pie chart
        st.plotly_chart(
            plots.make_pie_chart_track(album_sum_stats.full_hist, album=True),
            width='stretch'
        )
        
        # Listening patterns over time
        plots.make_mins_and_streams_plots(album_hist)
        
        st.divider()
        st.subheader("When did you listen?")
        st.write(
            f"For the time period {album_hist['ts'].min().date()} "
            f"to {album_hist['ts'].max().date()}"
        )
        time_dfs = analytics_funcs.get_data_for_polar_plots(album_hist)
        polar_plots = plots.make_polar_plots(time_dfs)
        plots.plot_polar_plots(polar_plots)

    # Show full history if requested
    if album_hist is not None:
        if st.checkbox(
            "See Full Listening History for this Album?",
            help="This shows all times a song from this album was listened to, "
                "drawn straight from your raw Spotify data."
        ):
            st.dataframe(album_hist, hide_index=True)
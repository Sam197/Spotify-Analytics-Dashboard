import streamlit as st
from utils.session_state import get_data, has_data, reset_random_selection
import analyticsFuncs
import markdown
import plots
import models

def render():
    if not has_data():
        st.warning("Please upload data first using the Upload page")
        st.stop()

    df = get_data()

    st.title("Looking for a Specific Artist?")

    search_keyword = st.text_input(
        "Start Searching for an Artist",
        placeholder="Enter an Artist's Name",
        on_change=reset_random_selection
    )

    artist_hist = None

    col1, col2 = st.columns(2)

    with col1:
        exact = st.checkbox("Exact Match?")

    with col2:
        if st.button(
            'Surprise Me!',
            help="Choose a random Song that you have listened to to look at! Biased towards number of plays"
        ):
            st.session_state.previous_rand = analyticsFuncs.random_play(df)

    # Handle random selection
    if st.session_state.previous_rand:
        _, artist, _ = st.session_state.previous_rand
        search_keyword = artist
        exact = True

    # Search for artist
    if search_keyword != "":
        artist_hist = analyticsFuncs.get_artist_hist(df, search_keyword, exact=exact)
        
        if artist_hist is not None:
            artist_sum_stats = analyticsFuncs.artist_album_sum_stats(artist_hist, artist=True)
            markdown.summary_artist_album_markdown(artist_sum_stats, artist=True)
            
            # Show all songs if there are many
            if artist_sum_stats.unique_songs > models.Config.top_n:
                see_all_songs = st.checkbox(f"See all songs? ({artist_sum_stats.unique_songs})")
                if see_all_songs:
                    st.dataframe(artist_sum_stats.full_hist, hide_index=True)
            
            # Track pie chart
            st.plotly_chart(
                plots.make_pie_chart_track(artist_sum_stats.full_hist),
                use_container_width=True
            )
            
            # Albums for this artist
            top_albums_for_artist = analyticsFuncs.top_albums(artist_hist, single=True)
            top_albums_for_artist.drop(columns=['artist_name'], inplace=True)
            
            st.subheader("Top Albums for this Artist")
            st.write(f"Top {models.Config.top_n} albums by number of plays")
            st.dataframe(top_albums_for_artist.head(models.Config.top_n), hide_index=True)
            
            if artist_sum_stats.unique_albums > models.Config.top_n:
                see_all_albums = st.checkbox(f"See all albums? ({artist_sum_stats.unique_albums})")
                if see_all_albums:
                    st.dataframe(top_albums_for_artist, hide_index=True)
            
            # Album pie chart
            st.plotly_chart(
                plots.make_pie_chart_album(top_albums_for_artist),
                use_container_width=True
            )
            
            # Listening patterns over time
            plots.make_mins_and_streams_plots(artist_hist)
            
            st.divider()
            st.subheader("When did you listen?")
            st.write(
                f"For the time period {artist_hist['ts'].min().date()} "
                f"to {artist_hist['ts'].max().date()}"
            )
            time_dfs = analyticsFuncs.get_data_for_polar_plots(artist_hist)
            polar_plots = plots.make_polar_plots(time_dfs)
            plots.plot_polar_plots(polar_plots)

    # Show full history if requested
    if artist_hist is not None:
        if st.checkbox(
            "See Full Listening History for this Artist?",
            help="This shows all times a song from this artist was listened to, "
                "drawn straight from your raw Spotify data."
        ):
            st.dataframe(artist_hist, hide_index=True)
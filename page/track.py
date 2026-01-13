import streamlit as st
from utils.session_state import get_data, has_data, reset_random_selection
import analyticsFuncs
import markdown
import plots

def render():
    if not has_data():
        st.warning("Please upload data first using the Upload page")
        st.stop()

    df = get_data()

    st.title("Looking for a Specific Track?")

    search_keyword = st.text_input(
        "Start Searching for a Song",
        placeholder="Enter a Song Title",
        on_change=reset_random_selection
    )

    artist, album = "", ""
    col1, col2, col3, col4 = st.columns(4)
    song_history = None

    with col1:
        exact = st.checkbox(
            "Exact Match?",
            help="Looks for an exact match, your search phrase needs to exactly match what you are looking for"
        )

    with col2:
        artistEntry = st.checkbox(
            "Refine With Artist?",
            help='Add an artist to refine your search. Will return all times this song has been listened to'
        )

    if artistEntry:
        artist = st.text_input("Artist Name", placeholder="Enter Artist Name")

    with col3:
        albumEntry = st.checkbox(
            "Refine With Album?",
            help='Will return all times the song as been listened to as part of the album. '
                'If a song is listened to across different albums, the numbers you see could be different'
        )

    if albumEntry:
        album = st.text_input("Album Name", placeholder="Enter Album Name")

    with col4:
        if st.button(
            'Surprise Me!',
            help="Choose a random Song that you have listened to to look at! Biased towards number of plays"
        ):
            st.session_state.previous_rand = analyticsFuncs.random_play(df)

    # Handle random selection
    if st.session_state.previous_rand:
        track, artist, _ = st.session_state.previous_rand
        search_keyword = track
        exact = True

    # Search for song
    if search_keyword != "":
        song_history = analyticsFuncs.get_song_stats(
            df,
            search_keyword,
            exact=exact,
            artist=artist,
            album=album
        )

    # Display results
    if song_history is not None:
        summary_song_data = analyticsFuncs.song_sum_stats(song_history)
        markdown.summary_song_markdown(summary_song_data)
        
        plots.make_mins_and_streams_plots(song_history)
        
        st.divider()
        st.write("When did you listen?")
        time_dfs = analyticsFuncs.get_data_for_polar_plots(song_history)
        polar_plots = plots.make_polar_plots(time_dfs)
        plots.plot_polar_plots(polar_plots)
        
        if st.checkbox(
            "See Full Listening History for this Song?",
            help="This shows all times this song was listened to, drawn straight from your raw Spotify data."
        ):
            st.dataframe(song_history, hide_index=True)
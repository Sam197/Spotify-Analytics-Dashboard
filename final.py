import streamlit as st
import pandas as pd
import analyticsFuncs, markdown
import plotly.express as px
import plots
import io
import models

UPLOAD_FILES_HELP_TEXT = """
Upload Spotify Data here. You can either upload the JSON files you download from Spotify or
a previously saved Parquet file for faster loading. If you upload JSON files, they will be
processed and you will have the option to save the combined dataset as a Parquet file for future use.
Only JSON and Parquet files are supported.
"""
DOWNLOAD_FILE_HELP_TEXT = """
You can download your current dataset as a Parquet file for faster loading next time.
Simply provide a filename (without extension), hit enter, and click the download button.
"""

st.set_page_config(page_title="Music Analytics", layout="wide", page_icon='logo.jpg')

#st.logo('Data from backscatter.png', size='large')
if 'data' not in st.session_state:
    st.session_state.data = None
    st.session_state.has_inital_data = False
if 'page' not in st.session_state:
    st.session_state.page = 'Upload'
if st.session_state.data is not None:
    st.logo('logo.jpg', size='large')
    st.sidebar.title("Navigate")
    page = st.sidebar.radio("Navigate", ['Upload', 'Home', 'Track', 'Artist', 'Album'])
    st.session_state.page = page
    st.sidebar.markdown("Checkout the [GitHub Repository](https://github.com/Sam197/Spotify-Analytics-Dashboard)!")

if st.session_state.page == 'Upload' or st.session_state.data is None:
    st.title("📊 Spotify Analytics Dashboard")
    if st.session_state.data is None:
        st.markdown("### Upload your data to get started")
    else:
        st.markdown("### Upload different data?")
    
    st.write("Don't know how to get your Spotify data? Request your 'Extended Streaming History' from [Spotify here](https://www.spotify.com/uk/account/privacy/). Once you have the data, upload the JSON files here to get started!")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['json', 'parquet'],
        help=UPLOAD_FILES_HELP_TEXT,
        accept_multiple_files=True
    )

    if uploaded_files is not None and uploaded_files != []:
        if any([file.name.endswith('.parquet') for file in uploaded_files]):
            df = pd.read_parquet(uploaded_files[0])
            
        else:
            alldata = pd.concat([pd.read_json(path) for path in uploaded_files])
            coldrop = ["ip_addr", "episode_show_name", 'audiobook_title', 'audiobook_uri', 'audiobook_chapter_uri', 'audiobook_chapter_title', 'episode_name', 'spotify_episode_uri']
            df = alldata.drop(columns=coldrop)
            df['ts'] = pd.to_datetime(df['ts'])

            uri_mapping = df.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name'])['spotify_track_uri'].first().reset_index()
            df = df.merge(uri_mapping, on=['master_metadata_track_name', 'master_metadata_album_artist_name'], suffixes=('_old', ''))
            df = df.drop(columns=['spotify_track_uri_old'])

        st.session_state.data = df.copy(deep=True)
            
        st.success(f"✅ Successfully loaded {len(df)} rows and {len(df.columns)} columns!")
        
        if not st.session_state.has_inital_data:
            st.write("Loading Landing Page!")
        st.dataframe(st.session_state.data, hide_index=True)
        if not st.session_state.has_inital_data:
            st.session_state.has_inital_data = True
            st.rerun()
    else:
        if not st.session_state.has_inital_data:
            st.info("Please upload .json files, or a .parquet file to begin analysis")
        else:
            st.info("You can analyse different data if you upload new stuff here!")
            st.write("Do you want to save the loaded dataset for quicker uploads next time?")

            buffer = io.BytesIO()
            st.session_state.data.to_parquet(buffer, index=False)

            filename = st.text_input("Enter filename to save as (without extension)", placeholder="my_spotify_data", help=DOWNLOAD_FILE_HELP_TEXT)
            st.download_button(
                "Download Current Dataset",
                data=buffer.getvalue(),
                file_name="my_spotify_data.parquet" if filename == "" else f"{filename}.parquet",
                mime="application/octet-stream"
            )

if st.session_state.page == "Home":
    df = st.session_state.data
    st.title("Tracks")

    min_date = df['ts'].min().date()
    max_date = df['ts'].max().date() + pd.Timedelta('1d')
    col1, col2 = st.columns(2)
    with col1:
        selected_dates = st.date_input(
            "Select Date Range",
            value=[min_date, max_date]
        )
    with col2:
        use_all_history = st.checkbox("Look at all History?")

    if use_all_history:
        start_date, end_date = min_date, max_date
    else:
        start_date, end_date = selected_dates
    start_date = pd.to_datetime(start_date).tz_localize('UTC')
    end_date = pd.to_datetime(end_date).tz_localize('UTC')   
    mask = (df['ts'] >= start_date) & (df['ts'] <= end_date)
    filtered_df = df.loc[mask]

    st.markdown("### Track-Level Analysis")

    
    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    basic_stats = analyticsFuncs.basicStats(filtered_df)
    with col1:
        st.metric("Total Plays", basic_stats.total_plays)
    with col2:
        st.metric("Total Plays No Skips", basic_stats.total_plays_no_skips)
    with col3:
        st.metric("Skip Percentage", f"{(basic_stats.skip_percentage*100):.2f}%")
    with col4:
        st.metric("Total Listening Time", f"{basic_stats.total_minutes:.2f} minutes")

    col1, col2 = st.columns(2)
    first_last_play = analyticsFuncs.firstLastPlay(filtered_df)
    with col1:
        st.markdown(f"## First Listen: {first_last_play.first_play[0].date()}")
        st.write(f"{first_last_play.first_play[1]} by {first_last_play.first_play[2]}")
    with col2:
        st.markdown(f"## Last Listen: {first_last_play.last_play[0].date()}")
        st.write(f"{first_last_play.last_play[1]} by {first_last_play.last_play[2]}")
    st.markdown(f"### Thats {first_last_play.timespan} days apart!")
    st.divider()

    st.subheader("When Do You Listen?")
    polar_plot_data = analyticsFuncs.get_data_for_polar_plots(filtered_df)
    polar_plots = plots.make_polar_plots(polar_plot_data)
    plots.plot_polar_plots(polar_plots)

    st.divider()
    st.subheader("Graph - Yipee")

    plots.make_mins_and_streams_plots(filtered_df)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.title("Track Analytics")
    with col2:
        show_uri = st.checkbox("Show URIs?")
    st.write(f"Encompassing date range from {start_date.date()} to {end_date.date()}")

    top_songs = analyticsFuncs.top_songs(filtered_df, show_uri=show_uri)
    st.write(f"Top {models.Config.top_n} songs by number of plays")
    st.dataframe(top_songs.by_plays, hide_index=True)
    st.write(f"Top {models.Config.top_n} songs with no skips")
    st.dataframe(top_songs.by_no_skips, hide_index=True)
    st.write(f"Top {models.Config.top_n} songs by minutes listened to")
    st.dataframe(top_songs.by_minutes, hide_index=True)
    st.write(f"Top {models.Config.top_n} songs by average listen time")
    st.dataframe(top_songs.by_mean_minutes, hide_index=True)
    st.write(f"Top {models.Config.top_n} songs by lowest skip percentage (where a song has at least {models.Config.min_plays_skip_analysis} plays)")
    st.dataframe(top_songs.lowest_skip, hide_index=True)
    st.write(f"Top {models.Config.top_n} songs by highest skip percentage (where a song has at least {models.Config.min_plays_skip_analysis} plays)")
    st.dataframe(top_songs.highest_skip, hide_index=True)
    st.divider()
    st.write(f"Full song summary statistics for period {start_date.date()} to {end_date.date()}")
    st.dataframe(top_songs.all_data, hide_index=True)

    st.divider()
    st.title("Artists")
    st.write(f"Encompassing date range from {start_date.date()} to {end_date.date()}")

    top_artists = analyticsFuncs.top_artists(filtered_df)
    st.write(f"Top {models.Config.top_n} artists by number of plays")
    st.dataframe(top_artists.by_plays, hide_index=True)
    st.write(f"Top {models.Config.top_n} artists by number of full plays (no skips)")
    st.dataframe(top_artists.by_no_skips, hide_index=True)
    st.write(f"Top {models.Config.top_n} artists by minutes listened to")
    st.dataframe(top_artists.by_time, hide_index=True)
    st.write(f"Top {models.Config.top_n} artists by number of unique songs listened to")
    st.dataframe(top_artists.by_diversity, hide_index=True)
    st.write(f"Top {models.Config.top_n} artists with lowest skip percentage (where an artist has at least {models.Config.min_plays_artist_skip_analysis} plays)")
    st.dataframe(top_artists.lowest_skip, hide_index=True)
    st.write(f"Top {models.Config.top_n} artists with highest skip percentage (where an artist has at least {models.Config.min_plays_artist_skip_analysis} plays)")
    st.dataframe(top_artists.highest_skip, hide_index=True)
    st.divider()
    st.write(f"Full artist summary statistics for period {start_date.date()} to {end_date.date()}")
    st.dataframe(top_artists.all_data, hide_index=True)

    st.divider()
    st.title("Albums")
    st.write(f"Encompassing date range from {start_date.date()} to {end_date.date()}")
    
    top_albums = analyticsFuncs.top_albums(filtered_df)
    st.write(f"Top {models.Config.top_n} albums by number of plays")
    st.dataframe(top_albums.by_plays, hide_index=True)
    st.write(f"Top {models.Config.top_n} albums by number of full plays (no skips)")
    st.dataframe(top_albums.by_no_skips, hide_index=True)
    st.write(f"Top {models.Config.top_n} albums by minutes listened to")
    st.dataframe(top_albums.by_time, hide_index=True)
    st.write(f"Top {models.Config.top_n} albums by number of unique songs listened to")
    st.dataframe(top_albums.by_diversity, hide_index=True)
    st.write(f"Top {models.Config.top_n} albums with lowest skip percentage (where an artist has at least {models.Config.min_plays_artist_skip_analysis} plays)")
    st.dataframe(top_albums.lowest_skip, hide_index=True)
    st.write(f"Top {models.Config.top_n} albums with highest skip percentage (where an artist has at least {models.Config.min_plays_artist_skip_analysis} plays)")
    st.dataframe(top_albums.highest_skip, hide_index=True)
    st.divider()
    st.write(f"Full album summary statistics for period {start_date.date()} to {end_date.date()}")
    st.dataframe(top_albums.all_data, hide_index=True)

elif st.session_state.page == 'Track':

    st.title("Looking for a Specific Track?")
    search_keyword = st.text_input("Start Searching for a Song", placeholder="Enter a Song Title")
    artist, album = "", ""
    col1, col2, col3 = st.columns(3)
    song_history = None

    with col1:
        exact = st.checkbox("Exact Match?")
    with col2:
        artistEntry = st.checkbox("Refine With Artist?")
    with col3:
        albumEntry = st.checkbox("Refine With Album?")
    if artistEntry:
        artist = st.text_input("Artist Name", placeholder="Enter Artist Name")
    if albumEntry:
        album = st.text_input("Album Name", placeholder="Enter Album Name")

    if search_keyword != "":
        song_history = analyticsFuncs.get_song_stats(st.session_state.data, search_keyword, exact=exact, artist=artist, album=album)
        print(song_history)
    if song_history is not None:
        summary_song_data = analyticsFuncs.song_sum_stats(song_history)
        markdown.summary_song_markdown(summary_song_data)
        plots.make_mins_and_streams_plots(song_history)
        st.divider()
        st.write("When did you listen?")
        time_dfs = analyticsFuncs.get_data_for_polar_plots(song_history)
        polar_plots = plots.make_polar_plots(time_dfs)
        plots.plot_polar_plots(polar_plots)
        if st.checkbox("See Full Listening History for this Song?", help="This shows all times this song was listened to, drawn straight from your raw Spotify data."):
            st.dataframe(song_history, hide_index=True)

elif st.session_state.page == 'Artist':

    st.title("Looking for a Specific Artist?")
    search_keyword = st.text_input("Start Searching for an Artist", placeholder="Enter an Artist's Name")
    exact = st.checkbox("Exact Match?")
    artist_hist = None

    if search_keyword != "":
        artist_hist = analyticsFuncs.get_artist_hist(st.session_state.data, search_keyword, exact=exact)
        if artist_hist is not None:
            artist_sum_stats = analyticsFuncs.artist_album_sum_stats(artist_hist, artist=True)
            markdown.summary_artist_album_markdown(artist_sum_stats, artist=True)

            if artist_sum_stats.unique_songs > models.Config.top_n:
                see_all_songs = st.checkbox(f"See all songs? ({artist_sum_stats.unique_songs})")
                if see_all_songs:
                    st.dataframe(artist_sum_stats.full_hist, hide_index=True)
    
            top_albums_for_artist = analyticsFuncs.top_albums(artist_hist, single=True)
            top_albums_for_artist.drop(columns=['artist_name'], inplace=True)
            st.subheader("Top Albums for this Artist")
            st.write(f"Top {models.Config.top_n} albums by number of plays")
            st.dataframe(top_albums_for_artist.head(models.Config.top_n), hide_index=True)
            if artist_sum_stats.unique_albums > models.Config.top_n:
                see_all_albums = st.checkbox(f"See all albums? ({artist_sum_stats.unique_albums})")
                if see_all_albums:
                    st.dataframe(top_albums_for_artist, hide_index=True)
        
        plots.make_mins_and_streams_plots(artist_hist)

        st.divider()
        st.subheader("When did you listen?")
        st.write(f"For the time period {artist_hist['ts'].min().date()} to {artist_hist['ts'].max().date()}")
        time_dfs = analyticsFuncs.get_data_for_polar_plots(artist_hist)
        polar_plots = plots.make_polar_plots(time_dfs)
        plots.plot_polar_plots(polar_plots)

    if artist_hist is not None:
        if st.checkbox("See Full Listening History for this Artist?", help="This shows all times a song from this artist was listened to, drawn straight from your raw Spotify data."):
            st.dataframe(artist_hist, hide_index=True)

elif st.session_state.page == 'Album':

    st.title("Looking for a Specific Album?")
    search_keyword = st.text_input("Start Searching for an Album", placeholder="Enter an Album Name")
    exact = st.checkbox("Exact Match?")
    album_hist = None

    if search_keyword != "":
        album_hist = analyticsFuncs.get_album_hist(st.session_state.data, search_keyword, exact=exact)
        if album_hist is not None:
            album_sum_stats = analyticsFuncs.artist_album_sum_stats(album_hist, album=True)
            markdown.summary_artist_album_markdown(album_sum_stats, album=True)

    if album_hist is not None and album_sum_stats.unique_songs > models.Config.top_n:
        see_all_songs = st.checkbox(f"See all songs? ({album_sum_stats.unique_songs})")
        if see_all_songs:
            st.dataframe(album_sum_stats.full_hist, hide_index=True)
        
        plots.make_mins_and_streams_plots(album_hist)

        st.divider()
        st.subheader("When did you listen?")
        st.write(f"For the time period {album_hist['ts'].min().date()} to {album_hist['ts'].max().date()}")
        time_dfs = analyticsFuncs.get_data_for_polar_plots(album_hist)
        polar_plots = plots.make_polar_plots(time_dfs)
        plots.plot_polar_plots(polar_plots)

    if album_hist is not None:
        if st.checkbox("See Full Listening History for this Album?", help="This shows all times a song from this album was listened to, drawn straight from your raw Spotify data."):
            st.dataframe(album_hist, hide_index=True)
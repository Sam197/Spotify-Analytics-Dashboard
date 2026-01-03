import streamlit as st
import pandas as pd
import analyticsFuncs, markdown
import plotly.express as px
import plots

st.set_page_config(page_title="Music Analytics", layout="wide")

#st.logo('Data from backscatter.png', size='large')
if 'data' not in st.session_state:
    st.session_state.data = None
    st.session_state.has_inital_data = False
if 'page' not in st.session_state:
    st.session_state.page = 'Upload'
if st.session_state.data is not None:
    page = st.sidebar.radio("Navigate", ['Upload', 'Home', 'Track', 'Artist', 'Album'])
    st.session_state.page = page
    st.sidebar.markdown("Checkout the [GitHub Repository](https://github.com/Sam197/Spotify-Analytics-Dashboard)!")

if st.session_state.page == 'Upload' or st.session_state.data is None:
    st.title("📊 Spotify Analytics Dashboard")
    if st.session_state.data is None:
        st.markdown("### Upload your data to get started")
    else:
        st.markdown("### Upload different data?")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['json'],
        help="Upload JSON files containing your music data",
        accept_multiple_files=True
    )

    if uploaded_files is not None and uploaded_files != []:
        try:
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

        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    else:
        if not st.session_state.has_inital_data:
            st.info("Please upload .json files to begin analysis")
        else:
            st.info("You can analyse different data if you upload new stuff here!")

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
    tot, totNSkip, skipPercentage, totMins = analyticsFuncs.basicStats(filtered_df)
    with col1:
        st.metric("Total Plays", tot)
    with col2:
        st.metric("Total Plays No Skips", totNSkip)
    with col3:
        st.metric("Skip Percentage", f"{(skipPercentage*100):.2f}%")
    with col4:
        st.metric("Total Listening Time", f"{totMins:.2f} minutes")

    col1, col2 = st.columns(2)
    fl, ll, ta = analyticsFuncs.firstLastPlay(filtered_df)
    with col1:
        st.markdown(f"## First Listen: {fl[0].date()}")
        st.write(f"{fl[1]} by {fl[2]}")
    with col2:
        st.markdown(f"## Last Listen: {ll[0].date()}")
        st.write(f"{ll[1]} by {ll[2]}")
    st.markdown(f"### Thats {ta} days apart!")

    st.divider()

    st.subheader("When Do You Listen?")
    time_dfs = analyticsFuncs.get_data_for_polar_plots(filtered_df)
    polar_plots = plots.make_polar_plots(time_dfs)
    plots.plot_polar_plots(polar_plots)

    st.divider()
    st.subheader("Graph - Yipee")

    freq_map = {
    "Daily": "D",
    "Weekly": "W",
    "Monthly": "M",
    "Yearly": "Y"
    }

    selected_label = st.select_slider(
        "Select Time Grain",
        options=["Daily", "Weekly", "Monthly", "Yearly"],
        value="Weekly"
    )
    freq_alias = freq_map[selected_label]

    resampled_df = filtered_df.set_index('ts').resample(freq_alias)['ms_played'].agg(['sum', 'size']).reset_index()
    resampled_df.columns = ['ts', 'ms_played', 'streams']
    resampled_df['minutes'] = resampled_df['ms_played'] / 60000

    fig = px.line(
        resampled_df, 
        x='ts', 
        y='minutes', 
        title=f"Total Minutes Listened ({selected_label}) between {start_date.date()} and {end_date.date()}",
        labels={'ts': 'Date', 'minutes': 'Minutes Played'},
        #markers=True if selected_label != "Daily" else False # Markers help on larger grains
    )

    fig.update_layout(hovermode="x unified")
    
    st.plotly_chart(fig, width='stretch')

    peak_mins_t = resampled_df['minutes'].idxmax()
    peak_mins_freq = resampled_df['minutes'].max()
    peak_mins_t = resampled_df['ts'].iloc[peak_mins_t].date()
    st.write(f"Peak {selected_label}: {peak_mins_t} with {peak_mins_freq:.2f} mins")


    fig = px.line(
        resampled_df,
        x='ts',
        y='streams',
        title=f"Total Number of Streams ({selected_label}) between {start_date.date()} and {end_date.date()}",
        labels={'ts': 'Date'}
    )
    fig.update_layout(hovermode="x unified")
    
    st.plotly_chart(fig, width='stretch')
    
    track_df = filtered_df.copy(deep=True)
    track_df['time_frame'] = track_df['ts'].dt.to_period(freq_alias)
    peak_t = track_df['time_frame'].value_counts().idxmax()
    peak_t_count = track_df['time_frame'].value_counts().max()

    st.write(f"Peak {selected_label}: {peak_t} with {peak_t_count} listnes")
    
    corr = resampled_df['minutes'].corr(resampled_df['streams'])
    st.write(f"Correlation between Minutes Played and Number of Streams: {corr:.4f}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.title("Track Analytics")
    with col2:
        show_uri = st.checkbox("Show URIs?")
    st.write(f"Encompassing date range from {start_date.date()} to {end_date.date()}")

    song_sum, t10simple, t10noskip, t10mins, t10meanmin, t10lowskip, t10hightskip = analyticsFuncs.top_songs(filtered_df, show_uri=show_uri)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} songs by number of plays")
    st.dataframe(t10simple, hide_index=True)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} songs with no skips")
    st.dataframe(t10noskip, hide_index=True)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} songs by minutes listened to")
    st.dataframe(t10mins, hide_index=True)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} songs by average listen time")
    st.dataframe(t10meanmin, hide_index=True)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} songs by lowest skip percentage (where a song has at least 20 plays)")
    st.dataframe(t10lowskip, hide_index=True)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} songs by highest skip percentage (where a song has at least 20 plays)")
    st.dataframe(t10hightskip, hide_index=True)
    st.divider()
    st.write(f"Full song summary statistics for period {start_date.date()} to {end_date.date()}")
    st.dataframe(song_sum, hide_index=True)

    st.divider()
    st.title("Artists")
    st.write(f"Encompassing date range from {start_date.date()} to {end_date.date()}")

    artist_sum, ta10simple, ta10noskip, ta10mins, ta10unique, ta10lskippercen, ta10hskippercen = analyticsFuncs.top_artists(filtered_df)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} artists by number of plays")
    st.dataframe(ta10simple, hide_index=True)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} artists by number of full plays (no skips)")
    st.dataframe(ta10noskip, hide_index=True)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} artists by minutes listened to")
    st.dataframe(ta10mins, hide_index=True)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} artists by number of unique songs listened to")
    st.dataframe(ta10unique, hide_index=True)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} artists with lowest skip percentage (where an artist has at least 100 plays)")
    st.dataframe(ta10lskippercen, hide_index=True)
    st.write(f"Top {analyticsFuncs.TOP_SONG_HEAD} artists with highest skip percentage (where an artist has at least 100 plays)")
    st.dataframe(ta10hskippercen, hide_index=True)
    st.divider()
    st.write(f"Full artist summary statistics for period {start_date.date()} to {end_date.date()}")
    st.dataframe(artist_sum, hide_index=True)

elif st.session_state.page == 'Track':
    df = st.session_state.data
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
        song_history = analyticsFuncs.get_song_stats(df, search_keyword, exact=exact, artist=artist, album=album)
        print(song_history)
    if song_history is not None:
        summary_song_data = analyticsFuncs.song_sum_stats(song_history)
        markdown.summary_song_markdown(summary_song_data)
        resampled_df = song_history.set_index('ts').resample('ME').size().reset_index(name='Plays')
        fig = px.line(resampled_df, x='ts', y='Plays',title="Daily Listens Over Time", labels={'ts': 'Date', 'Play Count': 'Number of Plays'})
        st.plotly_chart(fig)
        st.divider()
        st.write("When did you listen?")
        time_dfs = analyticsFuncs.get_data_for_polar_plots(song_history)
        polar_plots = plots.make_polar_plots(time_dfs)
        plots.plot_polar_plots(polar_plots)

elif st.session_state.page == 'Artist':
    df = st.session_state.data
    st.title("Looking for a Specific Artist?")
    search_keyword = st.text_input("Start Searching for an Artist", placeholder="Enter an Artist's Name")
    exact = st.checkbox("Exact Match?")
    artist_hist = None
    if search_keyword != "":
        artist_hist = analyticsFuncs.get_artist_hist(df, search_keyword, exact=exact)
        if artist_hist is not None:
            artist_sum_stats = analyticsFuncs.artist_sum_stats(artist_hist)
            markdown.summary_artist_markdown(artist_sum_stats)
    if artist_hist is not None and artist_sum_stats['unique_songs'] > analyticsFuncs.TOP_SONG_HEAD:
        see_all_songs = st.checkbox(f"See all songs? ({artist_sum_stats['unique_songs']})")
        artist_hist_full = artist_hist['master_metadata_track_name'].value_counts().reset_index()
        artist_hist_full.columns = ['Song', 'Listens']
        if see_all_songs:
            st.dataframe(artist_hist_full, hide_index=True)
        fig = px.histogram(
            artist_hist_full,
            x='Listens',
            title="Distribution of Song Plays",
        )
        st.plotly_chart(fig)

        st.divider()
        st.subheader("When did you listen?")
        st.write(f"For the time period {artist_hist['ts'].min().date()} to {artist_hist['ts'].max().date()}")
        time_dfs = analyticsFuncs.get_data_for_polar_plots(artist_hist)
        polar_plots = plots.make_polar_plots(time_dfs)
        plots.plot_polar_plots(polar_plots)

elif st.session_state.page == 'Album':
    st.title("Looks like I have not implemented this yet. Whoops")

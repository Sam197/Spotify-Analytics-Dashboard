import streamlit as st
from analyticsFuncs import MONTHS

def summary_song_markdown(data):

    st.markdown(f"""
    ### 🎵 Track Report: {data.name}
    **Artist:** {data.artist}  
    **Album:** {data.album}

    ---

    #### 📅 Listening Timeline
    * **First Heard:** `{data.first_listen.strftime('%Y-%m-%d')}`
    * **Last Heard:** `{data.last_listen.strftime('%Y-%m-%d')}` ({data.timespan} days apart)

    ---

    #### 📊 Play Statistics
    | Metric | Value |
    | :--- | :--- |
    | **Total Plays** | {data.tot_plays} |
    | **Full Listens** | {data.full_plays} |
    | **Skips** | {data.tot_skips} ({100 - data.listen_rate:.1f}% skip rate) |
    | **Total Time** | {data.tot_hours:.2f} hours |

    ---

    #### ⚡ Engagement
    * **Binge Factor:** {data.most_plays_in_day} plays in a single day (on {data.most_plays_in_day_date})
    * **Monthly Velocity:** {data.avg_plays_per_month:.2f} plays/month
    * **Peak Month:** {MONTHS[data.peak_month.month]} {data.peak_month.year} ({data.peak_month_count} plays)

    ---
    """)

def summary_artist_album_markdown(data, artist=False, album=False):

    profile = "Artist" if artist else "Album"

    if artist:
        st.markdown(f"""
        ### {profile} Profile: {data.artist_name}
        ---
        """)
    else:
        st.markdown(f"""
        ### {profile} Profile: {data.album_name} by {data.artist_name}
        ---
        """)
    if artist:
        st.markdown(f"""
        #### 📊 Career Statistics
        | Metric | Value |
        | :--- | :--- |
        | **Total Time** | {data.tot_mins:.2f} Minutes |
        | **Total Plays** | {data.tot_plays} |
        | **Unique Songs** | {data.unique_songs} |
        | **Unique Albums** | {data.unique_albums} |
        | **Loyalty** | Listened to in {data.years_active} different year(s) |
        """)
    else:
        st.markdown(f"""
        #### 📊 Career Statistics
        | Metric | Value |
        | :--- | :--- |
        | **Total Time** | {data.tot_mins:.2f} Minutes |
        | **Total Plays** | {data.tot_plays} |
        | **Unique Songs** | {data.unique_songs} |
        | **Loyalty** | Listened to in {data.years_active} different year(s) |
        """)
    st.markdown(f"""
    ---

    #### 📅 Journey Timeline
    * **First Listen:** `{data.first_song_row['ts'].strftime('%Y-%m-%d')}`  
    ↳ *Song:* {data.first_song_row['master_metadata_track_name']}
    * **Last Listen:** `{data.last_song_row['ts'].strftime('%Y-%m-%d')}`  
    ↳ *Song:* {data.last_song_row['master_metadata_track_name']}

    ---

    #### ⚡ Engagement
    * **Binge Factor:** {data.most_plays_in_day} plays in a single day (on {data.most_plays_in_day_date})
    * **Monthly Velocity:** {data.avg_plays_per_month:.2f} plays/month
    * **Peak Month:** {MONTHS[data.peak_month.month]} {data.peak_month.year} ({data.peak_month_count} plays)

    ---
    #### 🎵 Top Songs
    """
    )
    st.dataframe(data.top_songs, hide_index=True)

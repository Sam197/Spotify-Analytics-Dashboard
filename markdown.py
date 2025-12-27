import streamlit as st

def summary_song_markdown(data):

    st.markdown(f"""
    ### 🎵 Track Report: {data['name']}
    **Artist:** {data['artist']}  
    **Album:** {data['album']}

    ---

    #### 📅 Listening Timeline
    * **First Heard:** `{data['first_listen'].strftime('%Y-%m-%d')}`
    * **Last Heard:** `{data['last_listen'].strftime('%Y-%m-%d')}` ({data['timespan']} days apart)

    ---

    #### 📊 Play Statistics
    | Metric | Value |
    | :--- | :--- |
    | **Total Plays** | {data['tot_plays']} |
    | **Full Listens** | {data['full_plays']} |
    | **Skips** | {data['tot_skips']} ({100 - data['listen_rate']:.1f}% skip rate) |
    | **Total Time** | {data['tot_hours']:.2f} hours |

    ---

    #### ⚡ Engagement
    * **Binge Factor:** {data['most_plays_in_day']} plays in a single day
    * **Monthly Velocity:** {data['avg_plays_per_month']:.2f} plays/month

    ---
    """)

def summary_artist_markdown(data):

    table_rows = ""
    for _, row in data['top_songs'].iterrows():
        table_rows += f"| {row['Song']} | {row['Listens']} |\n"

    st.markdown(f"""
    ### 🎤 Artist Profile: {data['artist_name']}

    ---

    #### 📊 Career Statistics
    | Metric | Value |
    | :--- | :--- |
    | **Total Time** | {data['tot_hours']:.2f} Hours |
    | **Total Plays** | {data['tot_plays']} |
    | **Unique Songs** | {data['unique_songs']} |
    | **Loyalty** | Listened to in {data['years_active']} different year(s) |

    ---

    #### 📅 Journey Timeline
    * **First Listen:** `{data['first_song_row']['ts'].strftime('%Y-%m-%d')}`  
    ↳ *Song:* {data['first_song_row']['master_metadata_track_name']}
    * **Last Listen:** `{data['last_song_row']['ts'].strftime('%Y-%m-%d')}`  
    ↳ *Song:* {data['last_song_row']['master_metadata_track_name']}

    ---

    #### 🏆 Insights & Top Tracks
    * **Peak Era:** You listened to this artist most in **{data['peak_month']}** ({data['peak_month_count']} plays).
    """
    )
    st.dataframe(data['top_songs'], hide_index=True)
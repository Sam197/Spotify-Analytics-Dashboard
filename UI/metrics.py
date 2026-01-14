import streamlit as st

def display_basic_stats(basic_stats):
    """Display basic statistics in a grid of metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Plays", basic_stats.total_plays)
    with col2:
        st.metric("Total Plays No Skips", basic_stats.total_plays_no_skips)
    with col3:
        st.metric("Skip Percentage", f"{(basic_stats.skip_percentage*100):.2f}%")
    with col4:
        st.metric("Total Listening Time", f"{basic_stats.total_minutes:.2f} minutes")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Unique Songs", basic_stats.unique_tracks)
    with col2:
        st.metric("Unique Artists", basic_stats.unique_artists)
    with col3:
        st.metric("Unique Albums", basic_stats.unique_albums)
    with col4:
        avg_plays = basic_stats.total_plays / basic_stats.unique_tracks
        st.metric("On average each song is played", f"{avg_plays:.2f} times")

def display_first_last_play(first_last_play):
    """Display first and last play information"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"## First Listen: {first_last_play.first_play[0].date()}")
        st.write(f"{first_last_play.first_play[1]} by {first_last_play.first_play[2]}")
    
    with col2:
        st.markdown(f"## Last Listen: {first_last_play.last_play[0].date()}")
        st.write(f"{first_last_play.last_play[1]} by {first_last_play.last_play[2]}")
    
    st.markdown(f"### That's {first_last_play.timespan} days apart!")
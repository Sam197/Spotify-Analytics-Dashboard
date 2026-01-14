import streamlit as st
import models

def display_top_table(title, data, show_index=False):
    """Display a table with a title"""
    st.write(title)
    st.dataframe(data, hide_index=not show_index)

def display_top_songs_section(top_songs, start_date, end_date, show_uri=False):
    """Display all top songs tables"""
    st.write(f"Encompassing date range from {start_date.date()} to {end_date.date()}")
    
    display_top_table(
        f"Top {models.Config.top_n} songs by number of plays",
        top_songs.by_plays
    )
    
    display_top_table(
        f"Top {models.Config.top_n} songs with no skips",
        top_songs.by_no_skips
    )
    
    display_top_table(
        f"Top {models.Config.top_n} songs by minutes listened to",
        top_songs.by_minutes
    )
    
    display_top_table(
        f"Top {models.Config.top_n} songs by average listen time",
        top_songs.by_mean_minutes
    )
    
    display_top_table(
        f"Top {models.Config.top_n} songs by lowest skip percentage "
        f"(where a song has at least {models.Config.min_plays_skip_analysis} plays)",
        top_songs.lowest_skip
    )
    
    display_top_table(
        f"Top {models.Config.top_n} songs by highest skip percentage "
        f"(where a song has at least {models.Config.min_plays_skip_analysis} plays)",
        top_songs.highest_skip
    )
    
    st.divider()
    st.write(f"Full song summary statistics for period {start_date.date()} to {end_date.date()}")
    st.dataframe(top_songs.all_data, hide_index=True)

def display_top_artists_section(top_artists, start_date, end_date):
    """Display all top artists tables"""
    st.title("Artists")
    st.write(f"Encompassing date range from {start_date.date()} to {end_date.date()}")
    
    display_top_table(
        f"Top {models.Config.top_n} artists by number of plays",
        top_artists.by_plays
    )
    
    display_top_table(
        f"Top {models.Config.top_n} artists by number of full plays (no skips)",
        top_artists.by_no_skips
    )
    
    display_top_table(
        f"Top {models.Config.top_n} artists by minutes listened to",
        top_artists.by_time
    )
    
    display_top_table(
        f"Top {models.Config.top_n} artists by number of unique songs listened to",
        top_artists.by_diversity
    )
    
    display_top_table(
        f"Top {models.Config.top_n} artists with lowest skip percentage "
        f"(where an artist has at least {models.Config.min_plays_artist_skip_analysis} plays)",
        top_artists.lowest_skip
    )
    
    display_top_table(
        f"Top {models.Config.top_n} artists with highest skip percentage "
        f"(where an artist has at least {models.Config.min_plays_artist_skip_analysis} plays)",
        top_artists.highest_skip
    )
    
    st.divider()
    st.write(f"Full artist summary statistics for period {start_date.date()} to {end_date.date()}")
    st.dataframe(top_artists.all_data, hide_index=True)

def display_top_albums_section(top_albums, start_date, end_date):
    """Display all top albums tables"""
    st.title("Albums")
    st.write(f"Encompassing date range from {start_date.date()} to {end_date.date()}")
    
    display_top_table(
        f"Top {models.Config.top_n} albums by number of plays",
        top_albums.by_plays
    )
    
    display_top_table(
        f"Top {models.Config.top_n} albums by number of full plays (no skips)",
        top_albums.by_no_skips
    )
    
    display_top_table(
        f"Top {models.Config.top_n} albums by minutes listened to",
        top_albums.by_time
    )
    
    display_top_table(
        f"Top {models.Config.top_n} albums by number of unique songs listened to",
        top_albums.by_diversity
    )
    
    display_top_table(
        f"Top {models.Config.top_n} albums with lowest skip percentage "
        f"(where an artist has at least {models.Config.min_plays_artist_skip_analysis} plays)",
        top_albums.lowest_skip
    )
    
    display_top_table(
        f"Top {models.Config.top_n} albums with highest skip percentage "
        f"(where an artist has at least {models.Config.min_plays_artist_skip_analysis} plays)",
        top_albums.highest_skip
    )
    
    st.divider()
    st.write(f"Full album summary statistics for period {start_date.date()} to {end_date.date()}")
    st.dataframe(top_albums.all_data, hide_index=True)
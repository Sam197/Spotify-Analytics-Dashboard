import streamlit as st
import pandas as pd

MS_MIN_CONVERSION = 60000
TOP_SONG_HEAD = 5
DAYS_PER_MONTH = 30.44

def containsOne(df):

    unique_uris = df['spotify_track_uri'].nunique()

    if unique_uris > 2:
        found_versions = (
            df.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name', 'master_metadata_album_album_name'])
            .size()
            .reset_index(name='Listens')
            .rename(columns={
                "master_metadata_track_name": "Track Name",
                "master_metadata_album_artist_name": "Artist",
                "master_metadata_album_album_name": "Album"
            })
        )
        st.write(f"Found Multiple ({unique_uris}) Songs - please refine your search")
        st.dataframe(found_versions.sort_values('Listens', ascending=False), width='stretch', hide_index=True)
        return False
    
    return True

def song_sum_stats(df):
    if df is None or df.empty:
        #print("No data found for this song.")
        return
    
    # Ensure timestamps are datetime objects for math
    df['ts'] = pd.to_datetime(df['ts'])
    df = df.sort_values('ts')

    # Basic Info
    name = df['master_metadata_track_name'].iloc[0]
    artist = df['master_metadata_album_artist_name'].iloc[0]
    album = df['master_metadata_album_album_name'].iloc[0]
    
    # Time Stats
    first_listen = df['ts'].iloc[0]
    last_listen = df['ts'].iloc[-1]
    timespan = (last_listen - first_listen).days
    
    # Playback Stats
    tot_plays = len(df)

    # Summing booleans treats True as 1 and False as 0
    tot_skips = df['skipped'].sum() 
    full_plays = tot_plays - tot_skips
    listen_rate = (full_plays / tot_plays) * 100 if tot_plays > 0 else 0
    
    # Cool New Stats
    tot_hours = df['ms_played'].sum() / MS_MIN_CONVERSION
    avg_plays_per_month = tot_plays / (max(timespan, 1) / DAYS_PER_MONTH)
    
    # "Binge Factor" - What's the most you played this in a single day?
    most_plays_in_day = df.groupby(df['ts'].dt.date).size().max()

    summary_stats = {'name':name, 'artist':artist, 'album':album,
                     'first_listen':first_listen, 'last_listen':last_listen, 'timespan':timespan,
                     'tot_plays':tot_plays, 'tot_skips':tot_skips, 'full_plays':full_plays, 'listen_rate':listen_rate,
                     'tot_hours':tot_hours, 'avg_plays_per_month':avg_plays_per_month, 'most_plays_in_day': most_plays_in_day}

    return summary_stats

def get_song(df, song_name, exact=False, artist=None, album=None):
    mask = pd.Series([True] * len(df), index=df.index)

    if exact:
        mask &= (df['master_metadata_track_name'] == song_name)
    else:
        mask &= df['master_metadata_track_name'].str.contains(song_name, case=False, na=False)

    if artist:
        if exact:
            mask &= (df['master_metadata_album_artist_name'] == artist)
        else:
            mask &= df['master_metadata_album_artist_name'].str.contains(artist, case=False, na=False)

    if album:
        if exact:
            mask &= (df['master_metadata_album_album_name'] == album)
        else:
            mask &= df['master_metadata_album_album_name'].str.contains(album, case=False, na=False)

    song_history = df[mask].copy()
    return song_history

def get_song_stats(df, song_name, exact=False, artist=None, album=None):
    """
    Finds all occurrences of a song in the dataframe with optional artist/album filters.
    """
    song_history = get_song(df, song_name, exact, artist, album)

    if song_history.empty:
        st.write(f"No matches found for Song: '{song_name}', Artist: '{artist}', Album: '{album}'.")
        #print(f"No matches found for Song: '{song_name}', Artist: '{artist}', Album: '{album}'.")
        return None

    if not containsOne(song_history):
        return None
    
    song_history['ts'] = pd.to_datetime(song_history['ts'])
    song_history = song_history.sort_values('ts')
    return song_history

def firstLastPlay(df):
    df = df.sort_values('ts')
    cols = ['ts', 'master_metadata_track_name', 'master_metadata_album_artist_name', 'master_metadata_album_album_name']
    validPlays = df.dropna(subset=cols)

    if not validPlays.empty:
        firstPlay = tuple(validPlays.iloc[0][cols])
        lastPlay = tuple(validPlays.iloc[-1][cols])
    else:
        firstPlay = lastPlay = None

    #print(firstPlay[0], type(firstPlay[0]))
    tspan = (lastPlay[0] - firstPlay[0]).days
    return firstPlay, lastPlay, tspan

def basicStats(df):
    totalPlays = len(df)
    totalPlaysNoSkips = len(df[df['skipped']==False])
    skipPercentage = 1 - (totalPlaysNoSkips/totalPlays)
    totalMinutes = df['ms_played'].sum()/MS_MIN_CONVERSION
    df = df.sort_values('ts')
    return totalPlays, totalPlaysNoSkips, skipPercentage, totalMinutes

def artist_sum_stats(artist_df):

    artist_df['ts'] = pd.to_datetime(artist_df['ts'])
    artist_df = artist_df.sort_values('ts')
    
    # 3. Core Stats
    tot_plays = len(artist_df)
    tot_hours = artist_df['ms_played'].sum() / (1000 * 60 * 60)
    unique_songs = artist_df['master_metadata_track_name'].nunique()
    
    # 4. First and Last Listen (and the specific songs)
    first_row = artist_df.iloc[0]
    last_row = artist_df.iloc[-1]
    
    # 6. Your "Peak Era" (The month you listened to them the most)
    artist_df['month_year'] = artist_df['ts'].dt.to_period('M')
    peak_month = artist_df['month_year'].value_counts().idxmax()
    peak_month_count = artist_df['month_year'].value_counts().max()

    # 7. Loyalty Score (How many different years have you listened to them?)
    years_active = artist_df['ts'].dt.year.nunique()
    # 1. First, build the Top Tracks string
    actual_name = artist_df['master_metadata_album_artist_name'].iloc[0]
    top_songs = pd.DataFrame(artist_df['master_metadata_track_name'].value_counts().head(TOP_SONG_HEAD).reset_index())
    top_songs.columns = ['Song', 'Listens']

    summary_stats = {'artist_name':actual_name, 'tot_plays':tot_plays, 'tot_hours':tot_hours, 'unique_songs':unique_songs,
                     'first_song_row':first_row, 'last_song_row':last_row, 'peak_month':peak_month, 'peak_month_count':peak_month_count,
                     'years_active':years_active, 'top_songs':top_songs}

    return summary_stats

def get_artist(df, artist, exact):
    
    if exact:
        artist_history = df[df['master_metadata_album_artist_name'] == artist]
    else:
        artist_history = df[df['master_metadata_album_artist_name'].str.contains(artist, case=False, na=False)].copy()

    #print(artist_history['master_metadata_album_artist_name'])
    return artist_history

def get_artist_hist(df, artist, exact = False):

    artist_hist = get_artist(df, artist, exact)
    #print(artist_hist)
    unique_artists = artist_hist['master_metadata_album_artist_name'].nunique()
    if unique_artists > 2:
        #print("More than 2 artists")
        found_artists = (
            artist_hist.groupby('master_metadata_album_artist_name')
            .size()
            .reset_index(name='Listens')
            .rename(columns={
                "master_metadata_album_artist_name": "Artist",
            })
        )
        st.write(f"Found Multiple {unique_artists} Artists - please refine your search")
        st.dataframe(found_artists.sort_values('Listens', ascending=False), width='stretch', hide_index=True)
        return None
    elif artist_hist.empty:
        st.write(f"Could not find an artist containing '{artist}'")
        return None
    else:
        return artist_hist


def dfAnalytics(df):
    song_summary = df.groupby('spotify_track_uri').agg(
    # We use 'first' to grab the names associated with that unique URI
    track_name=('master_metadata_track_name', 'first'),
    artist_name=('master_metadata_album_artist_name', 'first'),
    album_name=('master_metadata_album_album_name', 'first'),
    
    # The math
    total_ms=('ms_played', 'sum'),
    total_plays=('ms_played', 'count'),
    mean_listen_ms=('ms_played', 'mean'),
    plays_no_skips=('skipped', lambda x: (x == False).sum())
    ).reset_index()

    # 2. Add minutes and filter
    song_summary['total_minutes'] = song_summary['total_ms'] / MS_MIN_CONVERSION
    song_summary['mean_listen_mins'] = song_summary['mean_listen_ms'] / MS_MIN_CONVERSION
    song_summary = song_summary.drop(columns=['total_ms', 'mean_listen_ms'])
    return song_summary

def top_songs(df):
    song_sum = dfAnalytics(df)
    top10simple = song_sum.sort_values('total_plays', ascending=False).head(10)
    top10noskip = song_sum.sort_values('plays_no_skips', ascending=False).head(10)
    top10mins = song_sum.sort_values('total_minutes', ascending=False).head(10)
    top10meanmins = song_sum.sort_values('mean_listen_mins', ascending=False).head(10)
    return top10simple, top10noskip, top10mins, top10meanmins

def artistAnalytics(df):
    # 1. Group by Artist Name
    # Note: We group by the name directly since Spotify doesn't always 
    # provide a unique Artist URI in every export version.
    artist_summary = df.groupby('master_metadata_album_artist_name').agg(
        # Diversity stats
        unique_tracks=('master_metadata_track_name', 'nunique'),
        unique_albums=('master_metadata_album_album_name', 'nunique'),
        
        # The math
        total_ms=('ms_played', 'sum'),
        total_plays=('ms_played', 'count'),
        mean_listen_ms=('ms_played', 'mean'),
        plays_no_skips=('skipped', lambda x: (x == False).sum())
    ).reset_index()

    # Rename the grouping column for clarity
    artist_summary = artist_summary.rename(columns={'master_metadata_album_artist_name': 'artist_name'})

    # 2. Add minutes and cleanup
    artist_summary['total_minutes'] = artist_summary['total_ms'] / MS_MIN_CONVERSION
    artist_summary['mean_listen_mins'] = artist_summary['mean_listen_ms'] / MS_MIN_CONVERSION
    artist_summary['skip_percentage'] = (1-(artist_summary['plays_no_skips']/artist_summary['total_plays']))*100
    
    # We keep the ms columns for now if needed, or drop them like your original code:
    artist_summary = artist_summary.drop(columns=['total_ms', 'mean_listen_ms'])
    
    return artist_summary

def top_artists(df):
    artist_sum = artistAnalytics(df)
    print(artist_sum)
    # Sorting by different engagement metrics
    top10_by_plays = artist_sum.sort_values('total_plays', ascending=False).head(10)
    top10_by_time = artist_sum.sort_values('total_minutes', ascending=False).head(10)
    top10_by_no_skips = artist_sum.sort_values('plays_no_skips', ascending=False).head(10)
    print(top10_by_time)
    # Sorting by diversity (Who has the most unique songs you've listened to?)
    top10_by_diversity = artist_sum.sort_values('unique_tracks', ascending=False).head(10)
    top10_lowest_skip = artist_sum[artist_sum['total_plays']>=100].sort_values('skip_percentage').head(10)
    
    return top10_by_plays, top10_by_no_skips, top10_by_time, top10_by_diversity, top10_lowest_skip

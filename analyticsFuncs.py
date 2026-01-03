import streamlit as st
import pandas as pd

MS_MIN_CONVERSION = 60000
MS_HOUR_CONVERSION = 3600000
TOP_SONG_HEAD = 5
DAYS_PER_MONTH = 30.44
DAYS_OF_WEEK = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
MONTHS = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
          7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
DATE_SUFFIX = {1: 'st', 2: 'nd', 3: 'rd', 4: 'th', 5: 'th', 6: 'th', 7: 'th', 8: 'th', 9: 'th', 10: 'th',
               11: 'th', 12: 'th', 13: 'th', 14: 'th', 15: 'th', 16: 'th', 17: 'th', 18: 'th', 19: 'th', 20: 'th',
               21: 'st', 22: 'nd', 23: 'rd', 24: 'th', 25: 'th', 26: 'th', 27: 'th', 28: 'th', 29: 'th', 30: 'th',
               31: 'st'}

def containsOne(df):

    unique_uris = df['spotify_track_uri'].nunique()

    if unique_uris > 2:
        found_versions = (
            df.groupby([
                'master_metadata_track_name', 
                'master_metadata_album_artist_name'
            ])
            .agg({
                'master_metadata_album_album_name': 'first',
                'spotify_track_uri': 'count'
            })
            .reset_index()
            .rename(columns={
                "master_metadata_track_name": "Track Name",
                "master_metadata_album_artist_name": "Artist",
                "master_metadata_album_album_name": "Album",
                "spotify_track_uri": "Listens"
            })
        )
        st.write(f"Found Multiple ({unique_uris}) Songs - please refine your search")
        st.dataframe(found_versions.sort_values('Listens', ascending=False), width='stretch')
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
    df['month_year'] = df['ts'].dt.to_period('M')
    peak_month = df['month_year'].value_counts().idxmax()
    peak_month_count = df['month_year'].value_counts().max()
    
    df['date'] = df['ts'].dt.to_period('D')
    most_plays_in_day_date = df['date'].value_counts().idxmax()
    most_plays_in_day = df['date'].value_counts().max()

    summary_stats = {'name':name, 'artist':artist, 'album':album,
                     'first_listen':first_listen, 'last_listen':last_listen, 'timespan':timespan,
                     'tot_plays':tot_plays, 'tot_skips':tot_skips, 'full_plays':full_plays, 'listen_rate':listen_rate,
                     'tot_hours':tot_hours, 'avg_plays_per_month':avg_plays_per_month, 'most_plays_in_day': most_plays_in_day,
                     'most_plays_in_day_date': most_plays_in_day_date, 'peak_month':peak_month, 'peak_month_count':peak_month_count}

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
    tot_hours = artist_df['ms_played'].sum() / MS_HOUR_CONVERSION
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
        st.write(f"Found Multiple ({unique_artists}) Artists - please refine your search")
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
    song_summary['skip_percentage'] = (1-(song_summary['plays_no_skips']/song_summary['total_plays']))*100

    return song_summary

def top_songs(df, show_uri=True):
    song_sum = dfAnalytics(df)
    if not show_uri:
        song_sum.drop(columns=['spotify_track_uri'], inplace=True)
    top10simple = song_sum.sort_values('total_plays', ascending=False).head(TOP_SONG_HEAD)
    top10noskip = song_sum.sort_values('plays_no_skips', ascending=False).head(TOP_SONG_HEAD)
    top10mins = song_sum.sort_values('total_minutes', ascending=False).head(TOP_SONG_HEAD)
    top10meanmins = song_sum.sort_values('mean_listen_mins', ascending=False).head(TOP_SONG_HEAD)
    top10lowestskip = song_sum[song_sum['total_plays']>=20].sort_values('skip_percentage').head(TOP_SONG_HEAD)
    top10highestskip = song_sum[song_sum['total_plays']>=20].sort_values('skip_percentage', ascending=False).head(TOP_SONG_HEAD)

    return song_sum, top10simple, top10noskip, top10mins, top10meanmins, top10lowestskip, top10highestskip

def artistAnalytics(df):
    # 1. Group by artist and aggregate
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
    top10_by_plays = artist_sum.sort_values('total_plays', ascending=False).head(TOP_SONG_HEAD)
    top10_by_time = artist_sum.sort_values('total_minutes', ascending=False).head(TOP_SONG_HEAD)
    top10_by_no_skips = artist_sum.sort_values('plays_no_skips', ascending=False).head(TOP_SONG_HEAD)
    top10_by_diversity = artist_sum.sort_values('unique_tracks', ascending=False).head(TOP_SONG_HEAD)
    top10_lowest_skip = artist_sum[artist_sum['total_plays']>=100].sort_values('skip_percentage').head(TOP_SONG_HEAD)
    top10_highest_skip = artist_sum[artist_sum['total_plays']>=100].sort_values('skip_percentage', ascending=False).head(TOP_SONG_HEAD)
    
    return artist_sum, top10_by_plays, top10_by_no_skips, top10_by_time, top10_by_diversity, top10_lowest_skip, top10_highest_skip

def get_data_for_polar_plots(df):

    hourly_counts = df['ts'].dt.hour.value_counts().sort_index().reset_index()
    hourly_counts.columns = ['hour', 'count']
    hourly_counts['hour'] = hourly_counts['hour'].astype(str) + ":00"

    daily_counts_week = df['ts'].dt.dayofweek.value_counts().sort_index().reset_index()
    daily_counts_week.columns = ['day', 'count']
    daily_counts_week['day'] = daily_counts_week['day'].map(DAYS_OF_WEEK)

    daily_counts_month = df['ts'].dt.day.value_counts().sort_index().reset_index()
    daily_counts_month.columns = ['day', 'count']
    daily_counts_month['day'] = daily_counts_month['day'].apply(lambda x: str(x) + DATE_SUFFIX[x])
    monthly_counts = df['ts'].dt.month.value_counts().sort_index().reset_index()
    monthly_counts.columns = ['month', 'count']
    #monthly_counts = monthly_counts.reindex(range(0,12), fill_value=0)
    monthly_counts['month'] = monthly_counts['month'].map(MONTHS)

    # minute_counts = df['ts'].dt.minute.value_counts().sort_index().reset_index()
    # minute_counts.columns = ['minute', 'count']
    # minute_counts['minute'] = minute_counts['minute'].astype(str)

    # second_counts = df['ts'].dt.second.value_counts().sort_index().reset_index()
    # second_counts.columns = ['second', 'count']
    # second_counts['second'] = second_counts['second'].astype(str)

    return {'hourly_counts': hourly_counts, 'daily_counts_week': daily_counts_week, 'daily_counts_month': daily_counts_month, 'monthly_counts':  monthly_counts}
from matplotlib import artist
import streamlit as st
import pandas as pd
from models import *

MS_MIN_CONVERSION = 60000
MS_HOUR_CONVERSION = 3600000
DAYS_PER_MONTH = 30.44
TOP_SONG_COLUMN_ORDER = ['spotify_track_uri', 'track_name', 'artist_name', 'album_name',
                'total_plays', 'plays_no_skips', 'total_minutes', 'mean_listen_mins', 'skip_percentage']
TOP_ALBUM_COLUMN_ORDER = ['album_name', 'artist_name', 'unique_tracks',
                'total_plays', 'plays_no_skips', 'total_minutes', 'mean_listen_mins', 'skip_percentage']

def reorganiseColumns(df, column_order=None):
    if column_order is None:
        return df
    df = df.loc[:, column_order + [col for col in df.columns if col not in column_order]]
    return df

# def round_df(df, decimal_places=2, columns=['total_minutes', 'mean_listen_mins', 'skip_percentage']):
#     df[columns] = df[columns].map(f"{{:.{decimal_places}f}}".format)
#     #df[columns] = df[columns].astype(float)
#     #df[columns] = df[columns].round(decimal_places)
#     return df

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
        return None
    
    df['ts'] = pd.to_datetime(df['ts'])
    df = df.sort_values('ts')

    name = df['master_metadata_track_name'].iloc[0]
    artist = df['master_metadata_album_artist_name'].iloc[0]
    album = df['master_metadata_album_album_name'].iloc[0]
    
    first_listen = df['ts'].iloc[0]
    last_listen = df['ts'].iloc[-1]
    timespan = (last_listen - first_listen).days
    
    tot_plays = len(df)
    tot_skips = df['skipped'].sum() 
    full_plays = tot_plays - tot_skips
    listen_rate = (full_plays / tot_plays) * 100 if tot_plays > 0 else 0
    
    tot_hours = df['ms_played'].sum() / MS_HOUR_CONVERSION
    avg_plays_per_month = tot_plays / (max(timespan, 1) / DAYS_PER_MONTH)
    
    df['month_year'] = df['ts'].dt.to_period('M')
    peak_month = df['month_year'].value_counts().idxmax()
    peak_month_count = df['month_year'].value_counts().max()
    
    df['date'] = df['ts'].dt.to_period('D')
    most_plays_in_day_date = df['date'].value_counts().idxmax()
    most_plays_in_day = df['date'].value_counts().max()

    return SongStats(
        name=name,
        artist=artist,
        album=album,
        first_listen=first_listen,
        last_listen=last_listen,
        timespan=timespan,
        tot_plays=tot_plays,
        tot_skips=tot_skips,
        full_plays=full_plays,
        listen_rate=listen_rate,
        tot_hours=tot_hours,
        avg_plays_per_month=avg_plays_per_month,
        most_plays_in_day=most_plays_in_day,
        most_plays_in_day_date=most_plays_in_day_date,
        peak_month=peak_month,
        peak_month_count=peak_month_count
    )

def filter_dataframe(df, column, value, exact=False):
    if exact:
        return df[df[column] == value]
    else:
        return df[df[column].str.contains(value, case=False, na=False)]

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
    song_history = get_song(df, song_name, exact, artist, album)

    if song_history.empty:
        st.write(f"No matches found for Song: '{song_name}', Artist: '{artist}', Album: '{album}'.")
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
        first_play = tuple(validPlays.iloc[0][cols])
        last_play = tuple(validPlays.iloc[-1][cols])
        tspan = (last_play[0] - first_play[0]).days
    else:
        first_play = last_play = None
        tspan = 0

    return FirstLastPlay(
        first_play=first_play,
        last_play=last_play,
        timespan=tspan
    )

def basicStats(df):
    total_plays = len(df)
    total_plays_no_skips = len(df[df['skipped'] == False])
    skip_percentage = 1 - (total_plays_no_skips / total_plays)
    total_minutes = df['ms_played'].sum() / MS_MIN_CONVERSION
    
    return BasicStats(
        total_plays=total_plays,
        total_plays_no_skips=total_plays_no_skips,
        skip_percentage=skip_percentage,
        total_minutes=total_minutes
    )

@st.cache_data
def aggregate_by(df, group_col, name_cols=None):
    if name_cols is None:
        name_cols = {}
    
    agg_dict = {
        'total_ms': ('ms_played', 'sum'),
        'total_plays': ('ms_played', 'count'),
        'mean_listen_ms': ('ms_played', 'mean'),
        'plays_no_skips': ('skipped', lambda x: (x == False).sum())
    }
    
    agg_dict.update(name_cols)
    
    summary = df.groupby(group_col).agg(**agg_dict).reset_index()
    
    summary['total_minutes'] = summary['total_ms'] / MS_MIN_CONVERSION
    summary['mean_listen_mins'] = summary['mean_listen_ms'] / MS_MIN_CONVERSION
    summary['skip_percentage'] = (1 - (summary['plays_no_skips'] / summary['total_plays'])) * 100
    
    summary = summary.drop(columns=['total_ms', 'mean_listen_ms'])
    
    return summary

def get_artist(df, artist, exact):
    return filter_dataframe(df, 'master_metadata_album_artist_name', artist, exact)

def get_artist_hist(df, artist, exact=False):
    artist_hist = get_artist(df, artist, exact)
    
    unique_artists = artist_hist['master_metadata_album_artist_name'].nunique()
    
    if unique_artists > 2:
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

@st.cache_data
def dfAnalytics(df):
    return aggregate_by(
        df,
        group_col='spotify_track_uri',
        name_cols={
            'track_name': ('master_metadata_track_name', 'first'),
            'artist_name': ('master_metadata_album_artist_name', 'first'),
            'album_name': ('master_metadata_album_album_name', 'first')
        }
    )

def get_top_n(df, sort_configs, n=5, min_plays_filter=None):
    results = {}
    
    for key, config in sort_configs.items():
        sorted_df = df.copy()
        
        if min_plays_filter and 'min_plays' in config:
            sorted_df = sorted_df[sorted_df['total_plays'] >= config['min_plays']]
        
        if isinstance(config['by'], list):
            sorted_df = sorted_df.sort_values(
                by=config['by'],
                ascending=config.get('ascending', [True] * len(config['by']))
            )
        else:
            sorted_df = sorted_df.sort_values(
                by=config['by'],
                ascending=config.get('ascending', True)
            )
        
        #sorted_df = round_df(sorted_df)
        results[key] = sorted_df.head(n)
    
    return results

def top_songs(df, show_uri=True, config=None):
    if config is None:
        config = Config()
    
    song_sum = dfAnalytics(df)
    song_sum = reorganiseColumns(song_sum, TOP_SONG_COLUMN_ORDER)

    if not show_uri:
        song_sum = song_sum.drop(columns=['spotify_track_uri'])
    
    sort_configs = {
        'by_plays': {'by': 'total_plays', 'ascending': False},
        'by_no_skips': {'by': 'plays_no_skips', 'ascending': False},
        'by_minutes': {'by': 'total_minutes', 'ascending': False},
        'by_mean_minutes': {'by': 'mean_listen_mins', 'ascending': False},
        'lowest_skip': {
            'by': ['skip_percentage', 'total_plays'],
            'ascending': [True, False],
            'min_plays': config.min_plays_skip_analysis
        },
        'highest_skip': {
            'by': 'skip_percentage',
            'ascending': False,
            'min_plays': config.min_plays_skip_analysis
        }
    }
    
    top_results = get_top_n(song_sum, sort_configs, n=config.top_n, min_plays_filter=True)
    
    return TopResults(
        all_data=song_sum,
        by_plays=top_results['by_plays'],
        by_no_skips=top_results['by_no_skips'],
        by_minutes=top_results['by_minutes'],
        by_mean_minutes=top_results['by_mean_minutes'],
        lowest_skip=top_results['lowest_skip'],
        highest_skip=top_results['highest_skip']
    )

@st.cache_data
def artistAnalytics(df):
    base_agg = aggregate_by(
        df,
        group_col='master_metadata_album_artist_name',
        name_cols={
            'unique_tracks': ('master_metadata_track_name', 'nunique'),
            'unique_albums': ('master_metadata_album_album_name', 'nunique')
        }
    )
    
    base_agg = base_agg.rename(columns={'master_metadata_album_artist_name': 'artist_name'})
    
    return base_agg

def top_artists(df, config=None):
    if config is None:
        config = Config()
    
    artist_sum = artistAnalytics(df)
    
    sort_configs = {
        'by_plays': {'by': 'total_plays', 'ascending': False},
        'by_no_skips': {'by': 'plays_no_skips', 'ascending': False},
        'by_time': {'by': 'total_minutes', 'ascending': False},
        'by_diversity': {'by': 'unique_tracks', 'ascending': False},
        'lowest_skip': {
            'by': 'skip_percentage',
            'ascending': True,
            'min_plays': config.min_plays_artist_skip_analysis
        },
        'highest_skip': {
            'by': 'skip_percentage',
            'ascending': False,
            'min_plays': config.min_plays_artist_skip_analysis
        }
    }
    
    top_results = get_top_n(artist_sum, sort_configs, n=config.top_n, min_plays_filter=True)
    
    return TopArtistResults(
        all_data=artist_sum,
        by_plays=top_results['by_plays'],
        by_no_skips=top_results['by_no_skips'],
        by_time=top_results['by_time'],
        by_diversity=top_results['by_diversity'],
        lowest_skip=top_results['lowest_skip'],
        highest_skip=top_results['highest_skip']
    )

@st.cache_data
def albumAnalytics(df):
    base_agg = aggregate_by(
        df,
        group_col='master_metadata_album_album_name',
        name_cols={
            'unique_tracks': ('master_metadata_track_name', 'nunique'),
            'artist_name': ('master_metadata_album_artist_name', 'first')   
        }
    )

    base_agg = base_agg.rename(columns={'master_metadata_album_album_name': 'album_name'})

    return base_agg

def top_albums(df, config=None, single=False):
    if config is None:
        config = Config()
    
    album_sum = albumAnalytics(df)
    album_sum = reorganiseColumns(album_sum, TOP_ALBUM_COLUMN_ORDER)

    if single:
        sort_configs = {
            'by_plays': {'by': 'total_plays', 'ascending': False}
        }
        top_results = get_top_n(album_sum, sort_configs, n=len(album_sum), min_plays_filter=True)
        return top_results['by_plays']
    else:
        sort_configs = {
            'by_plays': {'by': 'total_plays', 'ascending': False},
            'by_no_skips': {'by': 'plays_no_skips', 'ascending': False},
            'by_time': {'by': 'total_minutes', 'ascending': False},
            'by_diversity': {'by': 'unique_tracks', 'ascending': False},
            'lowest_skip': {
                'by': ['skip_percentage', 'total_plays'],
                'ascending': [True, False],
                'min_plays': config.min_plays_artist_skip_analysis
            },
            'highest_skip': {
                'by': ['skip_percentage', 'total_plays'],
                'ascending': [False, False],
                'min_plays': config.min_plays_artist_skip_analysis
            }
        }
        top_results = get_top_n(album_sum, sort_configs, n=Config.top_n, min_plays_filter=True)

    return TopArtistResults(
        all_data=album_sum,
        by_plays=top_results['by_plays'],
        by_no_skips=top_results['by_no_skips'],
        by_time=top_results['by_time'],
        by_diversity=top_results['by_diversity'],
        lowest_skip=top_results['lowest_skip'],
        highest_skip=top_results['highest_skip']
    )

def get_album_hist(df, album_name, exact=False):
    album_hist = filter_dataframe(df, 'master_metadata_album_album_name', album_name, exact)
    unique_albums = album_hist['master_metadata_album_album_name'].nunique()

    if unique_albums > 2:
        found_albums = (
            album_hist.groupby('master_metadata_album_album_name')
            .size()
            .reset_index(name='Listens')
            .rename(columns={
                "master_metadata_album_album_name": "Album",
            })
        )
        st.write(f"Found Multiple ({unique_albums}) Albums - please refine your search")
        st.dataframe(found_albums.sort_values('Listens', ascending=False), width='stretch', hide_index=True)
        return None
    elif album_hist.empty:
        st.write(f"Could not find an album containing '{album_name}'")
        return None
    else:
        return album_hist
    
def artist_album_sum_stats(df, artist=False, album=False):
    df['ts'] = pd.to_datetime(df['ts'])
    df = df.sort_values('ts')
    
    tot_plays = len(df)
    tot_hours = df['ms_played'].sum() / MS_HOUR_CONVERSION
    unique_songs = df['master_metadata_track_name'].nunique()
    unique_albums = df['master_metadata_album_album_name'].nunique()
    
    first_row = df.iloc[0]
    last_row = df.iloc[-1]

    df['month_year'] = df['ts'].dt.to_period('M')
    peak_month = df['month_year'].value_counts().idxmax()
    peak_month_count = df['month_year'].value_counts().max()

    df['date'] = df['ts'].dt.to_period('D')
    most_plays_in_day_date = df['date'].value_counts().idxmax()
    most_plays_in_day = df['date'].value_counts().max()

    timespan = (df['ts'].iloc[-1] - df['ts'].iloc[0]).days
    avg_plays_per_month = tot_plays / (max(timespan, 1) / DAYS_PER_MONTH)

    years_active = df['ts'].dt.year.nunique()

    full_hist = df.groupby('master_metadata_track_name').agg({
        'ts': 'count',
        'ms_played': 'sum',
        'master_metadata_album_album_name': 'first',
        'skipped': lambda x: (x == False).sum()
    }).reset_index().rename(columns={
        'master_metadata_track_name': 'Song',
        'ts': 'Listens',
        'master_metadata_album_album_name': 'Album',
        'skipped': 'Full Listens'
    }).sort_values('Listens', ascending=False)
    full_hist['Total Minutes'] = full_hist['ms_played'] / MS_MIN_CONVERSION
    full_hist = full_hist.drop(columns=['ms_played'])
    
    
    artist_name = df['master_metadata_album_artist_name'].iloc[0]
    album_name = df['master_metadata_album_album_name'].iloc[0]
    if artist:
        full_hist = reorganiseColumns(full_hist, ['Song', 'Album', 'Listens', 'Full Listens', 'Total Minutes'])
    elif album:
        full_hist.drop(columns=['Album'], inplace=True)
        full_hist = reorganiseColumns(full_hist, ['Song', 'Listens', 'Full Listens', 'Total Minutes'])
    
    top_songs = full_hist.head(Config().top_n)

    return ArtistAlbumStats(
        artist_name=artist_name,
        album_name=album_name,
        tot_plays=tot_plays,
        tot_hours=tot_hours,
        unique_songs=unique_songs,
        unique_albums=unique_albums,
        first_song_row=first_row,
        last_song_row=last_row,
        peak_month=peak_month,
        peak_month_count=peak_month_count,
        years_active=years_active,
        top_songs=top_songs,
        full_hist=full_hist,
        most_plays_in_day=most_plays_in_day,
        most_plays_in_day_date=most_plays_in_day_date,
        avg_plays_per_month=avg_plays_per_month
    )


# def artist_sum_stats(artist_df):
#     artist_df['ts'] = pd.to_datetime(artist_df['ts'])
#     artist_df = artist_df.sort_values('ts')
    
#     tot_plays = len(artist_df)
#     tot_hours = artist_df['ms_played'].sum() / MS_HOUR_CONVERSION
#     unique_songs = artist_df['master_metadata_track_name'].nunique()
#     unique_albums = artist_df['master_metadata_album_album_name'].nunique()
    
#     first_row = artist_df.iloc[0]
#     last_row = artist_df.iloc[-1]
    
#     artist_df['month_year'] = artist_df['ts'].dt.to_period('M')
#     peak_month = artist_df['month_year'].value_counts().idxmax()
#     peak_month_count = artist_df['month_year'].value_counts().max()

#     artist_df['date'] = artist_df['ts'].dt.to_period('D')
#     most_plays_in_day_date = artist_df['date'].value_counts().idxmax()
#     most_plays_in_day = artist_df['date'].value_counts().max()
    
#     timespan = (artist_df['ts'].iloc[-1] - artist_df['ts'].iloc[0]).days
#     avg_plays_per_month = tot_plays / (max(timespan, 1) / DAYS_PER_MONTH)

#     years_active = artist_df['ts'].dt.year.nunique()
    
#     actual_name = artist_df['master_metadata_album_artist_name'].iloc[0]

#     full_hist = artist_df.groupby('master_metadata_track_name').agg({
#         'ts': 'count',
#         'ms_played': 'sum',
#         'master_metadata_album_album_name': 'first',
#         'skipped': lambda x: (x == False).sum()
#     }).reset_index().rename(columns={
#         'master_metadata_track_name': 'Song',
#         'ts': 'Listens',
#         'master_metadata_album_album_name': 'Album',
#         'skipped': 'Full Listens'
#     }).sort_values('Listens', ascending=False)
#     full_hist['Total Minutes'] = full_hist['ms_played'] / MS_MIN_CONVERSION
#     full_hist = full_hist.drop(columns=['ms_played'])
#     full_hist = reorganiseColumns(full_hist, ['Song', 'Album', 'Listens', 'Full Listens', 'Total Minutes'])
#     top_songs = full_hist.head(Config().top_n)

#     return ArtistStats(
#         artist_name=actual_name,
#         tot_plays=tot_plays,
#         tot_hours=tot_hours,
#         unique_songs=unique_songs,
#         unique_albums=unique_albums,
#         first_song_row=first_row,
#         last_song_row=last_row,
#         peak_month=peak_month,
#         peak_month_count=peak_month_count,
#         years_active=years_active,
#         top_songs=top_songs,
#         full_hist=full_hist,
#         most_plays_in_day=most_plays_in_day,
#         most_plays_in_day_date=most_plays_in_day_date,
#         avg_plays_per_month=avg_plays_per_month
#     )


# def album_sum_stats(album_df):
#     album_df['ts'] = pd.to_datetime(album_df['ts'])
#     album_df = album_df.sort_values('ts')
    
#     tot_plays = len(album_df)
#     tot_hours = album_df['ms_played'].sum() / MS_HOUR_CONVERSION
#     unique_songs = album_df['master_metadata_track_name'].nunique()

#     first_row = album_df.iloc[0]
#     last_row = album_df.iloc[-1]

#     album_df['month_year'] = album_df['ts'].dt.to_period('M')
#     peak_month = album_df['month_year'].value_counts().idxmax()
#     peak_month_count = album_df['month_year'].value_counts().max()

#     album_df['date'] = album_df['ts'].dt.to_period('D')
#     most_plays_in_day_date = album_df['date'].value_counts().idxmax()
#     most_plays_in_day = album_df['date'].value_counts().max()
    
#     timespan = (album_df['ts'].iloc[-1] - album_df['ts'].iloc[0]).days
#     avg_plays_per_month = tot_plays / (max(timespan, 1) / DAYS_PER_MONTH)

#     years_active = album_df['ts'].dt.year.nunique()
    
#     actual_name = album_df['master_metadata_album_album_name'].iloc[0]

#     full_hist = album_df.groupby('master_metadata_track_name').agg({
#         'ts': 'count',
#         'ms_played': 'sum',
#         'skipped': lambda x: (x == False).sum()
#     }).reset_index().rename(columns={
#         'master_metadata_track_name': 'Song',
#         'ts': 'Listens',
#         'skipped': 'Full Listens'
#     }).sort_values('Listens', ascending=False)
#     full_hist['Total Minutes'] = full_hist['ms_played'] / MS_MIN_CONVERSION
#     full_hist = full_hist.drop(columns=['ms_played'])
#     top_songs = full_hist.head(Config().top_n)

#     return AlbumStats(
#         album_name=actual_name,
#         artist_name=album_df['master_metadata_album_artist_name'].iloc[0],
#         tot_plays=tot_plays,
#         tot_hours=tot_hours,
#         unique_songs=unique_songs,
#         first_song_row=first_row,
#         last_song_row=last_row,
#         peak_month=peak_month,
#         peak_month_count=peak_month_count,
#         years_active=years_active,
#         top_songs=top_songs,
#         full_hist=full_hist,
#         most_plays_in_day=most_plays_in_day,
#         most_plays_in_day_date=most_plays_in_day_date,
#         avg_plays_per_month=avg_plays_per_month,
#         unique_albums=0
#     )

@st.cache_data
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
    monthly_counts['month'] = monthly_counts['month'].map(MONTHS)

    return PolarPlotData(
        hourly_counts=hourly_counts,
        daily_counts_week=daily_counts_week,
        daily_counts_month=daily_counts_month,
        monthly_counts=monthly_counts
    )
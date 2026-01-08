from dataclasses import dataclass
import pandas as pd
from typing import Tuple

DAYS_OF_WEEK = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
MONTHS = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
          7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
DATE_SUFFIX = {1: 'st', 2: 'nd', 3: 'rd', 4: 'th', 5: 'th', 6: 'th', 7: 'th', 8: 'th', 9: 'th', 10: 'th',
               11: 'th', 12: 'th', 13: 'th', 14: 'th', 15: 'th', 16: 'th', 17: 'th', 18: 'th', 19: 'th', 20: 'th',
               21: 'st', 22: 'nd', 23: 'rd', 24: 'th', 25: 'th', 26: 'th', 27: 'th', 28: 'th', 29: 'th', 30: 'th',
               31: 'st'}

@dataclass
class Config:
    top_n: int = 5
    min_plays_skip_analysis: int = 20
    min_plays_artist_skip_analysis: int = 100

@dataclass
class SongStats:
    name: str
    artist: str
    album: str
    first_listen: pd.Timestamp
    last_listen: pd.Timestamp
    timespan: int
    tot_plays: int
    tot_skips: int
    full_plays: int
    listen_rate: float
    tot_hours: float
    avg_plays_per_month: float
    most_plays_in_day: int
    most_plays_in_day_date: pd.Period
    peak_month: pd.Period
    peak_month_count: int

@dataclass
class ArtistAlbumStats:
    artist_name: str
    album_name: str
    tot_plays: int
    tot_hours: float
    unique_songs: int
    unique_albums: int
    first_song_row: pd.Series
    last_song_row: pd.Series
    peak_month: pd.Period
    peak_month_count: int
    years_active: int
    top_songs: pd.DataFrame
    full_hist: pd.DataFrame
    most_plays_in_day: int
    most_plays_in_day_date: pd.Period
    avg_plays_per_month: float

@dataclass
class ArtistStats:
    artist_name: str
    tot_plays: int
    tot_hours: float
    unique_songs: int
    unique_albums: int
    first_song_row: pd.Series
    last_song_row: pd.Series
    peak_month: pd.Period
    peak_month_count: int
    years_active: int
    top_songs: pd.DataFrame
    full_hist: pd.DataFrame
    most_plays_in_day: int
    most_plays_in_day_date: pd.Period
    avg_plays_per_month: float

@dataclass
class AlbumStats(ArtistStats):
    album_name: str

@dataclass
class BasicStats:
    total_plays: int
    total_plays_no_skips: int
    skip_percentage: float
    total_minutes: float
    unique_tracks: int
    unique_artists: int
    unique_albums: int

@dataclass
class FirstLastPlay:
    first_play: Tuple
    last_play: Tuple
    timespan: int

@dataclass
class TopResults:
    all_data: pd.DataFrame
    by_plays: pd.DataFrame
    by_no_skips: pd.DataFrame
    by_minutes: pd.DataFrame
    by_mean_minutes: pd.DataFrame
    lowest_skip: pd.DataFrame
    highest_skip: pd.DataFrame

@dataclass
class TopArtistResults:
    all_data: pd.DataFrame
    by_plays: pd.DataFrame
    by_no_skips: pd.DataFrame
    by_time: pd.DataFrame
    by_diversity: pd.DataFrame
    lowest_skip: pd.DataFrame
    highest_skip: pd.DataFrame

@dataclass
class PolarPlotData:
    hourly_counts: pd.DataFrame
    daily_counts_week: pd.DataFrame
    daily_counts_month: pd.DataFrame
    monthly_counts: pd.DataFrame
import pandas as pd
import streamlit as st
from config import COLUMNS_TO_DROP

def load_parquet_file(file):
    """Load a parquet file and return a DataFrame"""
    return pd.read_parquet(file)

def load_and_process_json_files(files):
    """Load multiple JSON files and process them into a single DataFrame"""
    # Concatenate all JSON files
    alldata = pd.concat([pd.read_json(path) for path in files])
    
    # Drop unwanted columns
    df = alldata.drop(columns=COLUMNS_TO_DROP)
    
    # Convert timestamp to datetime
    df['ts'] = pd.to_datetime(df['ts'])
    
    # Create consistent URI mapping
    uri_mapping = (
        df.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name'])
        ['spotify_track_uri']
        .first()
        .reset_index()
    )
    
    df = df.merge(
        uri_mapping,
        on=['master_metadata_track_name', 'master_metadata_album_artist_name'],
        suffixes=('_old', '')
    )
    
    df = df.drop(columns=['spotify_track_uri_old'])
    
    return df

def create_parquet_buffer(df):
    """Create a BytesIO buffer containing the dataframe as parquet"""
    import io
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    return buffer
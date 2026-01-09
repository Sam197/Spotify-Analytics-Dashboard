import streamlit as st
import pandas as pd

def get_date_range_filter(df):
    """
    Display date range selection UI and return filtered dataframe
    
    Returns:
        tuple: (filtered_df, start_date, end_date)
    """
    min_date = df['ts'].min().date()
    max_date = df['ts'].max().date() + pd.Timedelta('1d')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Want to look at a certain date range?")
        selected_dates = st.date_input(
            "Select Date Range",
            value=[min_date, max_date]
        )
    
    with col2:
        st.subheader("Or look at all your history?")
        use_all_history = st.checkbox("Look at all History?")
    
    # Determine date range
    if use_all_history:
        start_date, end_date = min_date, max_date
    else:
        start_date, end_date = selected_dates
    
    # Convert to datetime and localize to UTC
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Handle timezone awareness
    if df['ts'].dt.tz is not None:
        if start_date.tz is None:
            start_date = start_date.tz_localize('UTC')
        if end_date.tz is None:
            end_date = end_date.tz_localize('UTC')
    
    # Filter dataframe
    mask = (df['ts'] >= start_date) & (df['ts'] <= end_date)
    filtered_df = df.loc[mask]
    
    return filtered_df, start_date, end_date
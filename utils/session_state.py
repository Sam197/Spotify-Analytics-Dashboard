import streamlit as st
from config import SessionKeys

def initialize_session_state():
    """Initialize all session state variables in one place"""
    if SessionKeys.DATA not in st.session_state:
        st.session_state[SessionKeys.DATA] = None
    
    if SessionKeys.HAS_INITIAL_DATA not in st.session_state:
        st.session_state[SessionKeys.HAS_INITIAL_DATA] = False
    
    if SessionKeys.PREVIOUS_RAND not in st.session_state:
        st.session_state[SessionKeys.PREVIOUS_RAND] = None

def reset_random_selection():
    """Reset the random track selection"""
    st.session_state[SessionKeys.PREVIOUS_RAND] = None

def set_data(df):
    """Set the main dataframe in session state"""
    st.session_state[SessionKeys.DATA] = df.copy(deep=True)

def get_data():
    """Get the main dataframe from session state"""
    return st.session_state[SessionKeys.DATA]

def has_data():
    """Check if data has been loaded"""
    return st.session_state[SessionKeys.DATA] is not None

def surprise_me_reset(page):
    if page != st.session_state.current_page:
        st.session_state.previous_rand = None
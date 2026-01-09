import streamlit as st
from utils.session_state import initialize_session_state, surprise_me_reset
from config import APP_CONFIG

# Page configuration
st.set_page_config(
    page_title=APP_CONFIG['page_title'],
    layout=APP_CONFIG['layout'],
    page_icon=APP_CONFIG['page_icon']
)

# Initialize session state
initialize_session_state()

# Initialize page selection in session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Upload'

# Display logo and navigation in sidebar if data is loaded
if st.session_state.has_initial_data:
    st.logo('utils/logo.jpg', size='large')
    st.sidebar.title("Navigate")
    
    # Manual page navigation to control order
    page = st.sidebar.radio(
        "Navigate",
        ['Upload', 'Home', 'Track', 'Artist', 'Album']
    )
    surprise_me_reset(page)
    # Update current page
    st.session_state.current_page = page

    st.sidebar.markdown(
        "Checkout the [GitHub Repository](https://github.com/Sam197/Spotify-Analytics-Dashboard)!"
    )
else:
    # Force to Upload page if no data
    st.session_state.current_page = 'Upload'

# Import and render the appropriate page
if st.session_state.current_page == 'Upload':
    from pa import upload
    upload.render()
elif st.session_state.current_page == 'Home':
    from pa import home
    home.render()
elif st.session_state.current_page == 'Track':
    from pa import track
    track.render()
elif st.session_state.current_page == 'Artist':
    from pa import artist
    artist.render()
elif st.session_state.current_page == 'Album':
    from pa import album
    album.render()
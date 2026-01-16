import streamlit as st
from utils.session_state import set_data, has_data
from utils.data_processing import load_parquet_file, load_and_process_json_files, create_parquet_buffer
from config import UPLOAD_FILES_HELP_TEXT, DOWNLOAD_FILE_HELP_TEXT

def render():
    st.title("📊 Spotify Analytics Dashboard")

    if not has_data():
        st.markdown("### Upload your data to get started")
    else:
        st.markdown("### Upload different data?")

    st.write(
        "Don't know how to get your Spotify data? Request your 'Extended Streaming History' "
        "from [Spotify here](https://www.spotify.com/uk/account/privacy/). "
        "Once you have the data, upload the JSON files here to get started!"
    )

    uploaded_files = st.file_uploader(
        "Choose files",
        type=['json', 'parquet'],
        help=UPLOAD_FILES_HELP_TEXT,
        accept_multiple_files=True
    )

    if uploaded_files:
        # Check if any parquet files were uploaded
        if any(file.name.endswith('.parquet') for file in uploaded_files):
            df = load_parquet_file(uploaded_files[0])
        else:
            df = load_and_process_json_files(uploaded_files)
        
        set_data(df)
        st.success(f"✅ Successfully loaded {len(df)} rows and {len(df.columns)} columns!")
        
        if not st.session_state.has_initial_data:
            st.write("Loading Landing Page!")
            st.session_state.has_initial_data = True
            st.rerun()
    else:
        if not st.session_state.has_initial_data:
            st.info("Please upload .json files, or a .parquet file to begin analysis")
        else:
            st.info("You can analyse different data if you upload new stuff here!")

    # Show download and data preview if data is loaded
    if has_data():
        st.write("Do you want to save the loaded dataset for quicker uploads next time?")
        
        buffer = create_parquet_buffer(st.session_state.data)
        
        col1, col2 = st.columns([5, 1])
        with col1:
            filename = st.text_input(
                "Enter filename to save as (without extension)",
                placeholder="my_spotify_data",
                help=DOWNLOAD_FILE_HELP_TEXT
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("**.parquet**  ")
        
        # Determine final filename
        if not filename:
            final_filename = "my_spotify_data.parquet"
        elif filename.endswith(".parquet"):
            final_filename = filename
        else:
            final_filename = f"{filename}.parquet"
        
        st.download_button(
            "Download Current Dataset",
            data=buffer.getvalue(),
            file_name=final_filename,
            mime="application/octet-stream"
        )
        
        st.divider()
        st.subheader("Your Data")
        st.dataframe(st.session_state.data)
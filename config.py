# Application configuration
APP_CONFIG = {
    'page_title': 'Music Analytics',
    'layout': 'wide',
    'page_icon': 'utils/logo.jpg'
}

# Column names to drop from raw Spotify data
COLUMNS_TO_DROP = [
    "ip_addr",
    "episode_show_name",
    'audiobook_title',
    'audiobook_uri',
    'audiobook_chapter_uri',
    'audiobook_chapter_title',
    'episode_name',
    'spotify_episode_uri'
]

# Help text constants
UPLOAD_FILES_HELP_TEXT = """
Upload Spotify Data here. You can either upload the JSON files you download from Spotify or
a previously saved Parquet file for faster loading. If you upload JSON files, they will be
processed and you will have the option to save the combined dataset as a Parquet file for future use.
Only JSON and Parquet files are supported.
"""

DOWNLOAD_FILE_HELP_TEXT = """
You can download your current dataset as a Parquet file for faster loading next time.
Simply provide a filename (without extension), hit enter, and click the download button.
"""

# Session state keys
class SessionKeys:
    DATA = 'data'
    HAS_INITIAL_DATA = 'has_initial_data'
    PREVIOUS_RAND = 'previous_rand'

spotify_palette = [
    "#0C7230", '#8D67AB', '#19E3E0', '#E91E63', '#4587F7', 
    '#FF5722', '#00897B', '#F4C430', '#3F51B5', '#607D8B'
]

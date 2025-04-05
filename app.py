import streamlit as st
from src.config import UI_CONFIG
from src.ui.styles import load_css
from src.ui.single_video import display_single_video_ui
from src.ui.playlist import display_playlist_ui
# Import the FFmpeg manager - just importing it ensures FFmpeg is configured
import src.ffmpeg.manager

# Set page config
st.set_page_config(**UI_CONFIG)

# Load custom CSS
load_css()

# Main title and description
st.title("YouTube Video Downloader")
st.markdown("Download videos for your web projects")

# Tabs for different functions
tab1, tab2 = st.tabs(["🎥 Single Video", "📚 Playlist"])

with tab1:
    display_single_video_ui()

with tab2:
    display_playlist_ui()

# Footer
st.markdown("---")
st.markdown("Made with ❤️ for web development students")
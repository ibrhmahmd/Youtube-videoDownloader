import streamlit as st
from src.core.downloader import download_video
from src.utils.file_handler import create_directories, get_temp_file_path, cleanup_old_files, remove_file

# Set page config
st.set_page_config(
    page_title="YouTube Video Downloader",
    page_icon="🎥",
    layout="centered"
)

# Create necessary directories
create_directories()

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 10px;
        background-color: #FF0000;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #CC0000;
    }
    .download-link {
        display: inline-block;
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        margin-top: 10px;
    }
    .download-link:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# Main title and description
st.title("YouTube Video Downloader")
st.markdown("Download videos for your web projects")

# URL input
url = st.text_input("Enter YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

# Quality selection
quality = st.selectbox(
    "Select Video Quality",
    ["720p", "480p"],
    help="Choose the video quality you want to download"
)

# Download button
if st.button("Download Video"):
    if url:
        try:
            with st.spinner("Fetching video information..."):
                temp_path = get_temp_file_path()
                
                # Download video
                video_info = download_video(url, quality, temp_path)
                
                if video_info:
                    # Show video information
                    st.info(f"Video Title: {video_info['title']}")
                    st.info(f"Duration: {video_info['duration']} seconds")
                    
                    # Create download link
                    with open(video_info['path'], 'rb') as f:
                        st.download_button(
                            label="Click to Download Video",
                            data=f,
                            file_name=f"{video_info['title']}.mp4",
                            mime="video/mp4"
                        )
                    
                    # Clean up temporary file
                    remove_file(video_info['path'])
                    
                    # Success message
                    st.success(f"Video processed successfully!")
                
        except Exception as e:
            st.error(f"Error downloading video: {str(e)}")
            # Clean up any temporary files
            remove_file(temp_path)
    else:
        st.warning("Please enter a YouTube URL")

# Clean up old temporary files
cleanup_old_files()

# Footer
st.markdown("---")
st.markdown("Made with ❤️ for web development students")
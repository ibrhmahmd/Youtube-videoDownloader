import streamlit as st
import time
import webbrowser
from src.ui.helpers import get_downloader_for_url

def display_single_video_ui():
    """Display UI for downloading a single video"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        url = st.text_input("Enter YouTube URL", placeholder="https://www.youtube.com/watch?v=...", key="single_url")
    
    with col2:
        search_button = st.button("🔍 Search", key="search_button")
    
    # Return if no URL or search button not clicked
    if not url:
        return
        
    # Store the URL and video info in session state so they persist between interactions
    if "video_data" not in st.session_state:
        st.session_state.video_data = {"current_url": "", "video_info": None, "searched": False}
    
    # Process the URL only when search button is clicked or URL has changed
    url_changed = st.session_state.video_data["current_url"] != url
    if search_button or (url_changed and st.session_state.video_data["searched"]):
        st.session_state.video_data["current_url"] = url
        st.session_state.video_data["searched"] = True
        
        # Get downloader for this URL
        downloader = get_downloader_for_url(url)
        if not downloader:
            st.error("Unsupported URL. Currently only YouTube videos are supported.")
            st.session_state.video_data["video_info"] = None
            return
            
        with st.spinner("Fetching video information..."):
            video_info = downloader.get_video_info(url)
            st.session_state.video_data["video_info"] = video_info
            
    # Get video info from session state
    video_info = st.session_state.video_data["video_info"]
    
    # Only proceed if we have video info
    if not video_info:
        if st.session_state.video_data["searched"]:
            st.error("Could not fetch video information. Please check the URL.")
        return
    
    # Display thumbnail if available
    if hasattr(video_info, 'thumbnail_url') and video_info.thumbnail_url:
        st.image(video_info.thumbnail_url, use_container_width=True)
    
    st.info(f"Video Title: {video_info.title}")
    
    # Format duration
    mins, secs = divmod(video_info.duration, 60)
    hours, mins = divmod(mins, 60)
    duration_str = f"{hours:02d}:{mins:02d}:{secs:02d}" if hours else f"{mins:02d}:{secs:02d}"
    st.info(f"Duration: {duration_str}")
    
    quality = st.selectbox(
        "Select Video Quality",
        video_info.available_qualities,
        help="Choose the video quality you want to download"
    )
    
    # Create columns for download options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download via Browser (Streaming)"):
            with st.spinner("Preparing direct download stream..."):
                # Need to get the downloader again as it's not stored in session state
                downloader = get_downloader_for_url(url)
                
                # Get direct stream URL
                stream_info = downloader.get_direct_stream_url(url, quality)
                
                if stream_info['success']:
                    # Display a bit of information about the stream
                    file_size_mb = stream_info.get('file_size_mb', 0)
                    size_text = f" ({file_size_mb:.1f}MB)" if file_size_mb > 0 else ""
                    
                    # Determine file extension based on format
                    file_ext = "mp4"
                    if stream_info.get('is_webm', False):
                        file_ext = "webm"
                        
                    # Create a download link for the direct URL
                    st.markdown(f"""
                    ### 🎬 Your video is ready to download!
                    
                    Click the link below to start downloading directly from YouTube's servers{size_text}:
                    
                    <a href="{stream_info['direct_url']}" download="{stream_info['safe_title']}.{file_ext}" target="_blank" class="download-link">
                        💾 Download "{stream_info['title']}"
                    </a>
                    
                    Right-click the link and select "Save link as..." if the download doesn't start automatically.
                    """, unsafe_allow_html=True)
                    
                    # Show info about available mp4 formats if webm format was selected
                    if stream_info.get('is_webm', False) and stream_info.get('available_mp4_formats'):
                        st.warning("""
                        **Note:** The download link is for a WebM format video because YouTube didn't have an MP4 format 
                        available for this quality. WebM videos work in most modern browsers but may require VLC Media Player 
                        for playback on some devices.
                        """)
                else:
                    st.error(f"Failed to get direct download link: {stream_info.get('error', 'Unknown error')}")
    
    with col2:
        if st.button("Download via Server (In-Memory)"):
            # Display a progress container
            progress_container = st.container()
            progress_bar = progress_container.progress(0)
            status_text = progress_container.empty()
            
            with st.spinner(f"Preparing {video_info.title} for download..."):
                # Need to get the downloader again as it's not stored in session state
                downloader = get_downloader_for_url(url)
                start_time = time.time()
                
                # Show initial status
                status_text.text("Starting download...")
                
                # Define a callback to update progress
                file_size = 0
                max_size = 0
                
                def progress_hook(d):
                    nonlocal file_size, max_size
                    if d['status'] == 'downloading':
                        file_size = d.get('downloaded_bytes', 0)
                        max_size = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                        
                        # Calculate percentage
                        if max_size > 0:
                            percentage = file_size / max_size
                            progress_bar.progress(min(percentage, 1.0))
                        
                        # Show human-readable progress
                        downloaded_mb = file_size / (1024 * 1024)
                        total_mb = max_size / (1024 * 1024) if max_size else 0
                        
                        if total_mb > 0:
                            status_text.text(f"Downloaded: {downloaded_mb:.1f}MB of {total_mb:.1f}MB ({percentage*100:.1f}%)")
                        else:
                            status_text.text(f"Downloaded: {downloaded_mb:.1f}MB")
                
                # Download with progress hook
                result = downloader.download_video(url, quality, progress_hook=progress_hook)
                download_time = time.time() - start_time
                
                if result.success:
                    # Complete the progress bar
                    progress_bar.progress(1.0)
                    status_text.text(f"Download complete: {file_size/(1024*1024):.1f}MB")
                    
                    st.success(f"Video processed successfully in {download_time:.1f} seconds!")
                    
                    # Create download button
                    st.download_button(
                        label="Click to Download Video",
                        data=result.data,
                        file_name=f"{result.video_info['title']}.mp4",
                        mime="video/mp4"
                    )
                    
                    # Download tips
                    st.info("""
                    📝 **Download Tips**: 
                    - If download doesn't start automatically, right-click the button and select "Save link as..."
                    - For large videos, download may take a while to start in the browser
                    - The video is in MP4 format compatible with most devices
                    - For best playback results, use VLC media player
                    """)
                else:
                    st.error(f"Failed to download video: {result.error}") 
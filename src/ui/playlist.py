import streamlit as st
from src.ui.helpers import get_downloader_for_url

def display_playlist_ui():
    """Display UI for downloading a playlist"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        playlist_url = st.text_input("Enter Playlist URL", placeholder="https://www.youtube.com/playlist?list=...", key="playlist_url")
    
    with col2:
        search_button = st.button("🔍 Search", key="playlist_search_button")
    
    # Return if no URL
    if not playlist_url:
        return
    
    # Store the URL and playlist info in session state
    if "playlist_data" not in st.session_state:
        st.session_state.playlist_data = {
            "current_url": "", 
            "videos": None, 
            "selected_videos": None,
            "searched": False
        }
    
    # Process the URL only when search button is clicked or URL has changed
    url_changed = st.session_state.playlist_data["current_url"] != playlist_url
    if search_button or (url_changed and st.session_state.playlist_data["searched"]):
        st.session_state.playlist_data["current_url"] = playlist_url
        st.session_state.playlist_data["searched"] = True
        
        if "playlist" not in playlist_url.lower():
            st.error("Invalid playlist URL. Please enter a YouTube playlist URL.")
            st.session_state.playlist_data["videos"] = None
            return
        
        # Get downloader for this URL
        downloader = get_downloader_for_url(playlist_url)
        if not downloader:
            st.error("Unsupported URL. Currently only YouTube playlists are supported.")
            st.session_state.playlist_data["videos"] = None
            return
            
        with st.spinner("Fetching playlist videos..."):
            videos = downloader.get_playlist_videos(playlist_url)
            st.session_state.playlist_data["videos"] = videos
    
    # Get playlist videos from session state
    videos = st.session_state.playlist_data["videos"]
    
    if not videos:
        if st.session_state.playlist_data["searched"]:
            st.error("Could not fetch playlist videos. Please check the URL.")
        return
    
    st.success(f"Found {len(videos)} videos in playlist")
    
    # Let user select videos
    selected_videos = st.multiselect(
        "Select videos to download",
        videos,
        format_func=lambda x: get_downloader_for_url(x).get_video_info(x).title 
            if get_downloader_for_url(x) and get_downloader_for_url(x).get_video_info(x) else x
    )
    
    if not selected_videos:
        return
        
    # Get quality options from first video
    downloader = get_downloader_for_url(selected_videos[0])
    first_video_info = downloader.get_video_info(selected_videos[0])
    if not first_video_info:
        st.error("Could not fetch video information. Please try again.")
        return
        
    # Display thumbnail of first selected video
    if hasattr(first_video_info, 'thumbnail_url') and first_video_info.thumbnail_url:
        st.image(first_video_info.thumbnail_url, width=300, use_container_width=False)
        
    quality = st.selectbox(
        "Select Video Quality for all videos",
        first_video_info.available_qualities,
        help="Choose the video quality you want to download"
    )
    
    # Create columns for download method selection
    method_col1, method_col2 = st.columns(2)
    
    with method_col1:
        stream_download = st.button("Download via Browser (Streaming)")
        
    with method_col2:
        memory_download = st.button("Download via Server (In-Memory)")
    
    # Streaming download option
    if stream_download:
        st.subheader("Direct Download Links")
        st.info("Click each link to download directly from YouTube's servers.")
        
        with st.spinner("Preparing direct download links..."):
            # List to track successful links
            stream_links = []
            
            # Create an expander for each video
            for i, video_url in enumerate(selected_videos):
                # Get downloader for this video
                downloader = get_downloader_for_url(video_url)
                
                # Get video info
                video_info = downloader.get_video_info(video_url)
                if not video_info:
                    continue
                
                # Get direct stream URL
                stream_info = downloader.get_direct_stream_url(video_url, quality)
                
                if stream_info['success']:
                    stream_links.append(stream_info)
                    
            # Display success message
            if stream_links:
                st.success(f"Generated {len(stream_links)} direct download links")
                
                # Display each download link
                for i, stream_info in enumerate(stream_links):
                    # Display information
                    with st.expander(f"{i+1}. {stream_info['title']}"):
                        # Display some info about the video
                        file_size_mb = stream_info.get('file_size_mb', 0)
                        size_text = f"Size: {file_size_mb:.1f}MB" if file_size_mb > 0 else "Size: Unknown"
                        
                        # Determine file extension based on format
                        file_ext = "mp4"
                        if stream_info.get('is_webm', False):
                            file_ext = "webm"
                        
                        st.markdown(f"""
                        **Quality:** {stream_info['quality']}  
                        **{size_text}**
                        
                        <a href="{stream_info['direct_url']}" download="{stream_info['safe_title']}.{file_ext}" target="_blank" class="download-link">
                            💾 Download Video
                        </a>
                        
                        Right-click the link and select "Save link as..." if the download doesn't start automatically.
                        """, unsafe_allow_html=True)
                
                # Add note about playback
                st.info("""
                📝 **Download Tips**: 
                - If downloads don't start automatically, right-click the links and select "Save link as..."
                - Some videos may download as WebM format if MP4 is not available at the selected quality
                - All videos are compatible with most modern browsers
                - For best playback results, use VLC media player
                """)
            else:
                st.error("Failed to generate any direct download links")
    
    # In-memory download option (original code)
    if memory_download:
        progress_bar = st.progress(0)
        status_text = st.empty()
        file_progress = st.empty()
        
        # Track overall progress
        total_videos = len(selected_videos)
        completed_videos = 0
        total_bytes_downloaded = 0
        
        # Update the overall progress bar
        status_text.text(f"Downloading {total_videos} videos (0%)")
        
        downloaded = []
        for i, video_url in enumerate(selected_videos):
            downloader = get_downloader_for_url(video_url)
            video_info = downloader.get_video_info(video_url)
            if not video_info:
                continue
                
            video_status = f"Downloading {i+1}/{total_videos}: {video_info.title}"
            status_text.text(video_status)
            
            # Define progress hook for current video
            current_bytes = 0
            max_bytes = 0
            
            def progress_hook(d):
                nonlocal current_bytes, max_bytes
                if d['status'] == 'downloading':
                    current_bytes = d.get('downloaded_bytes', 0)
                    max_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                    
                    # Show file size progress
                    downloaded_mb = current_bytes / (1024 * 1024)
                    total_mb = max_bytes / (1024 * 1024) if max_bytes else 0
                    
                    if total_mb > 0:
                        percentage = current_bytes / max_bytes * 100
                        file_progress.text(f"Current file: {downloaded_mb:.1f}MB of {total_mb:.1f}MB ({percentage:.1f}%)")
                    else:
                        file_progress.text(f"Current file: {downloaded_mb:.1f}MB downloaded")
            
            # Download with progress hook
            result = downloader.download_video(video_url, quality, progress_hook=progress_hook)
            
            if result.success:
                # Add file size to total
                file_size = current_bytes or result.video_info.get('file_size', 0)
                total_bytes_downloaded += file_size
                
                downloaded.append({
                    'title': result.video_info['title'],
                    'data': result.data,
                    'file_size': file_size
                })
                
                # Update completed count
                completed_videos += 1
            
            # Update overall progress
            progress_percentage = completed_videos / total_videos
            progress_bar.progress(progress_percentage)
            
            # Show overall progress with MB
            total_mb_downloaded = total_bytes_downloaded / (1024 * 1024)
            status_text.text(f"Downloaded {completed_videos}/{total_videos} videos ({total_mb_downloaded:.1f}MB total)")
        
        if downloaded:
            # Calculate total size
            total_size_mb = sum(video.get('file_size', 0) for video in downloaded) / (1024 * 1024)
            
            st.success(f"Successfully downloaded {len(downloaded)} videos ({total_size_mb:.1f}MB)")
            
            # Create download buttons for each video
            for i, video in enumerate(downloaded):
                # Get file size in MB
                video_size_mb = video.get('file_size', 0) / (1024 * 1024)
                
                st.download_button(
                    label=f"Click to Download: {video['title']} ({video_size_mb:.1f}MB)",
                    data=video['data'],
                    file_name=f"{video['title']}.mp4",
                    mime="video/mp4",
                    key=video['title']
                )
                
                # Add note about playback
                if i == 0:  # Only show the note once
                    st.info("""
                    📝 **Download Tips**: 
                    - If downloads don't start automatically, right-click the button and select "Save link as..."
                    - For large videos, download may take a while to start in the browser
                    - All videos are in MP4 format compatible with most devices
                    - For best playback results, use VLC media player
                    """)
        else:
            st.error("Failed to download any videos")
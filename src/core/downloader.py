from pytube import YouTube
import os
from pathlib import Path
import streamlit as st
import re

def get_video_stream(url, quality):
    """Get the appropriate video stream based on quality"""
    try:
        # Initialize YouTube with additional parameters
        yt = YouTube(
            url,
            use_oauth=False,
            allow_oauth_cache=True,
            proxies=None,
            on_progress_callback=None,
            on_complete_callback=None
        )
        
        # Wait for the video to be ready
        yt.check_availability()
        
        # Convert quality string (e.g., "720p") to resolution number
        target_resolution = int(quality[:-1])
        
        # Get available streams with more flexible filtering
        streams = yt.streams.filter(
            type='video',
            file_extension='mp4',
            progressive=True
        )
        
        if not streams:
            # Try without progressive filter
            streams = yt.streams.filter(
                type='video',
                file_extension='mp4'
            )
        
        if not streams:
            st.error("No streams available for this video")
            return None, None
            
        # Get the highest quality stream that's not above target resolution
        stream = streams.filter(
            resolution=f"{target_resolution}p"
        ).first()
        
        if not stream:
            # If exact resolution not found, get the highest quality below target
            stream = streams.filter(
                resolution__lte=f"{target_resolution}p"
            ).order_by('resolution').desc().first()
        
        if not stream:
            st.error(f"No suitable stream found for quality {quality}")
            return None, None
            
        return stream, yt
    except Exception as e:
        error_msg = str(e)
        if "400" in error_msg:
            st.error("Unable to access video. This might be due to YouTube's security measures. Please try again in a few minutes.")
        elif "403" in error_msg:
            st.error("Access to this video is forbidden. It might be age-restricted or private.")
        elif "Video unavailable" in error_msg:
            st.error("This video is unavailable. It might have been removed or made private.")
        else:
            st.error(f"Error getting video stream: {error_msg}")
        return None, None

def download_video(url, quality, temp_path):
    """Download video and return video info"""
    try:
        stream, yt = get_video_stream(url, quality)
        
        if not stream:
            return None
            
        # Download the video with progress tracking
        stream.download(
            output_path=str(temp_path.parent),
            filename=temp_path.name,
            skip_existing=False
        )
        
        return {
            'title': yt.title,
            'duration': yt.length,
            'path': temp_path
        }
    except Exception as e:
        st.error(f"Error downloading video: {str(e)}")
        return None 
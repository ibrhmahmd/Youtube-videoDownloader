import yt_dlp
import os
from pathlib import Path
import streamlit as st

def get_download_options(quality):
    """Get yt-dlp options for video download"""
    return {
        # Use format that includes both video and audio
        'format': f'best[height<={quality[:-1]}][ext=mp4]',
        'progress': True,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'prefer_insecure': False,
    }

def download_video(url, quality, temp_path):
    """Download video and return video info"""
    ydl_opts = get_download_options(quality)
    ydl_opts['outtmpl'] = str(temp_path)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Get video info first
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            # Download the video
            ydl.download([url])
            
            return {
                'title': video_title,
                'duration': duration,
                'path': temp_path
            }
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None 
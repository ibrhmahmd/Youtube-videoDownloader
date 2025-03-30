import yt_dlp
import os
from pathlib import Path
import sys
from datetime import datetime
import streamlit as st

def get_download_options(quality, ffmpeg_path):
    """Get yt-dlp options for video download"""
    return {
        'format': f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]',
        'progress': True,
        'quiet': True,
        'merge_output_format': 'mp4',
        'ffmpeg_location': str(ffmpeg_path),
    }

def download_video(url, quality, temp_path):
    """Download video and return video info"""
    ffmpeg_path = Path(sys.prefix) / ('Scripts' if os.name == 'nt' else 'bin') / ('ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
    
    ydl_opts = get_download_options(quality, ffmpeg_path)
    ydl_opts['outtmpl'] = str(temp_path)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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
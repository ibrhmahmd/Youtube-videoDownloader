from typing import List, Optional
import re
import io
import yt_dlp
from .base import BaseDownloader, VideoInfo, DownloadResult

class YouTubeDownloader(BaseDownloader):
    """YouTube video downloader implementation using yt-dlp"""
    
    SUPPORTED_QUALITIES = ["1080p", "720p", "480p", "360p", "240p", "144p"]
    
    def supports_url(self, url: str) -> bool:
        """Check if URL is a valid YouTube URL"""
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        return bool(re.match(youtube_regex, url))
    
    def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """Get video information without downloading"""
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Create more flexible filtering to find more format options
                qualities = []
                
                # First find formats with both audio and video in one stream (easier to play)
                combined_formats = [
                    f for f in info['formats'] 
                    if f.get('ext') == 'mp4' and f.get('acodec') != 'none' and f.get('vcodec') != 'none'
                ]
                
                # Get qualities from combined formats
                for f in combined_formats:
                    if f.get('height') and f"{f['height']}p" in self.SUPPORTED_QUALITIES:
                        qualities.append(f"{f['height']}p")
                        
                # If combined formats don't provide enough options, 
                # look at all available video formats
                if len(qualities) <= 1:
                    video_formats = [
                        f for f in info['formats'] 
                        if f.get('vcodec') != 'none' and f.get('height')
                    ]
                    
                    for f in video_formats:
                        if f"{f['height']}p" in self.SUPPORTED_QUALITIES:
                            qualities.append(f"{f['height']}p")
                
                # Remove duplicates and sort
                qualities = sorted(list(set(qualities)), key=lambda x: int(x.rstrip('p')), reverse=True)
                
                # Get thumbnail URL
                thumbnail_url = info.get('thumbnail', '')
                
                # If no qualities found, use default supported qualities
                if not qualities:
                    qualities = self.SUPPORTED_QUALITIES
                
                video_info = VideoInfo(
                    title=info['title'],
                    duration=info['duration'],
                    url=url,
                    available_qualities=qualities
                )
                
                # Add thumbnail URL as a custom attribute
                video_info.thumbnail_url = thumbnail_url
                
                return video_info
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return None
    
    def download_video(self, url: str, quality: str, progress_hook=None) -> DownloadResult:
        """Download a single video
        
        Args:
            url (str): YouTube video URL
            quality (str): Video quality (e.g. "720p")
            progress_hook (callable, optional): Progress hook function for tracking download progress
            
        Returns:
            DownloadResult: Download result with video data and info
        """
        try:
            height = int(quality.rstrip('p'))
            
            # Create format selection based on quality with explicit MP4 preference
            if height >= 720:
                format_str = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best[height<={height}][ext=mp4]/best[height<={height}]'
            else:
                format_str = f'best[height<={height}][ext=mp4]/best[height<={height}]'
            
            # Select format that's more likely to be compatible with most players
            ydl_opts = {
                'format': format_str,
                'quiet': True,
                'logtostderr': False,
                'noprogress': False,  # We need progress for the progress_hook
                'noplaylist': True,
                'skip_download': False,
                # Prefer mp4 format which has widest compatibility
                'merge_output_format': 'mp4',
                # Force mp4 output with compatible codecs
                'postprocessor_args': {
                    'ffmpeg': ['-c:v', 'libx264', '-c:a', 'aac']
                },
            }
            
            # Add progress hooks if provided
            if progress_hook:
                ydl_opts['progress_hooks'] = [progress_hook]
            
            # Get info first
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
            
            # Direct download to file
            import tempfile
            import os
            
            # Create a temp directory to store the download
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_filename = os.path.join(temp_dir, "video.mp4")
                
                # Set output template
                ydl_opts['outtmpl'] = temp_filename
                
                # Download the video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Check if file exists
                if not os.path.exists(temp_filename):
                    # Try to find any file created in the temp directory
                    files = os.listdir(temp_dir)
                    if files:
                        temp_filename = os.path.join(temp_dir, files[0])
                    else:
                        return DownloadResult(success=False, error="Failed to download video. No output file created.")
                
                # Read file into buffer
                with open(temp_filename, 'rb') as f:
                    video_data = f.read()
            
            # Extract title and duration properly
            title = info.get('title', 'Video')
            duration = info.get('duration', 0)
            if isinstance(duration, str):
                try:
                    duration = int(duration)
                except ValueError:
                    duration = 0
                    
            # Get thumbnail URL
            thumbnail_url = info.get('thumbnail', '')
            
            # Get file size
            file_size = len(video_data)
            
            return DownloadResult(
                success=True,
                data=video_data,
                video_info={
                    'title': title,
                    'duration': duration,
                    'quality': quality,
                    'thumbnail_url': thumbnail_url,
                    'file_size': file_size
                }
            )
        except Exception as e:
            print(f"Download error: {str(e)}")
            return DownloadResult(success=False, error=str(e))
    
    def get_playlist_videos(self, url: str) -> List[str]:
        """Get list of video URLs from a playlist"""
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(url, download=False)
                
                if 'entries' in playlist_info:
                    video_urls = []
                    for entry in playlist_info['entries']:
                        if entry.get('url'):
                            video_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
                    return video_urls
                
            return []
        except Exception as e:
            print(f"Playlist error: {str(e)}")
            return []

    def get_direct_stream_url(self, url: str, quality: str) -> dict:
        """Get direct stream URL for a YouTube video without downloading it
        
        Args:
            url (str): YouTube video URL
            quality (str): Video quality (e.g. "720p")
            
        Returns:
            dict: Dictionary with direct URL and video information
        """
        try:
            height = int(quality.rstrip('p'))
            
            # Create format selection based on quality with explicit MP4 preference
            # The format string prioritizes mp4 and explicitly excludes webm
            if height >= 720:
                format_str = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best[height<={height}][ext=mp4]/best[height<={height}]'
            else:
                format_str = f'best[height<={height}][ext=mp4]/best[height<={height}]'
            
            # Configure yt-dlp to get direct URLs with mp4 preference
            ydl_opts = {
                'format': format_str,
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,  # Don't download, just get info
                'youtube_include_dash_manifest': False,
                'merge_output_format': 'mp4',  # Force MP4 output
                'postprocessor_args': {
                    'ffmpeg': ['-c:v', 'libx264', '-c:a', 'aac']  # Use standard mp4 codecs
                },
            }
            
            # Get video info and URL
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Get the best format matching our criteria
                if 'url' in info:
                    # Single format case
                    direct_url = info['url']
                    
                    # Check if it's a webm format and warn
                    is_webm = False
                    if 'ext' in info and info['ext'] == 'webm':
                        is_webm = True
                        print("Warning: Selected format is webm despite requesting mp4")
                        
                    file_size = info.get('filesize') or info.get('filesize_approx', 0)
                elif 'requested_formats' in info:
                    # Multiple formats case (video+audio)
                    # Check format of first stream (usually video)
                    formats = info['requested_formats']
                    main_format = formats[0]
                    
                    # Check if it's a webm format and warn
                    is_webm = False
                    if 'ext' in main_format and main_format['ext'] == 'webm':
                        is_webm = True
                        print(f"Warning: Selected format is {main_format['ext']} despite requesting mp4")
                    
                    direct_url = main_format['url']
                    file_size = sum(f.get('filesize', 0) or f.get('filesize_approx', 0) 
                                    for f in formats)
                else:
                    return {
                        'success': False,
                        'error': 'Could not find direct URL in the video info'
                    }
                
                # Get filename safe title
                import re
                safe_title = re.sub(r'[^\w\-_\. ]', '_', info['title'])
                
                # Include format information in the response
                formats_info = []
                if 'formats' in info:
                    # Get available mp4 formats for debugging
                    mp4_formats = [f for f in info['formats'] if f.get('ext') == 'mp4']
                    for f in mp4_formats[:3]:  # Just include a few for reference
                        formats_info.append({
                            'format_id': f.get('format_id', ''),
                            'ext': f.get('ext', ''),
                            'resolution': f"{f.get('width', '')}x{f.get('height', '')}"
                        })
                
                return {
                    'success': True,
                    'direct_url': direct_url,
                    'title': info['title'],
                    'safe_title': safe_title,
                    'duration': info.get('duration', 0),
                    'file_size': file_size,
                    'file_size_mb': file_size / (1024 * 1024) if file_size else 0,
                    'thumbnail_url': info.get('thumbnail', ''),
                    'quality': quality,
                    'is_webm': is_webm,
                    'available_mp4_formats': formats_info
                }
                
        except Exception as e:
            print(f"Error getting direct URL: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

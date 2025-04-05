from typing import Dict, Type
from src.Core.base import BaseDownloader
from src.Core.youtube import YouTubeDownloader

# Mapping of supported downloaders
DOWNLOADERS: Dict[str, Type[BaseDownloader]] = {
    "youtube": YouTubeDownloader
}

# Default supported qualities (from lowest to highest)
DEFAULT_QUALITIES = ["144p", "240p", "360p", "480p", "720p", "1080p"]

# UI Configuration
UI_CONFIG = {
    "page_title": "Video Downloader",
    "page_icon": "🎥",
    "layout": "centered"
}

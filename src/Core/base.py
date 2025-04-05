from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class VideoInfo:
    title: str
    duration: int
    url: str
    available_qualities: List[str]
    thumbnail_url: str = ""

@dataclass
class DownloadResult:
    success: bool
    data: Optional[bytes] = None
    error: Optional[str] = None
    video_info: Optional[Dict[str, Any]] = None

class BaseDownloader(ABC):
    """Base class for video downloaders"""
    
    @abstractmethod
    def get_video_info(self, url: str) -> VideoInfo:
        """Get video information without downloading"""
        pass
    
    @abstractmethod
    def download_video(self, url: str, quality: str) -> DownloadResult:
        """Download a single video"""
        pass
    
    @abstractmethod
    def get_playlist_videos(self, url: str) -> List[str]:
        """Get list of video URLs from a playlist"""
        pass

    @abstractmethod
    def supports_url(self, url: str) -> bool:
        """Check if the URL is supported by this downloader"""
        pass

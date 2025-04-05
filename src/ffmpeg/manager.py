"""
FFmpeg Manager Module

This module provides a centralized way to check, download, and configure FFmpeg.
It will automatically download FFmpeg if not found on the system.
"""

import os
import sys
import zipfile
import subprocess
import platform
import tempfile
from urllib.request import urlretrieve
from dotenv import load_dotenv

# Path constants
FFMPEG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ffmpeg_bin')
ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')

# Flag to track if FFmpeg has been configured
_ffmpeg_configured = False


def _download_progress(count, block_size, total_size):
    """Show download progress"""
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write(f"\rDownloading FFmpeg: {percent}%")
    sys.stdout.flush()


def _is_ffmpeg_in_path():
    """Check if FFmpeg is available in the system PATH"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True,
                                shell=platform.system() == "Windows")
        return result.returncode == 0
    except Exception:
        return False


def _download_and_setup_ffmpeg():
    """Download and setup FFmpeg"""
    # Create directory for FFmpeg
    os.makedirs(FFMPEG_DIR, exist_ok=True)
    
    # Download URL for FFmpeg
    if platform.system() == "Windows":
        download_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    else:
        # For Linux/Mac, we'd want different URLs, but for now, we'll focus on Windows
        download_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    # Set up temporary file for download
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
        zip_path = temp_zip.name
    
    try:
        # Download FFmpeg
        print("Downloading FFmpeg (this may take a few minutes)...")
        urlretrieve(download_url, zip_path, _download_progress)
        print("\nDownload complete!")
        
        # Extract the zip file
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(FFMPEG_DIR)
        
        # Find the bin directory with executables
        extracted_dir = None
        for item in os.listdir(FFMPEG_DIR):
            if os.path.isdir(os.path.join(FFMPEG_DIR, item)) and item.startswith('ffmpeg'):
                extracted_dir = item
                break
        
        if not extracted_dir:
            print("Error: Could not find extracted FFmpeg directory")
            return False
        
        bin_dir = os.path.join(FFMPEG_DIR, extracted_dir, 'bin')
        
        # Update PATH environment variable
        os.environ['PATH'] = bin_dir + os.pathsep + os.environ['PATH']
        
        # Save the path to .env file
        with open(ENV_FILE, 'w') as f:
            f.write(f"FFMPEG_PATH={bin_dir}")
        
        # Test if FFmpeg is working
        if _is_ffmpeg_in_path():
            print("\nFFmpeg installed successfully!")
            return True
        else:
            print("\nFFmpeg installation failed.")
            return False
            
    except Exception as e:
        print(f"\nError setting up FFmpeg: {str(e)}")
        return False
    finally:
        # Clean up the temporary zip file
        if os.path.exists(zip_path):
            os.unlink(zip_path)


def ensure_ffmpeg():
    """
    Ensure FFmpeg is available to the application.
    
    This function:
    1. Checks if FFmpeg is already in the system PATH
    2. If not, tries to load it from the saved path in .env
    3. If still not found, downloads and sets up FFmpeg
    
    Returns:
        bool: True if FFmpeg is available, False otherwise
    """
    global _ffmpeg_configured
    
    # If already configured in this session, return early
    if _ffmpeg_configured:
        return True
    
    # Check if FFmpeg is already in PATH
    if _is_ffmpeg_in_path():
        _ffmpeg_configured = True
        return True
    
    # Try to load from .env
    load_dotenv(ENV_FILE)
    ffmpeg_path = os.getenv('FFMPEG_PATH')
    
    if ffmpeg_path and os.path.exists(ffmpeg_path):
        # Add FFmpeg to PATH
        os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']
        
        # Check if it works
        if _is_ffmpeg_in_path():
            _ffmpeg_configured = True
            return True
    
    # Check if FFmpeg is already downloaded in our directory
    if os.path.exists(FFMPEG_DIR):
        for item in os.listdir(FFMPEG_DIR):
            bin_path = os.path.join(FFMPEG_DIR, item, 'bin')
            if os.path.isdir(bin_path) and os.path.exists(os.path.join(bin_path, 'ffmpeg.exe')):
                # Add FFmpeg to PATH
                os.environ['PATH'] = bin_path + os.pathsep + os.environ['PATH']
                
                # Save the path to .env file
                with open(ENV_FILE, 'w') as f:
                    f.write(f"FFMPEG_PATH={bin_path}")
                
                # Check if it works
                if _is_ffmpeg_in_path():
                    _ffmpeg_configured = True
                    return True
    
    # If all else fails, download and set up FFmpeg
    if _download_and_setup_ffmpeg():
        _ffmpeg_configured = True
        return True
    
    return False


# Automatically attempt to configure when the module is imported
# This allows simple usage like: import src.ffmpeg.manager
ensure_ffmpeg()
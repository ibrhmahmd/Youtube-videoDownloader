import os
import sys
from pathlib import Path
import urllib.request
import zipfile
import io
import shutil
import subprocess
import streamlit as st

def get_ffmpeg_path():
    """Get the path to ffmpeg in the virtual environment"""
    venv_path = Path(sys.prefix)
    ffmpeg_dir = venv_path / ('Scripts' if os.name == 'nt' else 'bin')
    return ffmpeg_dir / ('ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')

def setup_ffmpeg():
    """Setup ffmpeg in the virtual environment"""
    ffmpeg_path = get_ffmpeg_path()
    
    if not ffmpeg_path.exists():
        try:
            # Download ffmpeg
            if os.name == 'nt':  # Windows
                url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            else:  # Linux/Mac
                url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
            
            st.info("Downloading ffmpeg...")
            response = urllib.request.urlopen(url)
            
            if os.name == 'nt':  # Windows
                with zipfile.ZipFile(io.BytesIO(response.read())) as zip_ref:
                    # Extract only the ffmpeg.exe file
                    for file in zip_ref.namelist():
                        if file.endswith('ffmpeg.exe'):
                            zip_ref.extract(file, ffmpeg_path.parent)
                            # Move the file to the correct location
                            extracted_path = ffmpeg_path.parent / file
                            if extracted_path != ffmpeg_path:
                                if ffmpeg_path.exists():
                                    os.remove(ffmpeg_path)
                                os.rename(extracted_path, ffmpeg_path)
            else:  # Linux/Mac
                # For Linux/Mac, we'll use the system package manager
                if sys.platform == 'darwin':  # Mac
                    subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
                else:  # Linux
                    subprocess.run(['sudo', 'apt-get', 'install', 'ffmpeg', '-y'], check=True)
            
            st.success("ffmpeg installed successfully!")
        except Exception as e:
            st.error(f"Error installing ffmpeg: {str(e)}")
            return False
    
    return True
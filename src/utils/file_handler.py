import os
from pathlib import Path
import time
from datetime import datetime

def create_directories():
    """Create necessary directories"""
    directories = ['static', 'downloads']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)

def get_temp_file_path():
    """Generate a temporary file path"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path("static") / f"temp_{timestamp}.mp4"

def cleanup_old_files():
    """Clean up temporary files older than 1 hour"""
    current_time = time.time()
    static_dir = Path("static")
    for file in static_dir.glob("temp_*.mp4"):
        if current_time - os.path.getctime(file) > 3600:  # Remove files older than 1 hour
            try:
                os.remove(file)
            except:
                pass

def remove_file(file_path):
    """Remove a file if it exists"""
    try:
        if file_path.exists():
            os.remove(file_path)
    except:
        pass 
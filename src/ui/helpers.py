import streamlit as st
from src.config import DOWNLOADERS

def get_downloader_for_url(url):
    """Find the appropriate downloader for a given URL"""
    if not url:
        return None
        
    for name, downloader_class in DOWNLOADERS.items():
        d = downloader_class()
        if d.supports_url(url):
            return d
            
    return None 
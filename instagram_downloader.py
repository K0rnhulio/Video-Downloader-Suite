#!/usr/bin/env python3
"""
Instagram Video Downloader
--------------------------
Download videos from Instagram with ease.

This script allows you to download videos from Instagram posts, reels, and stories.
It automatically handles dependencies and provides multiple quality options.

Features:
- Automatic yt-dlp download
- Automatic ffmpeg download
- Multiple quality options
- Custom download directory
- Metadata extraction
"""

import os
import re
import sys
import json
import shutil
import zipfile
import platform
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime
import tempfile
import time

# Default download directory
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "Instagram_Videos")

# yt-dlp executable path
YTDLP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yt-dlp.exe")

# ffmpeg path
FFMPEG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
FFMPEG_PATH = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

def download_ytdlp():
    """Download the latest yt-dlp executable if not present."""
    if os.path.exists(YTDLP_PATH):
        return YTDLP_PATH
    
    print("yt-dlp not found. Downloading...")
    try:
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        urllib.request.urlretrieve(url, YTDLP_PATH)
        print("yt-dlp downloaded successfully.")
        return YTDLP_PATH
    except Exception as e:
        print(f"Error downloading yt-dlp: {e}")
        sys.exit(1)

def get_ffmpeg_path():
    """Get the path to ffmpeg, downloading it if necessary."""
    # Check if ffmpeg is already in the bin directory
    if os.path.exists(FFMPEG_PATH):
        return FFMPEG_PATH
    
    # Check if ffmpeg is in PATH
    ffmpeg_in_path = shutil.which("ffmpeg")
    if ffmpeg_in_path:
        return ffmpeg_in_path
    
    print("ffmpeg not found. Downloading...")
    try:
        # Create bin directory if it doesn't exist
        os.makedirs(FFMPEG_DIR, exist_ok=True)
        
        # Download ffmpeg from GitHub
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the latest ffmpeg build for Windows
            ffmpeg_zip = os.path.join(temp_dir, "ffmpeg.zip")
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
            
            # Extract the zip file
            with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the ffmpeg.exe in the extracted directory
            ffmpeg_dir = next(Path(temp_dir).glob("ffmpeg-master-*"))
            ffmpeg_bin_dir = ffmpeg_dir / "bin"
            
            # Copy ffmpeg.exe to our bin directory
            shutil.copy(ffmpeg_bin_dir / "ffmpeg.exe", FFMPEG_PATH)
            
            print(f"ffmpeg downloaded and installed to {FFMPEG_PATH}")
            return FFMPEG_PATH
    except Exception as e:
        print(f"Error downloading ffmpeg: {e}")
        print("Please install ffmpeg manually and add it to your PATH.")
        sys.exit(1)

def is_valid_instagram_url(url):
    """Check if the URL is a valid Instagram URL."""
    instagram_patterns = [
        r'https?://(www\.)?instagram\.com/p/[a-zA-Z0-9_-]+/?',
        r'https?://(www\.)?instagram\.com/reel/[a-zA-Z0-9_-]+/?',
        r'https?://(www\.)?instagram\.com/stories/[a-zA-Z0-9_.]+/[0-9]+/?',
        r'https?://(www\.)?instagram\.com/tv/[a-zA-Z0-9_-]+/?',
        r'https?://(www\.)?instagr\.am/p/[a-zA-Z0-9_-]+/?',
        r'https?://(www\.)?instagr\.am/reel/[a-zA-Z0-9_-]+/?'
    ]
    
    for pattern in instagram_patterns:
        if re.match(pattern, url):
            return True
    return False

def download_instagram_video(url, quality="best", download_dir=DEFAULT_DOWNLOAD_DIR):
    """
    Download a video from Instagram.
    
    Args:
        url (str): The Instagram URL
        quality (str): Video quality (best, medium, worst)
        download_dir (str): Directory to save the video
    
    Returns:
        bool: True if download was successful, False otherwise
    """
    if not is_valid_instagram_url(url):
        print("Invalid Instagram URL. Please provide a valid Instagram post, reel, or story URL.")
        return False
    
    # Create download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    # Get yt-dlp path
    ytdlp_path = download_ytdlp()
    
    # Get ffmpeg path
    ffmpeg_path = get_ffmpeg_path()
    ffmpeg_dir = os.path.dirname(ffmpeg_path)
    
    # Map quality options to yt-dlp format strings
    quality_map = {
        "best": "bestvideo+bestaudio/best",
        "medium": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "worst": "worstvideo+worstaudio/worst"
    }
    
    format_string = quality_map.get(quality, quality_map["best"])
    
    # Output template for the filename
    output_template = os.path.join(download_dir, "%(uploader)s_%(upload_date)s_%(title).50s.%(ext)s")
    
    # Build the yt-dlp command
    cmd = [
        ytdlp_path,
        "--no-warnings",
        "--ffmpeg-location", ffmpeg_dir,
        "-f", format_string,
        "--merge-output-format", "mp4",
        "-o", output_template,
        "--write-info-json",
        "--no-playlist",
        url
    ]
    
    print(f"\nDownloading Instagram video from: {url}")
    print(f"Quality: {quality}")
    print(f"Download directory: {download_dir}")
    print("Please wait...")
    
    try:
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error downloading video: {result.stderr}")
            return False
        
        # Extract metadata from the output
        output = result.stdout
        print("\nDownload completed successfully!")
        
        # Try to extract and display some metadata
        try:
            # Find the JSON file that was created
            json_files = [f for f in os.listdir(download_dir) if f.endswith('.info.json') and 
                         os.path.getmtime(os.path.join(download_dir, f)) > time.time() - 10]
            
            if json_files:
                json_path = os.path.join(download_dir, json_files[0])
                with open(json_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                print("\nPost Information:")
                print(f"Username: {metadata.get('uploader', 'Unknown')}")
                print(f"Caption: {metadata.get('description', 'No caption')[:100]}...")
                print(f"Upload Date: {metadata.get('upload_date', 'Unknown')}")
                print(f"Like Count: {metadata.get('like_count', 'Unknown')}")
                print(f"Comment Count: {metadata.get('comment_count', 'Unknown')}")
                
                # Clean up the JSON file
                os.remove(json_path)
        except Exception as e:
            print(f"Could not extract metadata: {e}")
        
        return True
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def main():
    """Main function to run the Instagram video downloader."""
    print("=" * 70)
    print(" " * 20 + "Instagram Video Downloader" + " " * 20)
    print("=" * 70)
    print("Download videos from Instagram with ease.")
    
    # Check for ffmpeg at startup
    ffmpeg_path = get_ffmpeg_path()
    print(f"Using ffmpeg from: {os.path.dirname(ffmpeg_path)}")
    
    while True:
        print("\nEnter Instagram URL (or 'q' to quit): ", end="")
        url = input().strip()
        
        if url.lower() == 'q':
            break
        
        if not url:
            print("Please enter a valid URL.")
            continue
        
        # Quality selection
        print("\nSelect video quality:")
        print("1. Best quality (default)")
        print("2. Medium quality (720p)")
        print("3. Worst quality (saves bandwidth)")
        
        quality_choice = input("Enter your choice (1-3) or press Enter for default: ").strip()
        
        quality_map = {
            "1": "best",
            "2": "medium",
            "3": "worst",
            "": "best"  # Default
        }
        
        quality = quality_map.get(quality_choice, "best")
        
        # Custom download directory option
        print("\nUse default download directory? (y/n)")
        print(f"Default: {DEFAULT_DOWNLOAD_DIR}")
        use_default = input("Your choice: ").strip().lower()
        
        if use_default == 'n':
            print("Enter custom download directory path:")
            custom_dir = input().strip()
            if custom_dir and os.path.isdir(custom_dir):
                download_dir = custom_dir
            else:
                print(f"Invalid directory. Using default: {DEFAULT_DOWNLOAD_DIR}")
                download_dir = DEFAULT_DOWNLOAD_DIR
        else:
            download_dir = DEFAULT_DOWNLOAD_DIR
        
        # Download the video
        success = download_instagram_video(url, quality, download_dir)
        
        if success:
            print(f"\nVideo saved to: {download_dir}")
        else:
            print("\nFailed to download the video. Please try again.")
    
    print("\nThank you for using Instagram Video Downloader!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

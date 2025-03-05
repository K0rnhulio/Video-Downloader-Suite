#!/usr/bin/env python3
"""
TikTok Video Downloader (No Watermark)
-------------------------------------
Download videos from TikTok without watermarks.

This script allows you to download videos from TikTok without the TikTok watermark.
It automatically handles dependencies and provides multiple quality options.

Features:
- Automatic yt-dlp download
- Automatic ffmpeg download
- Watermark removal
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
import requests
import logging
from urllib.parse import urlparse, parse_qs

# Default download directory
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "TikTok_Videos")

# yt-dlp executable path
YTDLP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yt-dlp.exe")

# ffmpeg path
FFMPEG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
FFMPEG_PATH = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

# Set up logging
log_dir = os.path.join(os.path.expanduser("~"), "Downloads", "VideoDownloader_Logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"tiktok_downloader_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TikTokDownloader')
logger.info(f"Starting TikTok Downloader. Log file: {log_file}")

def download_ytdlp():
    """Download the latest yt-dlp executable if not present."""
    if os.path.exists(YTDLP_PATH):
        logger.info(f"yt-dlp found at: {YTDLP_PATH}")
        return YTDLP_PATH
    
    logger.info("yt-dlp not found. Downloading...")
    try:
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        urllib.request.urlretrieve(url, YTDLP_PATH)
        logger.info("yt-dlp downloaded successfully")
        return YTDLP_PATH
    except Exception as e:
        logger.error(f"Error downloading yt-dlp: {e}")
        sys.exit(1)

def get_ffmpeg_path():
    """Get the path to ffmpeg, downloading it if necessary."""
    # Check if ffmpeg is already in the bin directory
    if os.path.exists(FFMPEG_PATH):
        logger.info(f"ffmpeg found at: {FFMPEG_PATH}")
        return FFMPEG_PATH
    
    # Check if ffmpeg is in PATH
    ffmpeg_in_path = shutil.which("ffmpeg")
    if ffmpeg_in_path:
        logger.info(f"ffmpeg found in PATH: {ffmpeg_in_path}")
        return ffmpeg_in_path
    
    logger.info("ffmpeg not found. Downloading...")
    try:
        # Create bin directory if it doesn't exist
        os.makedirs(FFMPEG_DIR, exist_ok=True)
        
        # Download ffmpeg from GitHub
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the latest ffmpeg build for Windows
            ffmpeg_zip = os.path.join(temp_dir, "ffmpeg.zip")
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
            logger.info("ffmpeg downloaded successfully")
            
            # Extract the zip file
            with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            logger.info("ffmpeg extracted successfully")
            
            # Find the ffmpeg.exe in the extracted directory
            ffmpeg_dir = next(Path(temp_dir).glob("ffmpeg-master-*"))
            ffmpeg_bin_dir = ffmpeg_dir / "bin"
            
            # Copy ffmpeg.exe to our bin directory
            shutil.copy(ffmpeg_bin_dir / "ffmpeg.exe", FFMPEG_PATH)
            
            logger.info(f"ffmpeg installed to {FFMPEG_PATH}")
            return FFMPEG_PATH
    except Exception as e:
        logger.error(f"Error downloading ffmpeg: {e}")
        logger.error("Please install ffmpeg manually and add it to your PATH")
        sys.exit(1)

def is_valid_tiktok_url(url):
    """Check if the URL is a valid TikTok URL."""
    tiktok_patterns = [
        r'https?://(www\.|vm\.)?tiktok\.com/(@[^/]+/video/\d+|[A-Za-z0-9]+/?)',
        r'https?://m\.tiktok\.com/v/\d+',
        r'https?://(www\.)?tiktok\.com/t/[A-Za-z0-9]+/?'
    ]
    
    for pattern in tiktok_patterns:
        if re.match(pattern, url):
            logger.info("Valid TikTok URL detected")
            return True
    logger.error("Invalid TikTok URL provided")
    return False

def extract_video_id(url):
    """Extract the video ID from a TikTok URL."""
    try:
        # Try to extract from standard URL format
        match = re.search(r'tiktok\.com/@[^/]+/video/(\d+)', url)
        if match:
            video_id = match.group(1)
            logger.info(f"Extracted video ID: {video_id}")
            return video_id
        
        # Try to extract from shortened URL
        if 'vm.tiktok.com' in url or '/t/' in url:
            # Follow the redirect to get the actual URL
            response = requests.head(url, allow_redirects=True)
            final_url = response.url
            match = re.search(r'tiktok\.com/@[^/]+/video/(\d+)', final_url)
            if match:
                video_id = match.group(1)
                logger.info(f"Extracted video ID from redirect: {video_id}")
                return video_id
        
        # Try to extract from mobile URL
        match = re.search(r'm\.tiktok\.com/v/(\d+)', url)
        if match:
            video_id = match.group(1)
            logger.info(f"Extracted video ID from mobile URL: {video_id}")
            return video_id
        
        logger.error("Could not extract video ID from URL")
        return None
    except Exception as e:
        logger.error(f"Error extracting video ID: {e}")
        return None

def download_tiktok_video(url, quality="best", download_dir=DEFAULT_DOWNLOAD_DIR):
    """
    Download a video from TikTok without watermark.
    
    Args:
        url (str): The TikTok URL
        quality (str): Video quality (best, medium, worst)
        download_dir (str): Directory to save the video
    
    Returns:
        bool: True if download was successful, False otherwise
    """
    logger.info(f"Starting TikTok video download from: {url}")
    logger.info(f"Quality setting: {quality}")
    logger.info(f"Download directory: {download_dir}")
    
    if not is_valid_tiktok_url(url):
        logger.error("Invalid TikTok URL provided")
        print("Invalid TikTok URL. Please provide a valid TikTok video URL.")
        return False
    
    # Create download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    logger.debug(f"Ensured download directory exists: {download_dir}")
    
    # Get yt-dlp path
    ytdlp_path = download_ytdlp()
    logger.debug(f"Using yt-dlp from: {ytdlp_path}")
    
    # Get ffmpeg path
    ffmpeg_path = get_ffmpeg_path()
    ffmpeg_dir = os.path.dirname(ffmpeg_path)
    logger.debug(f"Using ffmpeg from: {ffmpeg_dir}")
    
    # Map quality options to yt-dlp format strings
    quality_map = {
        "best": "bestvideo+bestaudio/best",
        "medium": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "worst": "worstvideo+worstaudio/worst"
    }
    
    format_string = quality_map.get(quality, quality_map["best"])
    logger.info(f"Using format string: {format_string}")
    
    # Output template for the filename
    output_template = os.path.join(download_dir, "%(uploader)s_%(upload_date)s_%(title).50s.%(ext)s")
    logger.debug(f"Output template: {output_template}")
    
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
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "--add-header", "Referer:https://www.tiktok.com/",
        "--no-check-certificate",
        url
    ]
    
    logger.debug(f"Download command: {' '.join(cmd)}")
    print(f"\nDownloading TikTok video from: {url}")
    print(f"Quality: {quality}")
    print(f"Download directory: {download_dir}")
    print("Please wait...")
    
    try:
        # Record files before download to detect new files
        files_before_download = set(os.listdir(download_dir)) if os.path.exists(download_dir) else set()
        logger.debug(f"Files in output directory before download: {files_before_download}")
        
        # Run the command and capture output
        logger.debug("Running download command")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Download failed with error: {result.stderr}")
            print(f"Error downloading video: {result.stderr}")
            return False
        
        # Check again after download
        files_after_download = set(os.listdir(download_dir))
        logger.debug(f"Files in output directory after download: {files_after_download}")
        
        # Find new files
        new_files = files_after_download - files_before_download
        logger.info(f"New files created: {new_files}")
        
        # Try to extract and display some metadata
        try:
            # Find the JSON file that was created
            json_files = [f for f in os.listdir(download_dir) if f.endswith('.info.json') and 
                         os.path.getmtime(os.path.join(download_dir, f)) > time.time() - 10]
            
            if json_files:
                json_path = os.path.join(download_dir, json_files[0])
                logger.debug(f"Found metadata JSON file: {json_path}")
                
                with open(json_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                logger.info(f"Post metadata - Username: {metadata.get('uploader', 'Unknown')}, "
                           f"Upload Date: {metadata.get('upload_date', 'Unknown')}, "
                           f"Like Count: {metadata.get('like_count', 'Unknown')}, "
                           f"Comment Count: {metadata.get('comment_count', 'Unknown')}")
                
                print("\nPost Information:")
                print(f"Username: {metadata.get('uploader', 'Unknown')}")
                
                # Handle caption with potential emoji/unicode characters safely
                try:
                    caption = metadata.get('description', 'No caption')
                    if caption:
                        # Truncate caption to 100 chars and add ellipsis
                        truncated_caption = caption[:100] + "..." if len(caption) > 100 else caption
                        print(f"Caption: {truncated_caption}")
                    else:
                        print("Caption: No caption")
                except UnicodeEncodeError:
                    # If we can't print the caption due to encoding issues, provide a safe alternative
                    logger.warning("Caption contains characters that can't be displayed in current console encoding")
                    print("Caption: [Contains emoji or special characters that can't be displayed]")
                
                print(f"Upload Date: {metadata.get('upload_date', 'Unknown')}")
                print(f"Like Count: {metadata.get('like_count', 'Unknown')}")
                print(f"Comment Count: {metadata.get('comment_count', 'Unknown')}")
                
                # Clean up the JSON file
                os.remove(json_path)
                logger.debug(f"Removed metadata JSON file: {json_path}")
        except Exception as e:
            logger.exception(f"Error extracting metadata: {e}")
            print(f"Could not extract metadata: {e}")
        
        logger.info("Download completed successfully!")
        print("\nDownload completed successfully!")
        return True
    
    except Exception as e:
        logger.exception(f"An unexpected error occurred during download: {e}")
        print(f"An unexpected error occurred: {e}")
        return False

def main():
    """Main function to run the TikTok video downloader."""
    print("=" * 70)
    print(" " * 15 + "TikTok Video Downloader (No Watermark)" + " " * 15)
    print("=" * 70)
    print("Download videos from TikTok without watermarks.")
    
    # Check for ffmpeg at startup
    ffmpeg_path = get_ffmpeg_path()
    print(f"Using ffmpeg from: {os.path.dirname(ffmpeg_path)}")
    
    while True:
        print("\nEnter TikTok URL (or 'q' to quit): ", end="")
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
        success = download_tiktok_video(url, quality, download_dir)
        
        if success:
            print(f"\nVideo saved to: {download_dir}")
        else:
            print("\nFailed to download the video. Please try again.")
    
    print("\nThank you for using TikTok Video Downloader!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

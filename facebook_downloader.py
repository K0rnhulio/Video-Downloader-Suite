#!/usr/bin/env python3
"""
Facebook Video Downloader
------------------------
Download videos from Facebook with ease.

This script allows you to download videos from Facebook posts, reels, and stories.
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
import logging

# Set up logging
log_dir = os.path.join(os.path.expanduser("~"), "Downloads", "VideoDownloader_Logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"facebook_downloader_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FacebookDownloader')
logger.info(f"Starting Facebook Downloader. Log file: {log_file}")

# Default download directory
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "Facebook_Videos")

# yt-dlp executable path
YTDLP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yt-dlp.exe")

# ffmpeg path
FFMPEG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
FFMPEG_PATH = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

def download_ytdlp():
    """Download the latest yt-dlp executable if not present."""
    if os.path.exists(YTDLP_PATH):
        logger.info(f"yt-dlp found at: {YTDLP_PATH}")
        return YTDLP_PATH
    
    logger.info("yt-dlp not found. Downloading...")
    try:
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        logger.debug(f"Downloading yt-dlp from: {url}")
        urllib.request.urlretrieve(url, YTDLP_PATH)
        logger.info("yt-dlp downloaded successfully.")
        return YTDLP_PATH
    except Exception as e:
        logger.exception(f"Error downloading yt-dlp: {e}")
        print(f"Error downloading yt-dlp: {e}")
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
            logger.debug(f"Downloading ffmpeg from: {ffmpeg_url}")
            urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
            logger.debug("ffmpeg download complete, extracting...")
            
            # Extract the zip file
            with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the ffmpeg.exe in the extracted directory
            ffmpeg_dir = next(Path(temp_dir).glob("ffmpeg-master-*"))
            ffmpeg_bin_dir = ffmpeg_dir / "bin"
            
            # Copy ffmpeg.exe to our bin directory
            shutil.copy(ffmpeg_bin_dir / "ffmpeg.exe", FFMPEG_PATH)
            
            logger.info(f"ffmpeg downloaded and installed to {FFMPEG_PATH}")
            return FFMPEG_PATH
    except Exception as e:
        logger.exception(f"Error downloading ffmpeg: {e}")
        print(f"Error downloading ffmpeg: {e}")
        print("Please install ffmpeg manually and add it to your PATH.")
        sys.exit(1)

def is_valid_facebook_url(url):
    """Check if the URL is a valid Facebook URL."""
    facebook_patterns = [
        r'https?://(www\.|m\.|web\.)?facebook\.com/[^/]+/videos/[0-9]+',
        r'https?://(www\.|m\.|web\.)?facebook\.com/watch\?v=[0-9]+',
        r'https?://(www\.|m\.|web\.)?facebook\.com/[^/]+/posts/[0-9]+',
        r'https?://(www\.|m\.|web\.)?facebook\.com/[^/]+/videos/[^/]+/[0-9]+',
        r'https?://(www\.|m\.|web\.)?facebook\.com/watch/live/\?v=[0-9]+',
        r'https?://(www\.|m\.|web\.)?fb\.watch/[a-zA-Z0-9_-]+/?',
        r'https?://(www\.|m\.|web\.)?facebook\.com/reel/[0-9]+',
        r'https?://(www\.|m\.|web\.)?facebook\.com/story\.php\?story_fbid=[0-9]+&id=[0-9]+'
    ]
    
    for pattern in facebook_patterns:
        if re.match(pattern, url):
            logger.info(f"Valid Facebook URL detected: {url}")
            return True
    
    logger.warning(f"Invalid Facebook URL: {url}")
    return False

def download_facebook_video(url, quality="best", download_dir=DEFAULT_DOWNLOAD_DIR):
    """
    Download a video from Facebook.
    
    Args:
        url (str): The Facebook URL
        quality (str): Video quality (best, medium, worst)
        download_dir (str): Directory to save the video
    
    Returns:
        bool: True if download was successful, False otherwise
    """
    logger.info(f"Starting Facebook video download from: {url}")
    logger.info(f"Quality setting: {quality}")
    logger.info(f"Download directory: {download_dir}")
    
    if not is_valid_facebook_url(url):
        logger.error("Invalid Facebook URL provided")
        print("Invalid Facebook URL. Please provide a valid Facebook video, post, or reel URL.")
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
    
    # Output template for the filename - use a simpler format to avoid special character issues
    output_template = os.path.join(download_dir, "facebook_video_%(upload_date)s_%(id)s.%(ext)s")
    logger.debug(f"Output template: {output_template}")
    
    # Build the yt-dlp command - start with the standard options without cookies
    cmd = [
        ytdlp_path,
        "--no-warnings",
        "--ffmpeg-location", ffmpeg_dir,
        "-f", format_string,
        "--merge-output-format", "mp4",
        "-o", output_template,
        "--no-write-info-json",  # Skip writing JSON metadata to avoid filename issues
        "--no-playlist",
        "--geo-bypass",  # Bypass geo-restrictions
        url
    ]
    
    logger.debug(f"Initial download command: {' '.join(cmd)}")
    print(f"\nDownloading Facebook video from: {url}")
    print(f"Quality: {quality}")
    print(f"Download directory: {download_dir}")
    print("Please wait...")
    
    try:
        # Run the command and capture output
        logger.debug("Running initial download command")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"Initial download attempt failed: {result.stderr}")
            print(f"Error downloading video: {result.stderr}")
            
            # Try with cookies as a fallback for private content
            logger.info("Trying with browser cookies...")
            print("Trying with browser cookies...")
            cookie_cmd = cmd.copy()
            # Insert cookies option before the URL (which is the last item)
            cookie_cmd.insert(-1, "--cookies-from-browser")
            cookie_cmd.insert(-1, "chrome")
            
            logger.debug(f"Cookie download command: {' '.join(cookie_cmd)}")
            result = subprocess.run(cookie_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Cookie download attempt failed: {result.stderr}")
                print(f"Error downloading video: {result.stderr}")
                
                # Try with mobile URL as a last resort
                logger.info("Trying with mobile URL format...")
                print("Trying with mobile URL format...")
                mobile_url = url.replace("www.facebook.com", "m.facebook.com")
                if mobile_url == url:  # If no change was made
                    mobile_url = url.replace("facebook.com", "m.facebook.com")
                
                logger.debug(f"Using mobile URL: {mobile_url}")
                cmd[-1] = mobile_url  # Replace the URL with mobile version
                logger.debug(f"Mobile URL download command: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.warning(f"Mobile URL download attempt failed: {result.stderr}")
                    print(f"Error downloading video: {result.stderr}")
                    
                    # One final attempt with a very basic approach
                    logger.info("Trying with basic settings...")
                    print("Trying with basic settings...")
                    basic_cmd = [
                        ytdlp_path,
                        "--no-warnings",
                        "--ffmpeg-location", ffmpeg_dir,
                        "-f", "best",  # Just use best format available
                        "-o", os.path.join(download_dir, "facebook_video_%(id)s.mp4"),
                        "--no-write-info-json",
                        "--no-check-certificate",  # Skip certificate validation
                        "--no-playlist",
                        "--geo-bypass",
                        mobile_url
                    ]
                    logger.debug(f"Basic download command: {' '.join(basic_cmd)}")
                    result = subprocess.run(basic_cmd, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        logger.error(f"All download attempts failed: {result.stderr}")
                        print(f"Error downloading video: {result.stderr}")
                        return False
        
        # Extract metadata from the output
        output = result.stdout
        logger.info("Download completed successfully!")
        print("\nDownload completed successfully!")
        
        # Since we're not writing JSON metadata anymore, display basic info
        print("\nVideo downloaded successfully to:")
        print(f"{download_dir}")
        
        # Find the most recently created mp4 file in the directory
        try:
            mp4_files = [f for f in os.listdir(download_dir) if f.endswith('.mp4') and 
                        os.path.getmtime(os.path.join(download_dir, f)) > time.time() - 30]
            
            if mp4_files:
                most_recent = max(mp4_files, key=lambda f: os.path.getmtime(os.path.join(download_dir, f)))
                logger.info(f"Downloaded file: {most_recent}")
                print(f"Filename: {most_recent}")
        except Exception as e:
            logger.error(f"Could not determine filename: {e}")
            print(f"Could not determine filename: {e}")
        
        return True
    
    except Exception as e:
        logger.exception(f"An unexpected error occurred during download: {e}")
        print(f"An unexpected error occurred: {e}")
        return False

def main():
    """Main function to run the Facebook video downloader."""
    logger.info("Starting Facebook Video Downloader CLI")
    print("=" * 70)
    print(" " * 20 + "Facebook Video Downloader" + " " * 20)
    print("=" * 70)
    print("Download videos from Facebook with ease.")
    
    # Check for ffmpeg at startup
    ffmpeg_path = get_ffmpeg_path()
    print(f"Using ffmpeg from: {os.path.dirname(ffmpeg_path)}")
    
    while True:
        print("\nEnter Facebook URL (or 'q' to quit): ", end="")
        url = input().strip()
        
        if url.lower() == 'q':
            logger.info("User quit the application")
            break
        
        if not url:
            logger.warning("Empty URL provided")
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
        logger.info(f"User selected quality: {quality}")
        
        # Custom download directory option
        print("\nUse default download directory? (y/n)")
        print(f"Default: {DEFAULT_DOWNLOAD_DIR}")
        use_default = input("Your choice: ").strip().lower()
        
        if use_default == 'n':
            print("Enter custom download directory path:")
            custom_dir = input().strip()
            if custom_dir and os.path.isdir(custom_dir):
                download_dir = custom_dir
                logger.info(f"Using custom download directory: {download_dir}")
            else:
                logger.warning(f"Invalid directory provided: {custom_dir}, using default")
                print(f"Invalid directory. Using default: {DEFAULT_DOWNLOAD_DIR}")
                download_dir = DEFAULT_DOWNLOAD_DIR
        else:
            logger.info(f"Using default download directory: {DEFAULT_DOWNLOAD_DIR}")
            download_dir = DEFAULT_DOWNLOAD_DIR
        
        # Download the video
        logger.info(f"Starting download with URL: {url}, quality: {quality}, dir: {download_dir}")
        success = download_facebook_video(url, quality, download_dir)
        
        if success:
            logger.info(f"Download successful, video saved to: {download_dir}")
            print(f"\nVideo saved to: {download_dir}")
        else:
            logger.error("Download failed")
            print("\nFailed to download the video. Please try again.")
    
    logger.info("Facebook Video Downloader exiting")
    print("\nThank you for using Facebook Video Downloader!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Download cancelled by user")
        print("\nDownload cancelled by user.")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        print(f"\nAn unexpected error occurred: {e}")

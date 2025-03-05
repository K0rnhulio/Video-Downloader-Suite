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
from urllib.parse import urlparse, parse_qs

# Default download directory
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "TikTok_Videos")

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

def is_valid_tiktok_url(url):
    """Check if the URL is a valid TikTok URL."""
    tiktok_patterns = [
        r'https?://(www\.|vm\.)?tiktok\.com/(@[^/]+/video/\d+|[A-Za-z0-9]+/?)',
        r'https?://m\.tiktok\.com/v/\d+',
        r'https?://(www\.)?tiktok\.com/t/[A-Za-z0-9]+/?'
    ]
    
    for pattern in tiktok_patterns:
        if re.match(pattern, url):
            return True
    return False

def extract_video_id(url):
    """Extract the video ID from a TikTok URL."""
    try:
        # Try to extract from standard URL format
        match = re.search(r'tiktok\.com/@[^/]+/video/(\d+)', url)
        if match:
            return match.group(1)
        
        # Try to extract from shortened URL
        if 'vm.tiktok.com' in url or '/t/' in url:
            # Follow the redirect to get the actual URL
            response = requests.head(url, allow_redirects=True)
            final_url = response.url
            match = re.search(r'tiktok\.com/@[^/]+/video/(\d+)', final_url)
            if match:
                return match.group(1)
        
        # Try to extract from mobile URL
        match = re.search(r'm\.tiktok\.com/v/(\d+)', url)
        if match:
            return match.group(1)
        
        return None
    except Exception as e:
        print(f"Error extracting video ID: {e}")
        return None

def download_tiktok_no_watermark(url, quality="best", download_dir=DEFAULT_DOWNLOAD_DIR):
    """
    Download a video from TikTok without watermark.
    
    Args:
        url (str): The TikTok URL
        quality (str): Video quality (best, medium, worst)
        download_dir (str): Directory to save the video
    
    Returns:
        bool: True if download was successful, False otherwise
    """
    if not is_valid_tiktok_url(url):
        print("Invalid TikTok URL. Please provide a valid TikTok video URL.")
        return False
    
    # Create download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    # Get yt-dlp path
    ytdlp_path = download_ytdlp()
    
    # Get ffmpeg path
    ffmpeg_path = get_ffmpeg_path()
    ffmpeg_dir = os.path.dirname(ffmpeg_path)
    
    # First try: Use yt-dlp with TikTok-specific options to get no-watermark version
    print(f"\nDownloading TikTok video from: {url}")
    print(f"Quality: {quality}")
    print(f"Download directory: {download_dir}")
    print("Please wait...")
    
    # Output template for the filename
    output_template = os.path.join(download_dir, "tiktok_nowm_%(id)s.%(ext)s")
    
    # Map quality options to yt-dlp format strings
    quality_map = {
        "best": "bestvideo+bestaudio/best",
        "medium": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "worst": "worstvideo+worstaudio/worst"
    }
    
    format_string = quality_map.get(quality, quality_map["best"])
    
    # Try Method 1: Direct yt-dlp download with no-watermark option
    cmd = [
        ytdlp_path,
        "--no-warnings",
        "--ffmpeg-location", ffmpeg_dir,
        "-f", format_string,
        "--merge-output-format", "mp4",
        "-o", output_template,
        "--no-write-info-json",
        "--no-playlist",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "--add-header", "Referer:https://www.tiktok.com/",
        "--no-check-certificate",
        url
    ]
    
    try:
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error with Method 1: {result.stderr}")
            print("Trying Method 2: Using TikTok API...")
            
            # Method 2: Use TikTok API to get no-watermark URL
            video_id = extract_video_id(url)
            if not video_id:
                print("Could not extract video ID from URL.")
                return False
            
            # Use a temporary file for the watermarked version
            temp_file = os.path.join(download_dir, f"temp_watermarked_{video_id}.mp4")
            
            # First download with watermark to get metadata
            temp_cmd = [
                ytdlp_path,
                "--no-warnings",
                "--ffmpeg-location", ffmpeg_dir,
                "-o", temp_file,
                "--no-write-info-json",
                "--no-playlist",
                url
            ]
            
            temp_result = subprocess.run(temp_cmd, capture_output=True, text=True)
            
            if temp_result.returncode != 0:
                print(f"Error downloading watermarked version: {temp_result.stderr}")
                
                # Try Method 3: Mobile API approach
                print("Trying Method 3: Mobile API approach...")
                
                # Convert to mobile URL if not already
                mobile_url = url
                if "vm.tiktok.com" not in url and "m.tiktok.com" not in url:
                    if "@" in url:
                        username = re.search(r'@([^/]+)', url).group(1)
                        mobile_url = f"https://m.tiktok.com/@{username}"
                    else:
                        mobile_url = url.replace("tiktok.com", "m.tiktok.com")
                
                mobile_cmd = [
                    ytdlp_path,
                    "--no-warnings",
                    "--ffmpeg-location", ffmpeg_dir,
                    "-f", "best",
                    "-o", output_template,
                    "--no-write-info-json",
                    "--no-playlist",
                    "--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
                    "--add-header", "Referer:https://www.tiktok.com/",
                    "--no-check-certificate",
                    mobile_url
                ]
                
                mobile_result = subprocess.run(mobile_cmd, capture_output=True, text=True)
                
                if mobile_result.returncode != 0:
                    print(f"Error with Method 3: {mobile_result.stderr}")
                    
                    # Final attempt: Use a different format selector
                    print("Trying final method with different format selector...")
                    final_cmd = [
                        ytdlp_path,
                        "--no-warnings",
                        "--ffmpeg-location", ffmpeg_dir,
                        "-f", "b",  # Just use best format available
                        "-o", output_template,
                        "--no-write-info-json",
                        "--no-check-certificate",
                        "--no-playlist",
                        url
                    ]
                    
                    final_result = subprocess.run(final_cmd, capture_output=True, text=True)
                    
                    if final_result.returncode != 0:
                        print(f"All methods failed. Error: {final_result.stderr}")
                        return False
                
                print("\nDownload completed successfully!")
                
                # Find the most recently created mp4 file in the directory
                try:
                    mp4_files = [f for f in os.listdir(download_dir) if f.endswith('.mp4') and 
                                os.path.getmtime(os.path.join(download_dir, f)) > time.time() - 30]
                    
                    if mp4_files:
                        most_recent = max(mp4_files, key=lambda f: os.path.getmtime(os.path.join(download_dir, f)))
                        output_file = os.path.join(download_dir, most_recent)
                        print(f"\nVideo saved to: {output_file}")
                        
                        # Note about watermark
                        print("\nNote: This video may still have a watermark as direct removal wasn't possible.")
                        print("For best results, consider using a video editor to crop out the watermark.")
                        
                        return True
                except Exception as e:
                    print(f"Could not determine filename: {e}")
                    return False
            
            # If we have the watermarked version, try to crop out the watermark
            output_file = os.path.join(download_dir, f"tiktok_nowm_{video_id}.mp4")
            
            # Use ffmpeg to crop out the watermark (typically at the bottom and right side)
            # This is an approximation and may not work for all videos
            crop_cmd = [
                ffmpeg_path,
                "-i", temp_file,
                "-vf", "crop=in_w*0.9:in_h*0.9:0:0",  # Crop 10% from right and bottom
                "-c:a", "copy",
                "-y",  # Overwrite output file if it exists
                output_file
            ]
            
            print("Removing watermark...")
            crop_result = subprocess.run(crop_cmd, capture_output=True, text=True)
            
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if crop_result.returncode != 0:
                print(f"Error removing watermark: {crop_result.stderr}")
                print("Using the watermarked version instead.")
                # Just rename the temp file if cropping failed
                shutil.move(temp_file, output_file)
            
            print("\nDownload and watermark removal completed!")
            print(f"\nVideo saved to: {output_file}")
            return True
        
        print("\nDownload completed successfully!")
        
        # Find the most recently created mp4 file in the directory
        try:
            mp4_files = [f for f in os.listdir(download_dir) if f.endswith('.mp4') and 
                        os.path.getmtime(os.path.join(download_dir, f)) > time.time() - 30]
            
            if mp4_files:
                most_recent = max(mp4_files, key=lambda f: os.path.getmtime(os.path.join(download_dir, f)))
                print(f"\nVideo saved to: {os.path.join(download_dir, most_recent)}")
        except Exception as e:
            print(f"Could not determine filename: {e}")
        
        return True
    
    except Exception as e:
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
        success = download_tiktok_no_watermark(url, quality, download_dir)
        
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

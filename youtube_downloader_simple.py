#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple YouTube Video Downloader
A straightforward Python script to download videos from YouTube using yt-dlp.
This is the most reliable method for downloading YouTube videos.
"""

import os
import re
import sys
import subprocess
import urllib.request
from urllib.error import URLError
import platform
from datetime import datetime

def get_yt_dlp_path():
    """Get or download the yt-dlp executable."""
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to yt-dlp executable
    if platform.system() == 'Windows':
        yt_dlp_path = os.path.join(script_dir, "yt-dlp.exe")
    else:
        yt_dlp_path = os.path.join(script_dir, "yt-dlp")
    
    # Check if yt-dlp already exists
    if os.path.exists(yt_dlp_path):
        return yt_dlp_path
    
    # Download yt-dlp
    print("yt-dlp not found. Downloading...")
    try:
        if platform.system() == 'Windows':
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        else:
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
        
        print(f"Downloading from {url}...")
        urllib.request.urlretrieve(url, yt_dlp_path)
        
        # Make executable on Unix-like systems
        if platform.system() != 'Windows':
            os.chmod(yt_dlp_path, 0o755)
            
        print(f"yt-dlp downloaded to {yt_dlp_path}")
        return yt_dlp_path
    except URLError as e:
        print(f"Error downloading yt-dlp: {e}")
        sys.exit(1)

def validate_youtube_url(url):
    """
    Validate if the URL is a YouTube URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if valid YouTube URL, False otherwise
    """
    # Regular expression patterns for YouTube URLs
    patterns = [
        r'^https?://(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]+)(?:\?.*)?$',
        r'^https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)(?:&.*)?$',
        r'^https?://(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)(?:\?.*)?$'
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    
    return False

def download_youtube_video(url, output_path=None, quality='best'):
    """
    Download a YouTube video using yt-dlp.
    
    Args:
        url (str): The YouTube video URL
        output_path (str, optional): The directory to save the video. Defaults to current directory.
        quality (str, optional): Video quality. Options: 'best', '1080p', '720p', '480p', '360p'. Defaults to 'best'.
        
    Returns:
        str: Success or error message
    """
    try:
        # Create output directory if it doesn't exist
        if output_path and not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Get yt-dlp path
        yt_dlp_path = get_yt_dlp_path()
        
        # Map quality to format
        quality_map = {
            'best': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]',
            '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]',
            '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]',
            '360p': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best[height<=360]'
        }
        
        format_str = quality_map.get(quality, 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best')
        
        # Prepare the output template
        output_template = os.path.join(output_path, "%(title)s.%(ext)s") if output_path else "%(title)s.%(ext)s"
        
        # Prepare the command
        cmd = [
            yt_dlp_path,
            url,
            "-f", format_str,
            "-o", output_template,
            "--no-playlist",
            "--progress",
            "--no-warnings",
            "--merge-output-format", "mp4"
        ]
        
        print(f"\nDownloading video from: {url}")
        print(f"Quality: {quality}")
        print("This may take a moment...")
        
        # Run the command
        process = subprocess.run(cmd, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        
        # Check if the download was successful
        if process.returncode == 0:
            # Try to find the downloaded file
            if output_path:
                # Parse the output to find the filename
                output_lines = process.stdout.splitlines()
                filename = None
                for line in output_lines:
                    if "Destination:" in line:
                        filename = line.split("Destination:", 1)[1].strip()
                        break
                
                if filename and os.path.exists(filename):
                    file_size = os.path.getsize(filename) / (1024 * 1024)  # in MB
                    return f"Success: Video downloaded successfully!\nSaved to: {filename}\nFile size: {file_size:.2f} MB"
                
                # If we couldn't find the filename in the output, look for the most recent file
                files = os.listdir(output_path)
                if files:
                    # Get the most recently modified file
                    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(output_path, f)))
                    file_path = os.path.join(output_path, latest_file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # in MB
                    return f"Success: Video downloaded successfully!\nSaved to: {file_path}\nFile size: {file_size:.2f} MB"
            
            return "Success: Video downloaded successfully!"
        else:
            error_msg = process.stderr.strip() if process.stderr else "Unknown error"
            return f"Error: {error_msg}"
    
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main function to run the YouTube video downloader."""
    print("=" * 60)
    print("Simple YouTube Video Downloader".center(60))
    print("=" * 60)
    
    # Get the default download directory
    default_download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube_Videos")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(default_download_dir):
        os.makedirs(default_download_dir)
    
    while True:
        # Get the video URL from the user
        video_url = input("\nEnter YouTube URL (or 'q' to quit): ").strip()
        
        if video_url.lower() == 'q':
            print("\nThank you for using YouTube Video Downloader!")
            break
        
        # Validate the URL
        if not validate_youtube_url(video_url):
            print("Error: This doesn't appear to be a valid YouTube URL.")
            continue
        
        # Ask for video quality
        print("\nSelect video quality:")
        print("1. Best quality (default)")
        print("2. 1080p")
        print("3. 720p")
        print("4. 480p")
        print("5. 360p")
        
        quality_choice = input("Enter your choice (1-5): ").strip()
        
        quality_map = {
            '1': 'best',
            '2': '1080p',
            '3': '720p',
            '4': '480p',
            '5': '360p'
        }
        
        quality = quality_map.get(quality_choice, 'best')
        
        # Ask for custom output directory
        use_custom_dir = input(f"Use default download directory ({default_download_dir})? (y/n): ").strip().lower()
        
        if use_custom_dir == 'n':
            custom_dir = input("Enter custom download directory: ").strip()
            if custom_dir and os.path.exists(custom_dir):
                output_dir = custom_dir
            else:
                print(f"Invalid directory. Using default: {default_download_dir}")
                output_dir = default_download_dir
        else:
            output_dir = default_download_dir
        
        # Download the video
        result = download_youtube_video(video_url, output_dir, quality)
        print(f"\n{result}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDownload canceled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)

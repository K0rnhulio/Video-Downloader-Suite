#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YouTube Shorts Downloader (Alternative Version)
A simple Python script to download videos from YouTube Shorts using yt-dlp.
"""

import os
import re
import sys
import subprocess
import platform
import tempfile
from urllib.request import urlopen
from urllib.error import URLError
import zipfile
import shutil

def get_yt_dlp_path():
    """Get the path to yt-dlp executable or download it if not available."""
    # Check if yt-dlp is in PATH
    if check_command_exists("yt-dlp"):
        return "yt-dlp"
    
    # Check if we have a local copy in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_yt_dlp = os.path.join(script_dir, "yt-dlp.exe")
    
    if os.path.exists(local_yt_dlp):
        return local_yt_dlp
    
    # Download yt-dlp executable
    print("yt-dlp not found. Downloading yt-dlp executable...")
    try:
        # URL for the latest yt-dlp executable
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        
        # Download the file
        print(f"Downloading from {url}...")
        with urlopen(url) as response, open(local_yt_dlp, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        
        print(f"yt-dlp downloaded to {local_yt_dlp}")
        return local_yt_dlp
    except URLError as e:
        print(f"Error downloading yt-dlp: {e}")
        print("Please download yt-dlp manually from https://github.com/yt-dlp/yt-dlp/releases")
        sys.exit(1)

def check_command_exists(command):
    """Check if a command exists in the system path."""
    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.check_call([command, "--version"], 
                                stdout=devnull, 
                                stderr=devnull)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

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

def download_youtube_video(url, output_path=None):
    """
    Download a YouTube video using yt-dlp.
    
    Args:
        url (str): The YouTube video URL
        output_path (str, optional): The directory to save the video. Defaults to current directory.
        
    Returns:
        str: Success or error message
    """
    try:
        # Create output directory if it doesn't exist
        if output_path and not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Get yt-dlp path
        yt_dlp_path = get_yt_dlp_path()
        
        # Prepare the output template
        output_template = os.path.join(output_path, "%(title)s.%(ext)s") if output_path else "%(title)s.%(ext)s"
        
        # Prepare the command with high quality format
        cmd = [
            yt_dlp_path,
            url,
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "-o", output_template,
            "--no-playlist",
            "--merge-output-format", "mp4"
        ]
        
        print(f"\nDownloading video from: {url}")
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
    """Main function to run the YouTube Shorts downloader."""
    print("=" * 60)
    print("YouTube Shorts Downloader (Alternative Version)".center(60))
    print("=" * 60)
    
    # Get the default download directory
    default_download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube_Shorts")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(default_download_dir):
        os.makedirs(default_download_dir)
    
    while True:
        # Get the video URL from the user
        video_url = input("\nEnter YouTube URL (or 'q' to quit): ").strip()
        
        if video_url.lower() == 'q':
            print("\nThank you for using YouTube Shorts Downloader!")
            break
        
        # Validate the URL
        if not validate_youtube_url(video_url):
            print("Error: This doesn't appear to be a valid YouTube URL.")
            continue
        
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
        result = download_youtube_video(video_url, output_dir)
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

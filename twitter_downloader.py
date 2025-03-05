#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Twitter/X Video Downloader
A specialized Python script to download videos from Twitter/X.
This version uses yt-dlp which has good support for Twitter/X videos.
"""

import os
import re
import sys
import time
import urllib.request
import urllib.error
import platform
import subprocess
import zipfile
import shutil
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
    except urllib.error.URLError as e:
        print(f"Error downloading yt-dlp: {e}")
        sys.exit(1)

def get_ffmpeg_path():
    """Get or download ffmpeg."""
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bin_dir = os.path.join(script_dir, "bin")
    
    # Create bin directory if it doesn't exist
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)
    
    # Path to ffmpeg executable
    if platform.system() == 'Windows':
        ffmpeg_path = os.path.join(bin_dir, "ffmpeg.exe")
        ffprobe_path = os.path.join(bin_dir, "ffprobe.exe")
    else:
        ffmpeg_path = os.path.join(bin_dir, "ffmpeg")
        ffprobe_path = os.path.join(bin_dir, "ffprobe")
    
    # Check if ffmpeg already exists
    if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
        # Add bin directory to PATH
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
        return ffmpeg_path
    
    # Download ffmpeg
    print("ffmpeg not found. Downloading...")
    try:
        if platform.system() == 'Windows':
            # URL for Windows ffmpeg
            url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            zip_path = os.path.join(script_dir, "ffmpeg.zip")
            
            print(f"Downloading ffmpeg from {url}...")
            urllib.request.urlretrieve(url, zip_path)
            
            # Extract the zip file
            print("Extracting ffmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(script_dir)
            
            # Move the ffmpeg executables to the bin directory
            ffmpeg_dir = None
            for item in os.listdir(script_dir):
                if item.startswith("ffmpeg-master"):
                    ffmpeg_dir = os.path.join(script_dir, item)
                    break
            
            if ffmpeg_dir:
                # Copy ffmpeg and ffprobe to bin directory
                shutil.copy(os.path.join(ffmpeg_dir, "bin", "ffmpeg.exe"), ffmpeg_path)
                shutil.copy(os.path.join(ffmpeg_dir, "bin", "ffprobe.exe"), ffprobe_path)
                
                # Clean up
                os.remove(zip_path)
                shutil.rmtree(ffmpeg_dir)
                
                print(f"ffmpeg downloaded to {bin_dir}")
                
                # Add bin directory to PATH
                os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
                
                return ffmpeg_path
            else:
                print("Error: Could not find ffmpeg directory after extraction")
                return None
        else:
            # For Unix systems, suggest using package manager
            print("Please install ffmpeg using your package manager:")
            print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
            print("  CentOS/RHEL: sudo yum install ffmpeg")
            print("  macOS: brew install ffmpeg")
            return None
    except Exception as e:
        print(f"Error downloading ffmpeg: {e}")
        return None

def validate_twitter_url(url):
    """
    Validate if the URL is a Twitter/X URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if valid Twitter/X URL, False otherwise
    """
    # Regular expression patterns for Twitter/X URLs
    patterns = [
        r'^https?://(?:www\.)?twitter\.com/\w+/status/\d+(?:\?.*)?$',
        r'^https?://(?:www\.)?x\.com/\w+/status/\d+(?:\?.*)?$',
        r'^https?://(?:mobile\.)?twitter\.com/\w+/status/\d+(?:\?.*)?$',
        r'^https?://(?:mobile\.)?x\.com/\w+/status/\d+(?:\?.*)?$'
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    
    return False

def get_video_info(url):
    """Get information about the video using yt-dlp."""
    try:
        yt_dlp_path = get_yt_dlp_path()
        cmd = [yt_dlp_path, "--dump-json", url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            video_info = json.loads(result.stdout)
            return video_info
        else:
            print(f"Error getting video info: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def download_twitter_video(url, output_path=None, quality='best'):
    """
    Download a Twitter/X video using yt-dlp.
    
    Args:
        url (str): The Twitter/X video URL
        output_path (str, optional): The directory to save the video. Defaults to current directory.
        quality (str, optional): The quality to download. Defaults to 'best'.
        
    Returns:
        str: Success or error message
    """
    try:
        # Create output directory if it doesn't exist
        if output_path and not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Get yt-dlp path
        yt_dlp_path = get_yt_dlp_path()
        
        # Get ffmpeg path
        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            print("Warning: ffmpeg not found. Attempting to download...")
            ffmpeg_path = get_ffmpeg_path()  # Try again after download attempt
            if not ffmpeg_path:
                print("Warning: Failed to download ffmpeg. Some videos may not download correctly.")
        
        # Get video info first
        print("Fetching video information...")
        video_info = get_video_info(url)
        
        if video_info:
            print(f"\nVideo from: @{video_info.get('uploader', 'Unknown')}")
            print(f"Tweet text: {video_info.get('description', 'No description')}")
            
            # Show available formats
            print("\nAvailable formats:")
            cmd = [yt_dlp_path, "-F", url]
            subprocess.run(cmd)
            
            # Ask user if they want to select a specific format
            use_specific_format = input("\nDo you want to select a specific format? (y/n): ").strip().lower() == 'y'
            
            if use_specific_format:
                format_id = input("Enter format ID: ").strip()
            else:
                # Use the best possible format by default
                format_id = quality
        else:
            # If we couldn't get video info, use the best format
            format_id = quality
        
        # Prepare the output template
        # Use a template that includes the tweet author and date
        output_template = os.path.join(output_path, "%(uploader)s_%(upload_date)s_%(id)s.%(ext)s") if output_path else "%(uploader)s_%(upload_date)s_%(id)s.%(ext)s"
        
        # Prepare the command
        cmd = [
            yt_dlp_path,
            url,
            "-f", format_id,
            "-o", output_template,
            "--no-playlist",
            "--no-warnings",
            "--no-check-certificate",  # Skip HTTPS certificate validation
            "--add-metadata",          # Add metadata to the file
            "--write-thumbnail"        # Save thumbnail
        ]
        
        # Add ffmpeg location if we found it
        if ffmpeg_path:
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
            cmd.extend(["--ffmpeg-location", ffmpeg_dir])
        
        print(f"\nDownloading video from: {url}")
        print(f"Format: {format_id}")
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
                    if latest_file.endswith(('.mp4', '.webm')):
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
    """Main function to run the Twitter/X Video Downloader."""
    print("=" * 70)
    print("Twitter/X Video Downloader".center(70))
    print("=" * 70)
    print("Download videos from Twitter/X with ease.")
    
    # Get the default download directory
    default_download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Twitter_Videos")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(default_download_dir):
        os.makedirs(default_download_dir)
    
    # Check for ffmpeg at startup
    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path:
        print(f"Using ffmpeg from: {os.path.dirname(ffmpeg_path)}")
    
    while True:
        # Get the video URL from the user
        video_url = input("\nEnter Twitter/X URL (or 'q' to quit): ").strip()
        
        if video_url.lower() == 'q':
            print("\nThank you for using Twitter/X Video Downloader!")
            break
        
        # Validate the URL
        if not validate_twitter_url(video_url):
            print("Error: This doesn't appear to be a valid Twitter/X URL.")
            print("Example of valid URL: https://twitter.com/username/status/1234567890")
            print("                      https://x.com/username/status/1234567890")
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
        
        # Ask for quality
        quality_choice = input("Select quality (1: best, 2: medium, 3: worst) [1]: ").strip()
        
        if quality_choice == '2':
            quality = 'medium'
        elif quality_choice == '3':
            quality = 'worst'
        else:
            quality = 'best'
        
        # Download the video
        result = download_twitter_video(video_url, output_dir, quality)
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

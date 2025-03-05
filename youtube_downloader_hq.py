#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
High Quality YouTube Video Downloader
A specialized Python script to download videos from YouTube in the highest possible quality.
This version uses advanced yt-dlp options to force the highest quality.
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

def download_youtube_video(url, output_path=None, force_high_quality=True):
    """
    Download a YouTube video using yt-dlp with advanced options for highest quality.
    
    Args:
        url (str): The YouTube video URL
        output_path (str, optional): The directory to save the video. Defaults to current directory.
        force_high_quality (bool, optional): Whether to force the highest quality. Defaults to True.
        
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
        if not ffmpeg_path and force_high_quality:
            print("Warning: ffmpeg not found. High quality downloads may not work properly.")
            print("Will try to use yt-dlp's built-in capabilities.")
        
        # Get video info first to show available formats
        print("Fetching video information...")
        video_info = get_video_info(url)
        
        if video_info:
            print(f"\nVideo Title: {video_info.get('title', 'Unknown')}")
            print(f"Channel: {video_info.get('channel', 'Unknown')}")
            print(f"Duration: {video_info.get('duration', 0)} seconds")
            
            # Show available formats
            print("\nAvailable formats:")
            cmd = [yt_dlp_path, "-F", url]
            subprocess.run(cmd)
            
            # Ask user if they want to select a specific format
            use_specific_format = input("\nDo you want to select a specific format? (y/n): ").strip().lower() == 'y'
            
            if use_specific_format:
                format_id = input("Enter format ID (e.g., 137+140, 22, best): ").strip()
            else:
                # Use the best possible format by default
                if force_high_quality:
                    # Force the highest quality video and audio, then merge
                    format_id = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
                else:
                    format_id = "best"
        else:
            # If we couldn't get video info, use the best format
            format_id = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
        
        # Prepare the output template
        output_template = os.path.join(output_path, "%(title)s.%(ext)s") if output_path else "%(title)s.%(ext)s"
        
        # Prepare the command with advanced options
        cmd = [
            yt_dlp_path,
            url,
            "-f", format_id,
            "-o", output_template,
            "--no-playlist",
            "--merge-output-format", "mp4",
            "--no-warnings",
            "--no-check-certificate",  # Skip HTTPS certificate validation
            "--prefer-ffmpeg",         # Prefer ffmpeg for post-processing
            "--add-metadata",          # Add metadata to the file
            "--write-thumbnail"        # Save thumbnail
        ]
        
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
                    
                    # Get video dimensions using ffprobe
                    try:
                        ffprobe_path = os.path.join(os.path.dirname(ffmpeg_path), "ffprobe.exe") if ffmpeg_path else "ffprobe"
                        ffprobe_cmd = [ffprobe_path, "-v", "error", "-select_streams", "v:0", 
                                      "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", filename]
                        dimensions = subprocess.check_output(ffprobe_cmd, text=True).strip()
                        dimensions_info = f"\nResolution: {dimensions}"
                    except:
                        dimensions_info = ""
                    
                    return f"Success: Video downloaded successfully!\nSaved to: {filename}\nFile size: {file_size:.2f} MB{dimensions_info}"
                
                # If we couldn't find the filename in the output, look for the most recent file
                files = os.listdir(output_path)
                if files:
                    # Get the most recently modified file
                    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(output_path, f)))
                    if latest_file.endswith('.mp4'):
                        file_path = os.path.join(output_path, latest_file)
                        file_size = os.path.getsize(file_path) / (1024 * 1024)  # in MB
                        
                        # Get video dimensions using ffprobe
                        try:
                            ffprobe_path = os.path.join(os.path.dirname(ffmpeg_path), "ffprobe.exe") if ffmpeg_path else "ffprobe"
                            ffprobe_cmd = [ffprobe_path, "-v", "error", "-select_streams", "v:0", 
                                          "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", file_path]
                            dimensions = subprocess.check_output(ffprobe_cmd, text=True).strip()
                            dimensions_info = f"\nResolution: {dimensions}"
                        except:
                            dimensions_info = ""
                        
                        return f"Success: Video downloaded successfully!\nSaved to: {file_path}\nFile size: {file_size:.2f} MB{dimensions_info}"
            
            return "Success: Video downloaded successfully!"
        else:
            error_msg = process.stderr.strip() if process.stderr else "Unknown error"
            return f"Error: {error_msg}"
    
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main function to run the High Quality YouTube Video Downloader."""
    print("=" * 70)
    print("High Quality YouTube Video Downloader".center(70))
    print("=" * 70)
    print("This version is specialized for getting the highest possible quality.")
    
    # Get the default download directory
    default_download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube_Videos_HQ")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(default_download_dir):
        os.makedirs(default_download_dir)
    
    while True:
        # Get the video URL from the user
        video_url = input("\nEnter YouTube URL (or 'q' to quit): ").strip()
        
        if video_url.lower() == 'q':
            print("\nThank you for using High Quality YouTube Video Downloader!")
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
        
        # Ask if user wants to force high quality
        force_hq = input("Force highest possible quality? (y/n): ").strip().lower() != 'n'
        
        # Download the video
        result = download_youtube_video(video_url, output_dir, force_hq)
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

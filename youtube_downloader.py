#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YouTube Shorts Downloader
A simple Python script to download videos from YouTube Shorts.
"""

import os
import re
import sys
import urllib.request
import urllib.error
from pytube import YouTube
from pytube.exceptions import PytubeError
from datetime import timedelta

# Apply patch to fix 403 Forbidden error
def apply_pytube_patch():
    """
    Apply a patch to fix the 403 Forbidden error in pytube.
    This is a workaround for YouTube's security measures.
    """
    try:
        # Import necessary modules
        from pytube.innertube import InnerTube
        
        # Monkey patch the InnerTube._headers method
        original_headers = InnerTube._headers
        
        def patched_headers(self):
            headers = original_headers(self)
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            headers['Accept-Language'] = 'en-US,en;q=0.9'
            return headers
        
        InnerTube._headers = patched_headers
        
        return True
    except Exception as e:
        print(f"Warning: Could not apply pytube patch: {e}")
        return False

def validate_youtube_shorts_url(url):
    """
    Validate if the URL is a YouTube Shorts URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if valid YouTube Shorts URL, False otherwise
    """
    # Regular expression patterns for YouTube Shorts URLs
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
    Download a YouTube video using pytube.
    
    Args:
        url (str): The YouTube video URL
        output_path (str, optional): The directory to save the video. Defaults to current directory.
        
    Returns:
        str: Success or error message
    """
    try:
        # Apply the patch to fix 403 Forbidden errors
        apply_pytube_patch()
        
        # Create output directory if it doesn't exist
        if output_path and not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Create a YouTube object
        yt = YouTube(url)
        
        # Get video information
        video_title = yt.title
        video_author = yt.author
        video_length = yt.length  # in seconds
        
        # Get the highest resolution stream
        # First try to get the highest quality progressive stream (video+audio)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        # If no progressive stream is available, try to get the highest quality adaptive stream
        if not stream:
            stream = yt.streams.filter(adaptive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        # If still no stream is available, try to get any mp4 stream
        if not stream:
            stream = yt.streams.filter(file_extension='mp4').first()
        
        # If no mp4 stream is available, get any stream
        if not stream:
            stream = yt.streams.first()
        
        if not stream:
            return "Error: No suitable stream found for this video."
        
        # Get stream information
        resolution = stream.resolution if hasattr(stream, 'resolution') and stream.resolution else "Unknown"
        
        # Download the video
        print(f"\nDownloading video: {video_title}")
        print(f"Channel: {video_author}")
        print(f"Length: {timedelta(seconds=video_length)}")
        print(f"Resolution: {resolution}")
        print("This may take a moment...")
        
        # Download with progress reporting
        file_path = stream.download(output_path=output_path)
        
        # Get file size
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # in MB
        
        return f"Success: Video downloaded successfully!\nTitle: {video_title}\nSaved to: {file_path}\nFile size: {file_size:.2f} MB\nResolution: {resolution}"
    
    except Exception as e:
        # If pytube fails, try using yt-dlp as a fallback
        print(f"PyTube download failed: {e}")
        print("Trying alternative download method with yt-dlp...")
        
        try:
            # Check if we have the alternative downloader
            alt_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube_downloader_alt.py")
            if os.path.exists(alt_script):
                # Import the alternative downloader
                import importlib.util
                spec = importlib.util.spec_from_file_location("youtube_downloader_alt", alt_script)
                alt_downloader = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(alt_downloader)
                
                # Use the alternative downloader
                return alt_downloader.download_youtube_video(url, output_path)
            else:
                # If alternative downloader is not available, try a direct yt-dlp implementation
                import subprocess
                
                # Check if we have yt-dlp in the same directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                yt_dlp_path = os.path.join(script_dir, "yt-dlp.exe")
                
                # If not, download it
                if not os.path.exists(yt_dlp_path):
                    print("Downloading yt-dlp...")
                    yt_dlp_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
                    urllib.request.urlretrieve(yt_dlp_url, yt_dlp_path)
                
                # Prepare the output template
                output_template = os.path.join(output_path, "%(title)s.%(ext)s") if output_path else "%(title)s.%(ext)s"
                
                # Use yt-dlp to download the video with high quality
                cmd = [
                    yt_dlp_path,
                    url,
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                    "-o", output_template,
                    "--no-playlist",
                    "--merge-output-format", "mp4"
                ]
                
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if process.returncode == 0:
                    return "Success: Video downloaded successfully with alternative method!"
                else:
                    error_msg = process.stderr.strip() if process.stderr else "Unknown error"
                    return f"Error with alternative method: {error_msg}"
        except Exception as alt_e:
            return f"Error: {str(e)}\nAlternative method also failed: {str(alt_e)}"

def main():
    """Main function to run the YouTube Shorts downloader."""
    print("=" * 60)
    print("YouTube Shorts Downloader".center(60))
    print("=" * 60)
    
    # Apply the patch to fix 403 Forbidden errors
    patch_result = apply_pytube_patch()
    if patch_result:
        print(" Applied patch to fix potential 403 Forbidden errors")
    
    # Get the default download directory
    default_download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube_Shorts")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(default_download_dir):
        os.makedirs(default_download_dir)
    
    while True:
        # Get the video URL from the user
        video_url = input("\nEnter YouTube Shorts URL (or 'q' to quit): ").strip()
        
        if video_url.lower() == 'q':
            print("\nThank you for using YouTube Shorts Downloader!")
            break
        
        # Validate the URL
        if not validate_youtube_shorts_url(video_url):
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

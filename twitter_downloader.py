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
import io
import logging
from datetime import datetime

# Set up logging
log_dir = os.path.join(os.path.expanduser("~"), "Downloads", "VideoDownloader_Logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"twitter_downloader_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TwitterDownloader')
logger.info(f"Starting Twitter Downloader. Log file: {log_file}")

# Remove the stdout/stderr redirection that was causing issues

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
        logger.info(f"Found existing yt-dlp at: {yt_dlp_path}")
        return yt_dlp_path
    
    # Download yt-dlp
    logger.info("yt-dlp not found. Downloading...")
    try:
        if platform.system() == 'Windows':
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        else:
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
        
        logger.info(f"Downloading from {url}...")
        urllib.request.urlretrieve(url, yt_dlp_path)
        
        # Make executable on Unix-like systems
        if platform.system() != 'Windows':
            os.chmod(yt_dlp_path, 0o755)
            
        logger.info(f"yt-dlp downloaded to {yt_dlp_path}")
        return yt_dlp_path
    except Exception as e:
        logger.error(f"Failed to download yt-dlp: {str(e)}")
        return None

def get_ffmpeg_path():
    """Get or download the ffmpeg executable."""
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to ffmpeg directory
    ffmpeg_dir = os.path.join(script_dir, "ffmpeg")
    
    # Path to ffmpeg executable
    if platform.system() == 'Windows':
        ffmpeg_path = os.path.join(ffmpeg_dir, "bin", "ffmpeg.exe")
    else:
        ffmpeg_path = os.path.join(ffmpeg_dir, "bin", "ffmpeg")
    
    # Check if ffmpeg already exists
    if os.path.exists(ffmpeg_path):
        logger.info(f"Found existing ffmpeg at: {ffmpeg_path}")
        return ffmpeg_path
    
    # Download ffmpeg
    logger.info("ffmpeg not found. Downloading...")
    try:
        # Create ffmpeg directory if it doesn't exist
        if not os.path.exists(ffmpeg_dir):
            os.makedirs(ffmpeg_dir)
        
        # Download URL based on platform
        if platform.system() == 'Windows':
            url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            zip_path = os.path.join(script_dir, "ffmpeg.zip")
            
            logger.info(f"Downloading ffmpeg from {url}...")
            urllib.request.urlretrieve(url, zip_path)
            
            logger.info("Extracting ffmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(script_dir)
            
            # Rename the extracted directory to "ffmpeg"
            extracted_dir = None
            for item in os.listdir(script_dir):
                if item.startswith("ffmpeg-master") and os.path.isdir(os.path.join(script_dir, item)):
                    extracted_dir = os.path.join(script_dir, item)
                    break
            
            if extracted_dir and os.path.exists(extracted_dir):
                if os.path.exists(ffmpeg_dir):
                    shutil.rmtree(ffmpeg_dir)
                os.rename(extracted_dir, ffmpeg_dir)
            
            # Clean up
            if os.path.exists(zip_path):
                os.remove(zip_path)
        else:
            # For Unix-like systems, you might want to use the package manager
            # or provide a similar download mechanism
            logger.error("Automatic ffmpeg download not supported on this platform.")
            logger.error("Please install ffmpeg manually using your package manager.")
            return None
        
        # Verify the download
        if os.path.exists(ffmpeg_path):
            logger.info(f"ffmpeg downloaded to {ffmpeg_path}")
            return ffmpeg_path
        else:
            logger.error("Failed to download ffmpeg: File not found after download")
            return None
    except Exception as e:
        logger.error(f"Failed to download ffmpeg: {str(e)}")
        return None

def validate_twitter_url(url):
    """
    Validate if the URL is a Twitter/X URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if valid Twitter/X URL, False otherwise
    """
    # Twitter URL patterns
    twitter_patterns = [
        r'https?://(www\.)?twitter\.com/\w+/status/\d+',
        r'https?://(www\.)?x\.com/\w+/status/\d+'
    ]
    
    for pattern in twitter_patterns:
        if re.match(pattern, url):
            logger.info(f"Valid Twitter URL: {url}")
            return True
    
    logger.warning(f"Invalid Twitter URL: {url}")
    return False

def get_video_info(url):
    """
    Get information about the video using yt-dlp.
    
    Args:
        url (str): The Twitter/X video URL
        
    Returns:
        dict: Video information or None if failed
    """
    try:
        logger.info(f"Getting video info for: {url}")
        yt_dlp_path = get_yt_dlp_path()
        
        if not yt_dlp_path:
            logger.error("yt-dlp not found")
            return None
        
        cmd = [yt_dlp_path, "--dump-json", url]
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        
        if process.returncode == 0:
            import json
            video_info = json.loads(process.stdout)
            logger.info(f"Successfully retrieved video info: {video_info.get('id', 'Unknown ID')}")
            return video_info
        else:
            logger.error(f"Failed to get video info: {process.stderr}")
            return None
    except Exception as e:
        logger.exception(f"Error getting video info: {str(e)}")
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
        logger.info(f"Starting download for: {url}")
        logger.info(f"Output path: {output_path}")
        logger.info(f"Quality: {quality}")
        
        # Create output directory if it doesn't exist
        if output_path and not os.path.exists(output_path):
            logger.info(f"Creating output directory: {output_path}")
            os.makedirs(output_path)
        
        # Get yt-dlp path
        yt_dlp_path = get_yt_dlp_path()
        if not yt_dlp_path:
            error_msg = "yt-dlp not found or could not be downloaded"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # Get ffmpeg path
        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            logger.warning("ffmpeg not found. Attempting to download...")
            ffmpeg_path = get_ffmpeg_path()  # Try again after download attempt
            if not ffmpeg_path:
                logger.warning("Failed to download ffmpeg. Some videos may not download correctly.")
        
        # Get video info first
        logger.info("Fetching video information...")
        video_info = get_video_info(url)
        
        # Non-interactive mode for GUI integration
        use_specific_format = False
        
        if video_info:
            try:
                logger.info(f"Video from: @{video_info.get('uploader', 'Unknown')}")
                description = video_info.get('description', 'No description')
                # Handle potential encoding issues with description
                if description:
                    description = description.encode('ascii', 'replace').decode('ascii')
                logger.info(f"Tweet text: {description}")
            except UnicodeEncodeError:
                logger.warning("Video information contains special characters that couldn't be displayed")
            
            # For non-interactive mode, just use the quality parameter
            format_id = quality
            logger.info(f"Using format: {format_id}")
        else:
            # If we couldn't get video info, use the best format
            format_id = quality
            logger.warning(f"Could not get video info, defaulting to format: {format_id}")
        
        # Prepare the output template
        # Use a template that includes the tweet author and date
        output_template = os.path.join(output_path, "%(uploader)s_%(upload_date)s_%(id)s.%(ext)s") if output_path else "%(uploader)s_%(upload_date)s_%(id)s.%(ext)s"
        logger.info(f"Output template: {output_template}")
        
        # Log the files in the output directory before download
        if output_path and os.path.exists(output_path):
            files_before = os.listdir(output_path)
            logger.debug(f"Files in output directory before download: {files_before}")
        
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
            "--write-thumbnail",       # Save thumbnail
            "--verbose"                # Add verbose output for debugging
        ]
        
        # Add ffmpeg location if we found it
        if ffmpeg_path:
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
            cmd.extend(["--ffmpeg-location", ffmpeg_dir])
            logger.info(f"Using ffmpeg from: {ffmpeg_dir}")
        
        logger.info(f"Downloading video from: {url}")
        logger.info(f"Format: {format_id}")
        logger.debug(f"Command: {' '.join(cmd)}")
        
        # Run the command with encoding handling
        process = subprocess.run(cmd, 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True,
                              encoding='utf-8',
                              errors='replace')
        
        # Log the complete output for debugging
        logger.debug(f"Command stdout: {process.stdout}")
        logger.debug(f"Command stderr: {process.stderr}")
        
        # Check if the download was successful
        if process.returncode == 0:
            logger.info("Download process completed with return code 0")
            
            # Log the files in the output directory after download
            if output_path and os.path.exists(output_path):
                files_after = os.listdir(output_path)
                logger.debug(f"Files in output directory after download: {files_after}")
                
                # Find new files
                new_files = set(files_after) - set(files_before) if 'files_before' in locals() else set(files_after)
                logger.info(f"New files created: {new_files}")
            
            # Try to find the downloaded file
            if output_path:
                # Parse the output to find the filename
                output_lines = process.stdout.splitlines()
                filename = None
                for line in output_lines:
                    if "Destination:" in line:
                        filename = line.split("Destination:", 1)[1].strip()
                        logger.info(f"Found destination filename in output: {filename}")
                        break
                
                if filename and os.path.exists(filename):
                    file_size = os.path.getsize(filename) / (1024 * 1024)  # in MB
                    logger.info(f"Download successful. File: {filename}, Size: {file_size:.2f} MB")
                    return f"Success: Video downloaded successfully! Saved to: {filename} File size: {file_size:.2f} MB"
                
                # If we couldn't find the filename in the output, look for the most recent file
                files = os.listdir(output_path)
                if files:
                    # Get the most recently modified file
                    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(output_path, f)))
                    if latest_file.endswith(('.mp4', '.webm')):
                        file_path = os.path.join(output_path, latest_file)
                        file_size = os.path.getsize(file_path) / (1024 * 1024)  # in MB
                        logger.info(f"Found most recent video file: {file_path}, Size: {file_size:.2f} MB")
                        return f"Success: Video downloaded successfully! Saved to: {file_path} File size: {file_size:.2f} MB"
                    else:
                        logger.warning(f"Most recent file is not a video: {latest_file}")
                else:
                    logger.warning(f"No files found in output directory: {output_path}")
            
            logger.info("Download reported as successful but couldn't find the specific file")
            return "Success: Video downloaded successfully!"
        else:
            error_msg = process.stderr.strip() if process.stderr else "Unknown error"
            # Handle potential encoding issues in error message
            if error_msg:
                error_msg = error_msg.encode('ascii', 'replace').decode('ascii')
            logger.error(f"Download failed: {error_msg}")
            return f"Error: {error_msg}"
    
    except UnicodeEncodeError as ue:
        logger.exception(f"Unicode encoding error: {str(ue)}")
        return f"Error with character encoding: Some special characters couldn't be processed"
    except Exception as e:
        # Ensure the error message is ASCII-compatible
        error_str = str(e)
        safe_error = error_str.encode('ascii', 'replace').decode('ascii')
        logger.exception(f"Download exception: {safe_error}")
        return f"Error: {safe_error}"

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

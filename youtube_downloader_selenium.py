#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YouTube Shorts Downloader (Selenium Version)
A simple Python script to download videos from YouTube Shorts using Selenium.
This version can bypass most YouTube restrictions by simulating a real browser.
"""

import os
import re
import sys
import time
import urllib.request
import urllib.error
from urllib.parse import parse_qs, urlparse
import json
import tempfile
import shutil
import platform
import subprocess
from datetime import datetime

def get_chrome_version():
    """Get the installed Chrome version."""
    if platform.system() == 'Windows':
        try:
            # Try to get Chrome version from registry
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
            version, _ = winreg.QueryValueEx(key, 'version')
            return version
        except:
            # If registry method fails, try the executable method
            try:
                chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
                if not os.path.exists(chrome_path):
                    chrome_path = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
                
                output = subprocess.check_output(f'wmic datafile where name="{chrome_path.replace("\\", "\\\\")}" get Version /value', shell=True)
                version = output.decode('utf-8').strip().split('=')[1]
                return version
            except:
                pass
    
    # If all methods fail, return None
    return None

def download_webdriver():
    """
    Download and extract the appropriate webdriver for Chrome.
    Returns the path to the webdriver executable.
    """
    try:
        # Create a directory for the webdriver if it doesn't exist
        script_dir = os.path.dirname(os.path.abspath(__file__))
        webdriver_dir = os.path.join(script_dir, "webdriver")
        if not os.path.exists(webdriver_dir):
            os.makedirs(webdriver_dir)
        
        # Check if webdriver already exists
        webdriver_path = os.path.join(webdriver_dir, "chromedriver.exe")
        
        # Get Chrome version
        chrome_version = get_chrome_version()
        if chrome_version:
            major_version = chrome_version.split('.')[0]
            print(f"Detected Chrome version: {chrome_version} (Major: {major_version})")
        else:
            print("Could not detect Chrome version. Will try to use latest ChromeDriver.")
            major_version = None
        
        print("Downloading compatible ChromeDriver...")
        
        # Use Chrome for Testing API to get the latest driver version
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json"
        
        with urllib.request.urlopen(api_url) as response:
            versions_data = json.loads(response.read().decode('utf-8'))
        
        # Find the matching version or closest available version
        if major_version and major_version in versions_data['milestones']:
            driver_version = versions_data['milestones'][major_version]['version']
            driver_download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{driver_version}/win64/chromedriver-win64.zip"
        else:
            # Use the latest stable version
            driver_version = versions_data['milestones']['stable']['version']
            driver_download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{driver_version}/win64/chromedriver-win64.zip"
        
        print(f"Downloading ChromeDriver version {driver_version}...")
        
        # Download the zip file
        temp_file = os.path.join(tempfile.gettempdir(), "chromedriver.zip")
        urllib.request.urlretrieve(driver_download_url, temp_file)
        
        # Extract the zip file
        import zipfile
        with zipfile.ZipFile(temp_file, 'r') as zip_ref:
            zip_ref.extractall(webdriver_dir)
        
        # Move the chromedriver.exe file to the right location
        extracted_driver = os.path.join(webdriver_dir, "chromedriver-win64", "chromedriver.exe")
        if os.path.exists(extracted_driver):
            if os.path.exists(webdriver_path):
                os.remove(webdriver_path)
            shutil.move(extracted_driver, webdriver_path)
            
            # Clean up the extracted directory
            shutil.rmtree(os.path.join(webdriver_dir, "chromedriver-win64"))
        
        # Clean up
        os.remove(temp_file)
        
        print(f"ChromeDriver downloaded to {webdriver_path}")
        return webdriver_path
    
    except Exception as e:
        print(f"Error downloading webdriver: {e}")
        print("Please download ChromeDriver manually from: https://googlechromelabs.github.io/chrome-for-testing/")
        return None

def extract_video_id(url):
    """Extract the YouTube video ID from a URL."""
    # Check for shorts URL format
    shorts_match = re.match(r'https?://(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]+)', url)
    if shorts_match:
        return shorts_match.group(1)
    
    # Check for standard YouTube URL format
    parsed_url = urlparse(url)
    if parsed_url.netloc in ('youtube.com', 'www.youtube.com') and parsed_url.path == '/watch':
        query_params = parse_qs(parsed_url.query)
        if 'v' in query_params:
            return query_params['v'][0]
    
    # Check for youtu.be format
    if parsed_url.netloc == 'youtu.be':
        return parsed_url.path.lstrip('/')
    
    return None

def validate_youtube_url(url):
    """
    Validate if the URL is a YouTube URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if valid YouTube URL, False otherwise
    """
    return extract_video_id(url) is not None

def download_youtube_video(url, output_path=None):
    """
    Download a YouTube video using direct video URL extraction.
    
    Args:
        url (str): The YouTube video URL
        output_path (str, optional): The directory to save the video. Defaults to current directory.
        
    Returns:
        str: Success or error message
    """
    try:
        # Extract video ID
        video_id = extract_video_id(url)
        if not video_id:
            return "Error: Could not extract video ID from URL."
        
        # Create output directory if it doesn't exist
        if output_path and not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Try to import selenium
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            print("Selenium is not installed. Installing now...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
            
            # Import again after installation
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        
        # Download webdriver if needed
        webdriver_path = download_webdriver()
        if not webdriver_path:
            return "Error: Could not download webdriver."
        
        # Set up Chrome options
        chrome_options = Options()
        # Don't use headless mode for blob URLs
        # chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--mute-audio")
        
        # Set up user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
        
        # Create a new Chrome browser instance
        service = Service(executable_path=webdriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Navigate to the YouTube video
            print(f"Accessing YouTube video: {url}")
            driver.get(url)
            
            # Wait for the video to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
            except:
                print("Video element not found. Trying alternative method...")
            
            # Get video information
            try:
                title_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.title, h1.style-scope.ytd-watch-metadata"))
                )
                video_title = title_element.text.strip()
            except:
                video_title = f"YouTube_Video_{video_id}"
                print(f"Could not get video title. Using default: {video_title}")
            
            # Generate a safe filename
            safe_title = re.sub(r'[\\/*?:"<>|]', "_", video_title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_path, f"{safe_title}_{timestamp}.mp4")
            
            # Try to download using yt-dlp first (most reliable method)
            print("Trying to download with yt-dlp...")
            try:
                # Check if we have yt-dlp in the same directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                yt_dlp_path = os.path.join(script_dir, "yt-dlp.exe")
                
                # If not, download it
                if not os.path.exists(yt_dlp_path):
                    print("Downloading yt-dlp...")
                    yt_dlp_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
                    urllib.request.urlretrieve(yt_dlp_url, yt_dlp_path)
                
                # Use yt-dlp to download the video directly with high quality
                import subprocess
                cmd = [
                    yt_dlp_path, 
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", 
                    "-o", output_file, 
                    "--merge-output-format", "mp4",
                    url
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(output_file):
                    # Get file size
                    file_size = os.path.getsize(output_file) / (1024 * 1024)  # in MB
                    return f"Success: Video downloaded successfully with yt-dlp!\nTitle: {video_title}\nSaved to: {output_file}\nFile size: {file_size:.2f} MB"
                else:
                    print("yt-dlp download failed. Trying browser method...")
            except Exception as e:
                print(f"yt-dlp download failed: {e}")
            
            # If yt-dlp failed, try browser download method
            print("Using browser download method...")
            
            # Method for downloading blob URLs
            download_script = """
            async function downloadVideo() {
                const videoElement = document.querySelector('video');
                if (!videoElement) {
                    return { success: false, error: 'No video element found' };
                }
                
                // Create a MediaSource
                const mediaSource = new MediaSource();
                const sourceBuffer = await new Promise((resolve) => {
                    mediaSource.addEventListener('sourceopen', () => {
                        const sourceBuffer = mediaSource.addSourceBuffer('video/mp4; codecs="avc1.42E01E, mp4a.40.2"');
                        resolve(sourceBuffer);
                    });
                    videoElement.src = URL.createObjectURL(mediaSource);
                });
                
                // Get video data
                const videoSrc = videoElement.currentSrc || videoElement.src;
                if (!videoSrc) {
                    return { success: false, error: 'No video source found' };
                }
                
                try {
                    // For blob URLs, we need to download the content
                    const response = await fetch(videoSrc);
                    const blob = await response.blob();
                    
                    // Create a download link
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = 'video.mp4';
                    a.style.display = 'none';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    
                    return { success: true, message: 'Video download initiated' };
                } catch (error) {
                    return { success: false, error: error.toString() };
                }
            }
            
            return downloadVideo();
            """
            
            # Execute the download script
            result = driver.execute_script(download_script)
            
            if result and result.get('success'):
                print("Browser download initiated. Please check your downloads folder.")
                
                # Wait for download to complete (this is a simple approach)
                print("Waiting for download to complete...")
                time.sleep(10)  # Wait 10 seconds for download to start
                
                # Try to find the downloaded file
                downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                downloaded_file = None
                
                # Look for recently downloaded mp4 files
                for file in os.listdir(downloads_dir):
                    if file.endswith(".mp4") and os.path.getmtime(os.path.join(downloads_dir, file)) > time.time() - 60:
                        downloaded_file = os.path.join(downloads_dir, file)
                        break
                
                if downloaded_file:
                    # Move the file to the desired location
                    shutil.move(downloaded_file, output_file)
                    file_size = os.path.getsize(output_file) / (1024 * 1024)  # in MB
                    return f"Success: Video downloaded successfully via browser!\nTitle: {video_title}\nSaved to: {output_file}\nFile size: {file_size:.2f} MB"
            
            # If browser download failed, try Method 4 (yt-dlp URL extraction)
            print("Browser download failed. Trying yt-dlp URL extraction...")
            try:
                # Use yt-dlp to get the video URL
                import subprocess
                cmd = [yt_dlp_path, "-g", url]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    video_url = result.stdout.strip()
                    
                    # Download with progress reporting
                    def report_progress(block_num, block_size, total_size):
                        if total_size > 0:
                            percent = min(100, int(block_num * block_size * 100 / total_size))
                            sys.stdout.write(f"\rProgress: {percent}% [{block_num * block_size}/{total_size} bytes]")
                            sys.stdout.flush()
                    
                    print(f"Downloading video: {video_title}")
                    print(f"From URL: {video_url[:100]}...")  # Only show the beginning of the URL
                    
                    urllib.request.urlretrieve(video_url, output_file, reporthook=report_progress)
                    print("\nDownload complete!")
                    
                    # Get file size
                    file_size = os.path.getsize(output_file) / (1024 * 1024)  # in MB
                    
                    return f"Success: Video downloaded successfully with URL extraction!\nTitle: {video_title}\nSaved to: {output_file}\nFile size: {file_size:.2f} MB"
            except Exception as e:
                print(f"yt-dlp URL extraction failed: {e}")
            
            return "Error: Could not download the video using any method. Please try the simple version instead."
        
        finally:
            # Close the browser
            driver.quit()
    
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main function to run the YouTube Shorts downloader."""
    print("=" * 60)
    print("YouTube Shorts Downloader (Selenium Version)".center(60))
    print("=" * 60)
    print("This version uses Selenium to bypass YouTube restrictions.")
    
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

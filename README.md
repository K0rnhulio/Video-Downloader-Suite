# Video Downloader Suite

A comprehensive suite of tools to download videos from YouTube, Twitter/X, Instagram, Facebook, and TikTok with the highest available resolution.

## Features

- Download YouTube videos with the highest available resolution
- Download Twitter/X videos with ease
- Download Instagram videos, reels, and stories
- Download Facebook videos, posts, and stories
- Download TikTok videos without watermarks
- Support for various URL formats (including YouTube Shorts and Twitter/X posts)
- Custom download directory option
- Video quality selection
- User-friendly command-line interface
- Multiple download methods to bypass platform restrictions

## Requirements

- Python 3.6 or higher

## Installation

1. Clone or download this repository
2. No additional installation required! All dependencies are automatically downloaded.

## Usage

### YouTube Downloaders

We provide five different methods to download YouTube videos. If one method doesn't work, try another:

#### 1. High Quality Version (Best Quality)

The specialized version for getting the absolute highest quality videos:

```bash
python youtube_downloader_hq.py
```

Or simply double-click the `run_downloader_hq.bat` file.

Features:
- Automatically downloads yt-dlp and ffmpeg
- Shows all available video formats
- Allows manual format selection
- Merges best video and audio streams for maximum quality
- Displays detailed video information and resolution

#### 2. Simple Version (Recommended)

The simplest and most reliable version using yt-dlp:

```bash
python youtube_downloader_simple.py
```

Or simply double-click the `run_downloader_simple.bat` file.

Features:
- Automatically downloads yt-dlp
- Allows quality selection (best, 1080p, 720p, 480p, 360p)
- Most reliable method

#### 3. Main Version (using pytube)

Run the script:

```bash
python youtube_downloader.py
```

Or simply double-click the `run_downloader.bat` file.

#### 4. Alternative Version (using yt-dlp)

If you encounter issues with the main version, try the alternative version:

```bash
python youtube_downloader_alt.py
```

Or simply double-click the `run_downloader_alt.bat` file.

#### 5. Selenium Version (using browser automation)

If both methods above fail, try the Selenium version which uses browser automation:

```bash
python youtube_downloader_selenium.py
```

Or simply double-click the `run_downloader_selenium.bat` file.

### Twitter/X Downloader

Download videos from Twitter/X:

```bash
python twitter_downloader.py
```

Or simply double-click the `run_twitter_downloader.bat` file.

Features:
- Automatically downloads yt-dlp
- Automatically downloads and installs ffmpeg
- Extracts video metadata from tweets
- Saves videos with username and date in filename
- Multiple quality options

### Instagram Downloader

Download videos from Instagram:

```bash
python instagram_downloader.py
```

Or simply double-click the `run_instagram_downloader.bat` file.

Features:
- Automatically downloads yt-dlp
- Automatically downloads and installs ffmpeg
- Extracts video metadata from posts
- Saves videos with username and date in filename
- Multiple quality options
- Works with posts, reels, and stories

### Facebook Downloader

Download videos from Facebook:

```bash
python facebook_downloader.py
```

Or simply double-click the `run_facebook_downloader.bat` file.

Features:
- Automatically downloads yt-dlp
- Automatically downloads and installs ffmpeg
- Extracts video metadata from posts
- Saves videos with username and date in filename
- Multiple quality options
- Works with posts, reels, and stories
- Smart download strategy:
  * Tries without cookies first (for public videos)
  * Uses browser cookies as fallback (for authenticated content)
  * Tries mobile URL as last resort
- Supports geo-bypass for region-restricted content

### TikTok Downloader (No Watermark)

Download videos from TikTok without watermarks:

```bash
python tiktok_downloader.py
```

Or simply double-click the `run_tiktok_downloader.bat` file.

Features:
- Automatically downloads yt-dlp
- Automatically downloads and installs ffmpeg
- Removes TikTok watermarks from videos
- Multiple quality options
- Works with all TikTok video formats
- Smart download strategy with multiple fallback methods
- Supports both public and private videos
- Default download location: `~/Downloads/TikTok_Videos/`

### All-in-One Launcher

For convenience, you can use the all-in-one launcher to access all downloaders:

```bash
run_all_downloaders.bat
```

This will present a menu where you can choose which downloader to use.

### Instructions

Follow the prompts:
1. Enter the video URL (YouTube, Twitter/X, Instagram, Facebook, or TikTok)
2. Select video quality or format (depending on the version)
3. Choose whether to use the default download directory or specify a custom one
4. Wait for the download to complete

## Troubleshooting

### HTTP Error 403: Forbidden

If you encounter this error with the main version:
1. Try the high quality or simple version (recommended)
2. Try the alternative version which uses yt-dlp
3. If that doesn't work, try the Selenium version which simulates a real browser

### The system cannot find the file specified

If you encounter this error:
- All versions now automatically download their required dependencies
- No manual installation is required

### ChromeDriver Version Issues

If you encounter ChromeDriver compatibility issues with the Selenium version:
- Use the high quality or simple version instead, which doesn't require ChromeDriver

### Other Issues

If you encounter any other issues:
1. Try each version in order (high quality → simple → main → alternative → Selenium)
2. The high quality and simple versions are the most reliable and recommended options

## Default Download Location

By default, videos are saved to:
- High Quality Version: `~/Downloads/YouTube_Videos_HQ/`
- Twitter/X Version: `~/Downloads/Twitter_Videos/`
- Instagram Version: `~/Downloads/Instagram_Videos/`
- Facebook Version: `~/Downloads/Facebook_Videos/`
- TikTok Version: `~/Downloads/TikTok_Videos/`
- Other Versions: `~/Downloads/YouTube_Videos/`

## Disclaimer

This script is provided for educational and personal use only. Downloading copyrighted material without proper authorization may infringe upon the rights of content creators. The developer of this script is not responsible for any misuse or legal issues that may arise from using this script.

## License

MIT License

# Video Downloader Suite - Platform Support

This document provides an overview of the different platform-specific downloaders in this project.

## Overview

| Downloader | Platform | Library | Features | Quality | Fallback Methods |
|------------|----------|---------|-----------|---------|-----------------|
| YouTube | YouTube | yt-dlp | Full format selection, metadata extraction | Highest (4K+) | Built-in yt-dlp fallbacks |
| Twitter/X | Twitter/X | yt-dlp | Tweet metadata, author info | Best available | Multiple fallbacks |
| Facebook | Facebook | yt-dlp | Post metadata, authenticated content | Best available | Cookie-based, mobile URL |
| Instagram | Instagram | yt-dlp | Post/reel/story support | Best available | Multiple fallbacks |
| TikTok | TikTok | yt-dlp | No watermark downloads | Best available | Multiple fallbacks |

## Architecture

All downloaders inherit from the `DownloaderBase` class, which provides:
- Centralized dependency management (yt-dlp, ffmpeg)
- Standardized logging
- Common error handling
- Unified download interface
- Cross-platform compatibility

## Platform-Specific Features

### 1. YouTube Downloader
- Shows all available video formats
- Supports manual quality selection
- Merges best video and audio streams
- Displays detailed video information
- Advanced format selection (bestvideo+bestaudio)
- Custom download directories
- Comprehensive metadata extraction

### 2. Twitter/X Downloader
- Specialized for Twitter/X videos
- Extracts tweet metadata
- Includes username and date in filename
- Multiple quality options
- Shows tweet text and author information

### 3. Facebook Downloader
- Support for videos, posts, and reels
- Smart authentication handling:
  * Public video download
  * Cookie-based authentication
  * Mobile URL fallback
- Geo-bypass for region-restricted content
- Post metadata extraction

### 4. Instagram Downloader
- Support for posts, reels, and stories
- Post metadata extraction
- Author information preservation
- Quality selection options
- Private content handling

### 5. TikTok Downloader
- Watermark-free downloads
- High-quality video extraction
- Multiple download methods
- Robust URL validation
- Metadata preservation
- Region bypass capabilities

## Download Directories

Each platform has its dedicated download directory:
- YouTube: `~/Downloads/YouTube_Videos_HQ/`
- Twitter/X: `~/Downloads/Twitter_Videos/`
- Instagram: `~/Downloads/Instagram_Videos/`
- Facebook: `~/Downloads/Facebook_Videos/`
- TikTok: `~/Downloads/TikTok_Videos/`

## Common Features

All downloaders include:
- Automatic dependency management
- Progress tracking
- Error handling and recovery
- Logging system
- Custom download paths
- URL validation
- Metadata extraction
- Quality selection

# Video Downloader - Quick Start Guide

## Getting Started

This guide will help you quickly get started with the Video Downloader suite.

## Which Downloader Should I Use?

### For YouTube Videos:

#### 1. For Maximum Quality (4K and above)

Use the **High Quality Downloader**:
- Double-click `run_downloader_hq.bat`
- Shows all available formats
- Best for getting the absolute highest quality

#### 2. For Simple, Reliable Downloads

Use the **Simple Downloader**:
- Double-click `run_downloader_simple.bat`
- Easy quality selection
- Most reliable for everyday use

### For Twitter/X Videos:

Use the **Twitter/X Downloader**:
- Double-click `run_twitter_downloader.bat`
- Specialized for Twitter/X videos
- Automatically downloads yt-dlp and ffmpeg
- Saves videos with username and date

### For Instagram Videos:

Use the **Instagram Downloader**:
- Double-click `run_instagram_downloader.bat`
- Specialized for Instagram videos, reels, and stories
- Automatically downloads yt-dlp and ffmpeg
- Saves videos with username and date

### For Facebook Videos:

Use the **Facebook Downloader**:
- Double-click `run_facebook_downloader.bat`
- Specialized for Facebook videos, posts, and reels
- Automatically downloads yt-dlp and ffmpeg
- Smart download strategy with multiple fallbacks
- Saves videos with username and date

### For TikTok Videos:

Use the **TikTok Downloader**:
- Double-click `run_tiktok_downloader.bat`
- Specialized for TikTok videos without watermarks
- Automatically downloads yt-dlp and ffmpeg
- Smart download strategy with multiple fallbacks
- Removes TikTok watermarks from videos

### If You're Not Sure

Use the **All-in-One Launcher**:
- Double-click `run_all_downloaders.bat`
- Choose from all available downloaders
- Recommended for first-time users

## Step-by-Step Instructions

### For YouTube Videos:

1. **Launch the downloader** of your choice (see above)

2. **Enter a YouTube URL** when prompted
   - Regular videos: `https://www.youtube.com/watch?v=VIDEO_ID`
   - Shorts: `https://www.youtube.com/shorts/VIDEO_ID`
   - Shortened links: `https://youtu.be/VIDEO_ID`

3. **Select video quality**
   - High Quality Downloader: You can select from all available formats
   - Simple Downloader: Choose from best, 1080p, 720p, 480p, or 360p
   - Other downloaders: Follow the on-screen prompts

4. **Choose download location**
   - Use the default location or specify your own
   - Default locations:
     - High Quality: `~/Downloads/YouTube_Videos_HQ/`
     - Others: `~/Downloads/YouTube_Videos/`

5. **Wait for download to complete**
   - The downloader will show progress and file information
   - Downloaded files will be saved as MP4 videos

### For Twitter/X Videos:

1. **Launch the Twitter/X downloader**
   - Double-click `run_twitter_downloader.bat`

2. **Enter a Twitter/X URL** when prompted
   - Format: `https://twitter.com/username/status/TWEET_ID`
   - Or: `https://x.com/username/status/TWEET_ID`

3. **Select video quality**
   - Choose from best, medium, or worst quality

4. **Choose download location**
   - Use the default location or specify your own
   - Default location: `~/Downloads/Twitter_Videos/`

5. **Wait for download to complete**
   - The downloader will show progress and file information
   - Downloaded files will include the username and date in the filename

### For Instagram Videos:

1. **Launch the Instagram downloader**
   - Double-click `run_instagram_downloader.bat`

2. **Enter an Instagram URL** when prompted
   - Posts: `https://www.instagram.com/p/POST_ID/`
   - Reels: `https://www.instagram.com/reels/REEL_ID/`
   - Stories: `https://www.instagram.com/stories/USERNAME/STORY_ID/`

3. **Select video quality**
   - Choose from best, medium, or worst quality

4. **Choose download location**
   - Use the default location or specify your own
   - Default location: `~/Downloads/Instagram_Videos/`

5. **Wait for download to complete**
   - The downloader will show progress and file information
   - Downloaded files will include the username and date in the filename

### For Facebook Videos:

1. **Launch the Facebook downloader**
   - Double-click `run_facebook_downloader.bat`

2. **Enter a Facebook URL** when prompted
   - Posts: `https://www.facebook.com/USERNAME/videos/VIDEO_ID/`
   - Reels: `https://www.facebook.com/reel/REEL_ID`
   - Watch: `https://www.facebook.com/watch?v=VIDEO_ID`

3. **Select video quality**
   - Choose from best, medium, or worst quality

4. **Choose download location**
   - Use the default location or specify your own
   - Default location: `~/Downloads/Facebook_Videos/`

5. **Wait for download to complete**
   - The downloader will show progress and file information
   - Downloaded files will use a simplified filename format

### For TikTok Videos:

1. **Launch the TikTok downloader**
   - Double-click `run_tiktok_downloader.bat`

2. **Enter a TikTok URL** when prompted
   - Standard: `https://www.tiktok.com/@USERNAME/video/VIDEO_ID`
   - Short: `https://vm.tiktok.com/XXXX/`
   - Mobile: `https://m.tiktok.com/v/VIDEO_ID`

3. **Select video quality**
   - Choose from best, medium, or worst quality

4. **Choose download location**
   - Use the default location or specify your own
   - Default location: `~/Downloads/TikTok_Videos/`

5. **Wait for download to complete**
   - The downloader will show progress and file information
   - Downloaded files will have the watermark removed

## Troubleshooting

### If a download fails:

1. **Try another downloader**
   - Use the All-in-One Launcher to easily switch between downloaders
   - For YouTube: Try in this order: High Quality → Simple → Main → Alternative → Selenium
   - For Twitter/X, Instagram, Facebook, or TikTok: Their specialized downloaders should work for most videos

2. **Check your internet connection**
   - Make sure you have a stable connection

3. **Verify the URL**
   - Make sure the URL is correct and the video exists
   - Try copying the URL directly from your browser

4. **Look for error messages**
   - The downloader will display specific error messages
   - These can help identify the issue

## Need More Help?

For more detailed information:
- See `README.md` for full documentation
- Check `DOWNLOADERS_COMPARISON.md` for a detailed comparison of all downloaders

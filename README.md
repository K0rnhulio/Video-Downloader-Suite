# Media Downloader with GUI

A comprehensive multi-platform video downloader with a user-friendly GUI supporting YouTube, Twitter, Facebook, Instagram, and TikTok.

## Features

- **Multi-platform Support**: Download videos from YouTube, Twitter, Facebook, Instagram, and TikTok
- **User-friendly GUI**: Simple and intuitive interface for easy video downloading
- **Quality Options**: Choose between best, medium, or worst quality for each platform
- **Comprehensive Logging**: Detailed logs for troubleshooting and tracking download history
- **Error Handling**: Robust error handling for a smooth user experience
- **Unicode Support**: Properly handles video titles and descriptions with special characters and emojis

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/K0rnhulio/Media-Downloader-with-GUI.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Download and install the required binary files:
   - [yt-dlp](https://github.com/yt-dlp/yt-dlp/releases) (Place in the root directory)
   - [ffmpeg](https://ffmpeg.org/download.html) (Create an 'ffmpeg' folder and place the binaries there)

## Usage

1. Run the GUI application:
   ```
   python video_downloader_gui.py
   ```
   
   Or use the provided batch file:
   ```
   run_gui.bat
   ```

2. Enter the URL of the video you want to download
3. Select the platform from the dropdown menu
4. Choose the desired quality
5. Click "Download" and wait for the process to complete

## Download Locations

- YouTube Videos: `~/Downloads/YouTube_Videos/`
- Twitter Videos: `~/Downloads/Twitter_Videos/`
- Facebook Videos: `~/Downloads/Facebook_Videos/`
- Instagram Videos: `~/Downloads/Instagram_Videos/`
- TikTok Videos: `~/Downloads/TikTok_Videos/`
- Logs: `~/Downloads/VideoDownloader_Logs/`

## Requirements

- Python 3.x
- yt-dlp
- ffmpeg
- requests
- logging module
- tkinter (for GUI)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

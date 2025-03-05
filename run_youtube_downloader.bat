@echo off
echo YouTube Video Downloader
echo =====================
set /p url="Enter YouTube URL: "
echo Running: python youtube_downloader_hq.py "%url%" --non-interactive
python youtube_downloader_hq.py "%url%" --non-interactive
pause

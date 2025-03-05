@echo off
title Facebook Video Downloader
color 0A
cls
echo ===================================================
echo            Facebook Video Downloader
echo ===================================================
echo.
echo Starting Facebook Video Downloader...
echo.
python "%~dp0facebook_downloader.py"
echo.
echo Press any key to exit...
pause > nul

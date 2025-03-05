@echo off
title Instagram Video Downloader
color 0A
cls
echo ===================================================
echo            Instagram Video Downloader
echo ===================================================
echo.
echo Starting Instagram Video Downloader...
echo.
python "%~dp0instagram_downloader.py"
echo.
echo Press any key to exit...
pause > nul

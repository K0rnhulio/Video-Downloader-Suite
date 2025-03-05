@echo off
title Video Downloader Suite
color 0A
cls

:menu
echo ===================================================
echo               Video Downloader Suite
echo ===================================================
echo.
echo YouTube Downloaders:
echo 1. Main YouTube Downloader (pytube)
echo 2. High Quality YouTube Downloader
echo 3. Simple YouTube Downloader
echo 4. Alternative YouTube Downloader
echo 5. Selenium YouTube Downloader
echo.
echo Other Platforms:
echo 6. Twitter/X Video Downloader
echo 7. Instagram Video Downloader
echo 8. Facebook Video Downloader
echo 9. TikTok Video Downloader (No Watermark)
echo.
echo 0. Exit
echo.
set /p choice=Enter your choice (0-9): 

if "%choice%"=="1" goto youtube
if "%choice%"=="2" goto youtube_hq
if "%choice%"=="3" goto youtube_simple
if "%choice%"=="4" goto youtube_alt
if "%choice%"=="5" goto youtube_selenium
if "%choice%"=="6" goto twitter
if "%choice%"=="7" goto instagram
if "%choice%"=="8" goto facebook
if "%choice%"=="9" goto tiktok
if "%choice%"=="0" goto exit

echo Invalid choice. Please try again.
timeout /t 2 >nul
cls
goto menu

:youtube
cls
echo Starting Main YouTube Downloader...
python "%~dp0youtube_downloader.py"
goto end

:youtube_hq
cls
echo Starting High Quality YouTube Downloader...
python "%~dp0youtube_downloader_hq.py"
goto end

:youtube_simple
cls
echo Starting Simple YouTube Downloader...
python "%~dp0youtube_downloader_simple.py"
goto end

:youtube_alt
cls
echo Starting Alternative YouTube Downloader...
python "%~dp0youtube_downloader_alt.py"
goto end

:youtube_selenium
cls
echo Starting Selenium YouTube Downloader...
python "%~dp0youtube_downloader_selenium.py"
goto end

:twitter
cls
echo Starting Twitter/X Video Downloader...
python "%~dp0twitter_downloader.py"
goto end

:instagram
cls
echo Starting Instagram Video Downloader...
python "%~dp0instagram_downloader.py"
goto end

:facebook
cls
echo Starting Facebook Video Downloader...
python "%~dp0facebook_downloader.py"
goto end

:tiktok
cls
echo Starting TikTok Video Downloader...
python "%~dp0tiktok_downloader.py"
goto end

:exit
exit

:end
cls
echo.
echo ===================================================
echo               Video Downloader Suite
echo ===================================================
echo.
echo Thank you for using Video Downloader Suite!
echo.
echo Press any key to return to the menu...
pause >nul
cls
goto menu

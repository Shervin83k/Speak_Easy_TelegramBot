@echo off
echo Installing FFmpeg for TTS Bot...
echo.

REM Download FFmpeg
echo Downloading FFmpeg...
curl -L -o ffmpeg.zip "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

if errorlevel 1 (
    echo ❌ Failed to download. Trying alternative method...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'"
)

if not exist "ffmpeg.zip" (
    echo ❌ Download failed. Please manually download FFmpeg from:
    echo     https://github.com/BtbN/FFmpeg-Builds/releases
    echo Then extract to C:\ffmpeg and add to PATH
    pause
    exit /b 1
)

REM Extract
echo Extracting FFmpeg...
powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force"

REM Find extracted folder
for /d %%i in (ffmpeg-*) do (
    echo Found folder: %%i
    ren "%%i" "ffmpeg"
)

if not exist "ffmpeg" (
    echo ❌ Extraction failed
    pause
    exit /b 1
)

REM Add to PATH for current session
set PATH=%PATH%;%CD%\ffmpeg\bin

REM Add to system PATH (permanent)
setx PATH "%PATH%;%CD%\ffmpeg\bin"

REM Test
echo Testing FFmpeg...
ffmpeg -version > ffmpeg_test.txt 2>&1

if errorlevel 1 (
    echo ❌ FFmpeg test failed
    type ffmpeg_test.txt
) else (
    echo ✅ FFmpeg installed successfully!
    echo Version info saved to ffmpeg_test.txt
)

del ffmpeg_test.txt >nul 2>&1

echo.
echo ✅ FFmpeg setup complete!
echo You may need to restart your terminal/VS Code for PATH changes to take effect.
echo.
pause
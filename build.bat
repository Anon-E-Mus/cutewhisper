@echo off
REM Build script for CuteWhisper Windows executable
REM This script creates a standalone .exe file

echo ========================================
echo   CuteWhisper Build Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: venv\Scripts\activate
    echo Then run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install PyInstaller if not already installed
echo.
echo [2/5] Checking for PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Clean previous build
echo.
echo [3/5] Cleaning previous build...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build executable
echo.
echo [4/5] Building executable...
echo This may take several minutes...
pyinstaller CuteWhisper.spec --clean

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

REM Copy necessary files
echo.
echo [5/5] Copying configuration files and assets...

REM Copy config files
if not exist "dist\config" mkdir "dist\config"
copy "config\default_config.yaml" "dist\config\" >nul

REM CRITICAL: Copy assets folder (for video animation)
if exist "assets" (
    if not exist "dist\assets" mkdir "dist\assets"
    copy "assets\cute_cat.mp4" "dist\assets\" >nul
    echo [INFO] Assets copied successfully
)

REM Create required directories
if not exist "dist\models" mkdir "dist\models"
if not exist "dist\temp" mkdir "dist\temp"
if not exist "dist\data" mkdir "dist\data"
if not exist "dist\logs" mkdir "dist\logs"

echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo Executable location: dist\CuteWhisper.exe
echo.
echo To distribute:
echo   - Copy the entire "dist" folder
echo   - Users run: CuteWhisper.exe
echo.
echo First run will download Whisper model (~74MB)
echo.
pause

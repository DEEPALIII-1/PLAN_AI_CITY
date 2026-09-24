@echo off
title Plan AI City - One-Time Setup & Installation
color 0b
echo =========================================================
echo       PLAN AI CITY - ONE-TIME ENVIRONMENT SETUP
echo =========================================================
echo.

:: 1. Check Python
echo [1/3] Checking Python installation...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    echo IMPORTANT: Make sure to check "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)
python --version
echo Python is ready!
echo.

:: 2. Install Backend Python Dependencies
echo [2/3] Installing Python Backend dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies failed to install. Retrying with --user flag...
    pip install --user -r requirements.txt
)
echo Backend dependencies installed!
echo.

:: 3. Check Node.js and Install Frontend Packages
echo [3/3] Checking Node.js and installing Frontend packages...
where node >nul 2>nul
if %errorlevel% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\nodejs" (
        set "PATH=%LOCALAPPDATA%\Programs\nodejs;%PATH%"
    ) else if exist "C:\Program Files\nodejs" (
        set "PATH=C:\Program Files\nodejs;%PATH%"
    ) else if exist "C:\Program Files (x86)\nodejs" (
        set "PATH=C:\Program Files (x86)\nodejs;%PATH%"
    )
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js (LTS version) from: https://nodejs.org/
    echo After installing Node.js, run this script again.
    echo.
    pause
    exit /b 1
)

node --version
cd /d "%~dp0frontend"
echo Installing frontend npm packages (this might take 1-2 minutes)...
call npm install
echo Frontend packages installed!
echo.

echo =========================================================
echo   SETUP COMPLETED SUCCESSFULLY!
echo =========================================================
echo You can now run "START_APP.bat" to launch Plan AI City!
echo.
pause

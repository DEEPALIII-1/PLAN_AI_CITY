@echo off
title Plan AI City - Frontend (Port 3000)

:: Auto-detect nodejs in common paths if not in system PATH
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
    echo [ERROR] Node.js is not found on your system!
    echo Please download and install Node.js from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0frontend"
echo ==============================================
echo   Starting Plan AI City Frontend on port 3000
echo ==============================================
npm run dev -- --host 0.0.0.0 --port 3000
pause

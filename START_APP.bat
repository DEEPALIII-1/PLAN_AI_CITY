@echo off
title Plan AI City - Starting Application...
color 0a
echo =========================================================
echo            STARTING PLAN AI CITY PLATFORM
echo =========================================================
echo.
echo [1/2] Launching Backend Server on port 8000...
start "Plan AI City - Backend Server (Port 8000)" cmd /k "call "%~dp0run_backend.bat""

echo [2/2] Launching Frontend Server on port 3000...
start "Plan AI City - Frontend Server (Port 3000)" cmd /k "call "%~dp0run_frontend.bat""

echo.
echo Waiting for servers to initialize...
timeout /t 3 /nobreak >nul

echo Opening browser at http://localhost:3000 ...
start http://localhost:3000

echo.
echo =========================================================
echo   Plan AI City is now running!
echo   - Web App: http://localhost:3000
echo   - Backend API Docs: http://127.0.0.1:8000/docs
echo =========================================================
echo Keep the backend and frontend windows open while using the app.
echo.
pause

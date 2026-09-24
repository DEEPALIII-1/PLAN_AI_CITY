@echo off
title Plan AI City - SQLite Database Viewer
color 0b
echo ===================================================
echo     PLAN AI CITY - SQLITE DATABASE VIEWER
echo ===================================================
echo.
cd /d "%~dp0\backend"
python view_database.py
echo.
echo Press any key to close this viewer...
pause >nul

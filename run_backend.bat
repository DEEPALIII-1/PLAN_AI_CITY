@echo off
cd /d "%~dp0backend"
echo ==============================================
echo   Starting Plan AI City Backend on port 8000
echo ==============================================
python -m uvicorn app.main:app --reload --port 8000
pause

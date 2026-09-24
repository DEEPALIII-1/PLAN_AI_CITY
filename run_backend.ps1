Set-Location "$PSScriptRoot\backend"
Write-Host "==============================================" -ForegroundColor Green
Write-Host "  Starting Plan AI City Backend (Port 8000)   " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Green
python -m uvicorn app.main:app --reload --port 8000

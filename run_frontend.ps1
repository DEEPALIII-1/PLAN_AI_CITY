$env:PATH = "C:\Users\HP\AppData\Local\Programs\nodejs;" + $env:PATH
Set-Location "$PSScriptRoot\frontend"
Write-Host "==============================================" -ForegroundColor Green
Write-Host "  Starting Plan AI City Frontend (Port 3000)  " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Green
npm run dev

@echo off
title Push Plan AI City to GitHub
color 0b
echo =========================================================
echo       PUSH PLAN AI CITY TO GITHUB REPOSITORY
echo =========================================================
echo.
echo Make sure you have created an empty repository on GitHub:
echo   1. Go to https://github.com/new
echo   2. Name your repository (e.g. plan-ai-city)
echo   3. Do NOT check "Add a README" or ".gitignore" (already created)
echo   4. Click "Create repository"
echo   5. Copy the repository URL (e.g. https://github.com/YourUsername/plan-ai-city.git)
echo.
echo =========================================================
set /p REPO_URL="Enter or paste your GitHub Repository URL: "

if "%REPO_URL%"=="" (
    echo [ERROR] No repository URL was entered!
    pause
    exit /b 1
)

echo.
echo Setting remote origin to: %REPO_URL%
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo.
echo Pushing project code and commits to GitHub (main branch)...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo =========================================================
    echo   SUCCESS! Your project is now published on GitHub!
    echo =========================================================
) else (
    echo.
    echo [NOTE] If GitHub asked you to sign in, please complete the sign-in prompt.
    echo If you need a Personal Access Token, visit: https://github.com/settings/tokens
)
echo.
pause

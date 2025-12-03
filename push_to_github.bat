@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Uploading Item AI Assistant to GitHub
echo ========================================
echo.

cd /d "%~dp0"

set GIT="C:\Program Files\Git\bin\git.exe"

echo Checking Git status...
%GIT% status
if errorlevel 1 (
    echo ERROR: Git repository not found
    pause
    exit /b 1
)

echo.
echo Attempting to push to GitHub...
echo Repository: https://github.com/ShreyashPatil123/item-ai-assistant.git
echo.

REM Try push without rules check
%GIT% push origin main --verbose

if errorlevel 1 (
    echo.
    echo ========================================
    echo   Push failed - trying alternative method
    echo ========================================
    echo.
    echo Attempting force push...
    %GIT% push origin main --force --verbose
    
    if errorlevel 1 (
        echo.
        echo ==========================================
        echo   All automated methods failed
        echo ==========================================
        echo.
 echo The repository has protection rules blocking pushes.
        echo.
        echo Please try one of these:
        echo   1. Use GitHub Desktop (recommended)
        echo   2. Go to repo settings and disable branch protection
        echo   3. Upload files via GitHub web interface
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   SUCCESS! Code uploaded to GitHub
echo ========================================
echo.
echo Repository URL:
echo https://github.com/ShreyashPatil123/item-ai-assistant
echo.
echo You can now share this URL with anyone!
echo.
pause

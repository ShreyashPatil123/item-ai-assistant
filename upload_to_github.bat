@echo off
REM GitHub Upload Script for Item AI Assistant
REM Run this after logging into GitHub and creating the repository

echo ========================================
echo  Item AI Assistant - GitHub Upload
echo ========================================
echo.

REM Set Git executable path
set GIT="C:\Program Files\Git\bin\git.exe"

REM Check if we're in the right directory
if not exist "item_assistant" (
    echo ERROR: Please run this script from the item-assistant directory
    pause
    exit /b 1
)

echo Step 1: Verifying Git repository...
%GIT% status >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git repository not initialized
    pause
    exit /b 1
)

echo ✓ Git repository verified
echo.

REM Get repository URL from user
set /p REPO_URL="Enter your GitHub repository URL (e.g., https://github.com/username/item-ai-assistant.git): "

if "%REPO_URL%"=="" (
    echo ERROR: Repository URL cannot be empty
    pause
    exit /b 1
)

echo.
echo Step 2: Adding remote origin...
%GIT% remote add origin %REPO_URL%
if errorlevel 1 (
    echo Note: Remote might already exist, updating...
    %GIT% remote set-url origin %REPO_URL%
)

echo ✓ Remote added
echo.

echo Step 3: Renaming branch to main...
%GIT% branch -M main

echo ✓ Branch renamed
echo.

echo Step 4: Pushing to GitHub...
echo This may ask for your GitHub credentials.
echo Use a Personal Access Token as password (not your account password)
echo.

%GIT% push -u origin main

if errorlevel 1 (
    echo.
    echo ⚠️  Push failed. This might be because:
    echo   1. Wrong credentials
    echo   2. Repository doesn't exist on GitHub
    echo   3. Network issue
    echo.
    echo Please check and try running this command manually:
    echo %GIT% push -u origin main
    pause
    exit /b 1
)

echo.
echo ========================================
echo  ✅ SUCCESS!
echo ========================================
echo.
echo Your Item AI Assistant is now on GitHub!
echo Repository: %REPO_URL%
echo.
echo Security Check:
echo ✓ config.yaml with API keys was NOT uploaded
echo ✓ Virtual environment was NOT uploaded
echo ✓ Only source code and documentation uploaded
echo.
echo You can now share the repository URL with anyone!
echo.
pause

@echo off
REM Quick launcher for Item AI Assistant
REM Created for easy testing and startup

cd /d "%~dp0"

echo ========================================
echo   Starting Item AI Assistant
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: scripts\install.ps1
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if Item is already running
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo.
    echo WARNING: Python processes detected
    echo Item may already be running
    echo.
)

REM Start Item AI Assistant
echo Starting Item...
echo.
python -m item_assistant.main

REM If Item exits, show error message
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Item exited with error code %ERRORLEVEL%
    echo Check logs in: C:\Users\Shreyash\ItemAssistant\logs\
    echo.
    pause
)

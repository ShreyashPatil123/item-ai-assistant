@echo off
REM ============================================================================
REM Item AI Assistant - Start with Desktop UI
REM ============================================================================
REM This batch file starts the Item AI Assistant with the desktop slide-up panel
REM ============================================================================

echo.
echo ============================================================================
echo   Item AI Assistant - Starting with Desktop UI Panel
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if we're in the right directory
if not exist "item_assistant\main.py" (
    echo ERROR: item_assistant\main.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo [OK] Project structure found
echo.

REM Check if config exists
if not exist "item_assistant\config\config.yaml" (
    echo WARNING: config.yaml not found
    echo Creating from template...
    copy item_assistant\config\config.template.yaml item_assistant\config\config.yaml >nul
    if errorlevel 1 (
        echo ERROR: Failed to create config.yaml
        pause
        exit /b 1
    )
    echo [OK] config.yaml created
    echo.
    echo IMPORTANT: Edit config.yaml and set your API keys:
    echo   - voice.wake_word.access_key (Picovoice)
    echo   - llm.online.groq.api_key (Groq)
    echo.
    pause
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import tkinter; print('[OK] Tkinter found')" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Tkinter not found
    echo The UI panel requires Tkinter
    echo Try: pip install tk
    echo.
)

python -c "import pvporcupine; print('[OK] Picovoice found')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Picovoice not installed
    echo Run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [OK] Dependencies found
echo.

REM Start the assistant
echo ============================================================================
echo Starting Item AI Assistant...
echo ============================================================================
echo.
echo Features:
echo   - Desktop slide-up UI panel
echo   - Voice wake word detection
echo   - Real-time status display
echo   - Manual mic button
echo   - Auto-hide on idle
echo.
echo Controls:
echo   - Say wake word (porcupine/picovoice/bumblebee) to start
echo   - Click mic button on panel to listen manually
echo   - Press Ctrl+C to stop
echo.
echo Documentation:
echo   - RUN_WITH_UI.md - Quick start guide
echo   - DESKTOP_UI_GUIDE.md - Complete feature guide
echo   - UI_IMPLEMENTATION_SUMMARY.md - Technical details
echo.
echo ============================================================================
echo.

python -m item_assistant.main

echo.
echo ============================================================================
echo Assistant stopped
echo ============================================================================
pause

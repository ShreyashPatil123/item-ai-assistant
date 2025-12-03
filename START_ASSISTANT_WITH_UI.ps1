# ============================================================================
# Item AI Assistant - Start with Desktop UI
# ============================================================================
# This PowerShell script starts the Item AI Assistant with the desktop slide-up panel
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  Item AI Assistant - Starting with Desktop UI Panel" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "item_assistant\main.py")) {
    Write-Host "ERROR: item_assistant\main.py not found" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Project structure found" -ForegroundColor Green
Write-Host ""

# Check if config exists
if (-not (Test-Path "item_assistant\config\config.yaml")) {
    Write-Host "WARNING: config.yaml not found" -ForegroundColor Yellow
    Write-Host "Creating from template..." -ForegroundColor Yellow
    
    Copy-Item "item_assistant\config\config.template.yaml" "item_assistant\config\config.yaml" -ErrorAction Stop
    Write-Host "[OK] config.yaml created" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Edit config.yaml and set your API keys:" -ForegroundColor Yellow
    Write-Host "  - voice.wake_word.access_key (Picovoice)" -ForegroundColor Yellow
    Write-Host "  - llm.online.groq.api_key (Groq)" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue"
}

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Cyan

try {
    python -c "import tkinter" 2>&1 | Out-Null
    Write-Host "[OK] Tkinter found" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Tkinter not found" -ForegroundColor Yellow
    Write-Host "The UI panel requires Tkinter" -ForegroundColor Yellow
    Write-Host "Try: pip install tk" -ForegroundColor Yellow
    Write-Host ""
}

try {
    python -c "import pvporcupine" 2>&1 | Out-Null
    Write-Host "[OK] Picovoice found" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Picovoice not installed" -ForegroundColor Red
    Write-Host "Run: pip install -r requirements.txt" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Dependencies found" -ForegroundColor Green
Write-Host ""

# Start the assistant
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Starting Item AI Assistant..." -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features:" -ForegroundColor Green
Write-Host "  - Desktop slide-up UI panel" -ForegroundColor Green
Write-Host "  - Voice wake word detection" -ForegroundColor Green
Write-Host "  - Real-time status display" -ForegroundColor Green
Write-Host "  - Manual mic button" -ForegroundColor Green
Write-Host "  - Auto-hide on idle" -ForegroundColor Green
Write-Host ""
Write-Host "Controls:" -ForegroundColor Green
Write-Host "  - Say wake word (porcupine/picovoice/bumblebee) to start" -ForegroundColor Green
Write-Host "  - Click mic button on panel to listen manually" -ForegroundColor Green
Write-Host "  - Press Ctrl+C to stop" -ForegroundColor Green
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Green
Write-Host "  - RUN_WITH_UI.md - Quick start guide" -ForegroundColor Green
Write-Host "  - DESKTOP_UI_GUIDE.md - Complete feature guide" -ForegroundColor Green
Write-Host "  - UI_IMPLEMENTATION_SUMMARY.md - Technical details" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Run the assistant
python -m item_assistant.main

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Assistant stopped" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"

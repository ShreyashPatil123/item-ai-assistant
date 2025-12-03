# Item AI Assistant - Windows Installation Script
# Run this with: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "=" * 80
Write-Host "Item AI Assistant - Installation Script"
Write-Host "=" * 80

# Check Python installation
Write-Host "`nChecking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion"
} catch {
    Write-Host "✗ Python not found. Please install Python 3.9 or higher from python.org"
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..."
python -m venv venv
Write-Host "✓ Virtual environment created"

# Activate virtual environment
Write-Host "`nActivating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "`nUpgrading pip..."
python -m pip install --upgrade pip

# Install requirements
Write-Host "`nInstalling Python dependencies..."
pip install -r requirements.txt
Write-Host "✓ Dependencies installed"

# Copy config template
Write-Host "`nSetting up configuration..."
if (!(Test-Path "item_assistant\config\config.yaml")) {
    Copy-Item "item_assistant\config\config.template.yaml" "item_assistant\config\config.yaml"
    Write-Host "✓ Created config.yaml from template"
} else {
    Write-Host "  Config.yaml already exists, skipping"
}

if (!(Test-Path "item_assistant\config\allowed_apps.json")) {
    Copy-Item "item_assistant\config\allowed_apps.template.json" "item_assistant\config\allowed_apps.json"
    Write-Host "✓ Created allowed_apps.json from template"
} else {
    Write-Host "  allowed_apps.json already exists, skipping"
}

# Check for Ollama
Write-Host "`nChecking Ollama installation..."
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✓ Found Ollama: $ollamaVersion"
    
    # Pull required models
    Write-Host "`nPulling Ollama models..."
    Write-Host "  Pulling llama3.2:3b (general model)..."
    ollama pull llama3.2:3b
    Write-Host "  Pulling codegemma:7b (code model)..."
    ollama pull codegemma:7b
    Write-Host "✓ Models pulled successfully"
    
} catch {
    Write-Host "✗ Ollama not found"
    Write-Host "  Please download and install Ollama from: https://ollama.ai"
    Write-Host "  After installing, run: ollama pull llama3.2:3b && ollama pull codegemma:7b"
}

# Create shortcut for startup
Write-Host "`nSetup complete!"
Write-Host "`n" + "=" * 80
Write-Host "NEXT STEPS:"
Write-Host "=" * 80
Write-Host "1. Edit item_assistant\config\config.yaml and add your API keys:"
Write-Host "   - Picovoice access key (for wake word)"
Write-Host "   - Groq API key (for online LLM)"
Write-Host "   - Google Gemini API key (for fallback LLM)"
Write-Host "`n2. See docs\API_KEYS.md for detailed instructions on getting API keys"
Write-Host "`n3. Start the assistant with:"
Write-Host "   .\venv\Scripts\Activate.ps1"
Write-Host "   python -m item_assistant.main"
Write-Host "`n4. For automatic startup, run: .\scripts\setup_startup.ps1"
Write-Host "=" * 80

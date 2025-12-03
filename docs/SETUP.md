# Setup Guide - Item AI Assistant

Complete setup instructions for Item AI Assistant on Windows with Android phone integration.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Python Environment Setup](#python-environment-setup)
3. [Ollama Installation](#ollama-installation)
4. [Item Installation](#item-installation)
5. [API Keys Configuration](#api-keys-configuration)
6. [Network Configuration](#network-configuration)
7. [Android App Setup](#android-app-setup)
8. [Wake-on-LAN Setup](#wake-on-lan-setup)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **OS**: Windows 10/11  
- **CPU**: 4+ cores (Ryzen 7 or equivalent)  
- **RAM**: 16GB minimum, 24GB recommended  
- **GPU**: RTX 4060 or similar (optional but recommended for faster local LLM)  
- **Storage**: 20GB free space  
- **Network**: Wi-Fi or Ethernet  

### Software Requirements

- Python 3.9 or higher
- PowerShell 5.1 or higher (built into Windows)
- Internet connection (for initial setup and online features)

---

## Python Environment Setup

### 1. Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ **CHECK** "Add Python to PATH"
4. Click "Install Now"

### 2. Verify Installation

```powershell
python --version
# Should print: Python 3.9.x or higher
```

---

## Ollama Installation

Ollama provides local LLM capabilities.

### 1. Download Ollama

Visit [ollama.ai](https://ollama.ai) and download Windows installer.

### 2. Install

Run the installer - it will:
- Install Ollama to `C:\Users\<USER>\AppData\Local\Programs\Ollama`
- Add Ollama to PATH
- Create a system service

### 3. Verify Installation

```powershell
ollama --version
# Should print version info
```

### 4. Pull Required Models

```powershell
# General-purpose model (~2GB)
ollama pull llama3.2:3b

# Code-focused model (~5GB)
ollama pull codegemma:7b
```

This will download models to `~/.ollama/models/`

### 5. Test Ollama

```powershell
ollama run llama3.2:3b "Hello, how are you?"
# Should generate a response
```

---

## Item Installation

### 1. Navigate to Project

```powershell
cd C:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant
```

### 2. Run Installation Script

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install.ps1
```

This script will:
- Create Python virtual environment
- Install all dependencies from `requirements.txt`
- Copy configuration templates
- Pull Ollama models (if not already pulled)
- Display next steps

### 3. Verify Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
python --version
# Should show Python from venv path
```

---

## API Keys Configuration

See [API_KEYS.md](API_KEYS.md) for detailed step-by-step instructions.

### Quick Summary

1. **Picovoice** (wake word)
   - Sign up at [console.picovoice.ai](https://console.picovoice.ai)
   - Copy access key

2. **Groq** (online LLM - primary)
   - Sign up at [console.groq.com](https://console.groq.com)
   - Create API key

3. **Google Gemini** (online LLM - fallback)
   - Get key from [ai.google.dev](https://ai.google.dev)

### Update Config

Edit `item_assistant\config\config.yaml`:

```yaml
voice:
  wake_word:
    access_key: "YOUR_PICOVOICE_KEY"

llm:
  online:
    groq:
      enabled: true
      api_key: "YOUR_GROQ_KEY"
    
    gemini:
      enabled: true
      api_key: "YOUR_GEMINI_KEY"
```

---

## Network Configuration

### Local Network (LAN)

1. **Find Laptop IP**
   ```powershell
   ipconfig
   # Look for IPv4 Address (e.g., 192.168.1.100)
   ```

2. **Configure Firewall**
   ```powershell
   # Run as Administrator
   New-NetFirewallRule -DisplayName "Item AI Assistant" `
     -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow
   ```

### Remote Access (Tailscale - Recommended)

1. **Install Tailscale on Laptop**
   - Download from [tailscale.com](https://tailscale.com)
   - Install and sign in
   - Note your Tailscale IP (e.g., `100.101.102.103`)

2. **Install on Phone**
   - Install Tailscale app from Play Store
   - Sign in with same account

3. **Benefits**
   - Works from anywhere
   - No port forwarding needed
   - Encrypted VPN connection
   - Free for personal use (up to 100 devices)

---

## Android App Setup

### Building the App (Future)

```bash
cd android_app
# Open in Android Studio
# Build APK: Build → Build Bundle(s) / APK → Build APK
# Install generated APK on phone
```

### Configuration

1. Open Item app on phone
2. Go to Settings
3. Enter:
   - **Auth Token**: Copy from `config.yaml` → `security.auth_token`
   - **Laptop IP**: Local IP or Tailscale IP
   - **Port**: 8765 (default)

4. Test connection

---

## Wake-on-LAN Setup

Turn on your laptop remotely!

### 1. Run WoL Setup Script

```powershell
# Run as Administrator
powershell -ExecutionPolicy Bypass -File scripts\setup_wol.ps1
```

This will:
- Detect network adapters
- Show MAC address
- Enable WoL in adapter settings
- Provide BIOS instructions

### 2. BIOS Configuration

1. Restart laptop
2. Press Del, F2, or F12 to enter BIOS
3. Navigate to:
   - "Power Management" OR
   - "Advanced" → "Power Management"
4. Enable:
   - "Wake on LAN" OR
   - "PME Event Wake Up" OR
   - "Power On by PCI-E"
5. Save and Exit (F10)

### 3. Windows Network Adapter

1. Open Device Manager
2. Expand "Network adapters"
3. Right-click your Ethernet adapter → Properties
4. Go to "Power Management" tab
5. Check:
   - ✅ "Allow this device to wake the computer"
   - ✅ "Only allow a magic packet to wake the computer"
6. Click OK

### 4. Add MAC to Config

Edit `config.yaml`:

```yaml
wol:
  enabled: true
  mac_address: "12:34:56:78:9A:BC"  # Your MAC from script
  broadcast_ip: "192.168.1.255"     # Your subnet broadcast
```

---

## Testing

### 1. Start Item

```powershell
cd C:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant
.\venv\Scripts\Activate.ps1
python -m item_assistant.main
```

You should see:
```
================================================================================
Item AI Assistant is now running
Say 'Item' followed by your command
Press Ctrl+C to stop
================================================================================
```

### 2. Test Voice Commands

Say: **"Item, what time is it?"**

Expected:
- Wake word detected
- Command transcribed
- Response spoken via TTS

### 3. Test Desktop Automation

Say: **"Item, open Notepad"**

Expected:
- Notepad opens
- Confirmation spoken

### 4. Test API Server

In another PowerShell window:

```powershell
$headers = @{
    "Authorization" = "Bearer YOUR_AUTH_TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    command = "what time is it"
    source = "api"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8765/api/command" `
    -Method POST -Headers $headers -Body $body
```

### 5. Test Phone Control

1. Ensure phone and laptop on same network
2. Open Item Android app
3. Send command: "open calculator"
4. Verify calculator opens on laptop

---

## Auto-Start on Login

Make Item start automatically when Windows starts.

```powershell
# Run as Administrator
powershell -ExecutionPolicy Bypass -File scripts\setup_startup.ps1
```

This creates a scheduled task that:
- Starts Item on login
- Runs in background
- Waits 30 seconds after boot (configurable)

---

## Troubleshooting

### Python Issues

**"Python not found"**
- Reinstall Python with "Add to PATH" checked

**"Module not found"**
- Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt`

### Ollama Issues

**"Connection refused" to Ollama**
- Ensure Ollama is running: `ollama serve`
- Check if models are pulled: `ollama list`

**Models too large**
- Use smaller models: `llama3.2:1b` instead of `3b`

### Voice Issues

**Wake word not detected**
- Check Picovoice key in config
- Adjust sensitivity in config (0.0-1.0)
- Use higher value for easier detection

**STT not working**
- Verify microphone permissions
- Check Windows Privacy settings → Microphone

### Network Issues

**Phone can't connect**
- Verify laptop IP: `ipconfig`
- Check firewall: Port 8765 must be open
- Test: `curl http://laptop-ip:8765/health` from phone browser

**Tailscale not connecting**
- Ensure both devices logged into same Tailscale account
- Check Tailscale status: `tailscale status`

---

## Next Steps

After successful setup:

1. ✅ Review [USER_CHECKLIST.md](USER_CHECKLIST.md) for complete configuration
2. ✅ Customize `config.yaml` to your preferences
3. ✅ Train custom "Item" wake word at console.picovoice.ai
4. ✅ Explore voice commands and automation workflows
5. ✅ Build and install Android app

---

**Congratulations! Item AI Assistant is ready to use! 🎉**

For issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

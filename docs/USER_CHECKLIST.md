# User Checklist - Item AI Assistant

## What You Need to Provide

This checklist covers everything you need to configure to run Item AI Assistant.

---

## ✅ Step 1: Software Installation

- [ ] **Python 3.9+** installed from [python.org](https://python.org)
- [ ] **Ollama** installed from [ollama.ai](https://ollama.ai)
- [ ] **Git** (optional, if cloning from GitHub)

---

## ✅ Step 2: API Keys (See API_KEYS.md)

### Required for Wake Word
- [ ] **Picovoice access key**
  - Sign up at [console.picovoice.ai](https://console.picovoice.ai)
  - Copy access key to `config.yaml`

### Optional (but recommended) for Online LLM
- [ ] **Groq API key**
  - Sign up at [console.groq.com](https://console.groq.com)
  - Create API key
  - Paste in `config.yaml` → `llm.online.groq.api_key`

- [ ] **Google Gemini API key** (fallback)
  - Get from [ai.google.dev](https://ai.google.dev)
  - Paste in `config.yaml` → `llm.online.gemini.api_key`

---

## ✅ Step 3: System Configuration

### Network Settings
- [ ] Note your laptop's local IP address
  - Run: `ipconfig` in PowerShell
  - Look for "IPv4 Address" (e.g., `192.168.1.100`)

- [ ] Note your laptop's MAC address (for Wake-on-LAN)
  - Run: `ipconfig /all`
  - Look for "Physical Address" (e.g., `12-34-56-78-9A-BC`)
  - Or run `scripts\setup_wol.ps1` to auto-detect

### Router Settings (for remote access)
- [ ] Router admin password
- [ ] Public IP address or DDNS hostname (if using port forwarding)

**OR**

- [ ] Install Tailscale (recommended, easier)
  - [tailscale.com](https://tailscale.com)
  - Install on laptop and phone
  - Note Tailscale IPs

---

## ✅ Step 4: Project Configuration

Edit `item_assistant\config\config.yaml`:

### Personal Info
- [ ] Set `system.user_name` to your name

### Directories
- [ ] Verify `system.log_directory` path
- [ ] Verify `system.data_directory` path
- [ ] Set `desktop.projects.root_directory` to your coding folder

### Safe Folders
Add any custom folders you want Item to access:
- [ ] List in `desktop.safe_folders`

Example:
```yaml
desktop:
  safe_folders:
    - "C:\\Users\\Shreyash\\Documents"
    - "D:\\MyProjects"
    - "C:\\Users\\Shreyash\\Downloads"
```

---

## ✅ Step 5: BIOS/UEFI Settings (for Wake-on-LAN)

- [ ] Restart laptop and enter BIOS
  - Usually press Del, F2, or F12 during boot
- [ ] Find "Power Management" or "Advanced" section
- [ ] Enable "Wake on LAN" or "PME Event Wake Up"
- [ ] Save and exit BIOS

---

## ✅ Step 6: Windows Settings

### Network Adapter
- [ ] Open Device Manager
- [ ] Find your network adapter
- [ ] Right-click → Properties → Power Management
- [ ] Check "Allow this device to wake the computer"
- [ ] Check "Only allow a magic packet to wake the computer"

### Firewall
- [ ] Allow port 8765 (Item API server)
  - Run as Admin: `New-NetFirewallRule -DisplayName "Item AI Assistant" -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow`

---

## ✅ Step 7: Phone Setup (Android App)

When Android app is built:

- [ ] Install APK on phone
- [ ] Copy auth token from `config.yaml` → `security.auth_token`
- [ ] Paste token in Android app settings
- [ ] Enter laptop IP address (local or Tailscale)
- [ ] Test connection

---

## ✅ Step 8: Testing

Run these tests after installation:

### Local Components
- [ ] Test Python environment: `python --version`
- [ ] Test Ollama: `ollama list` (should show models)
- [ ] Test Item startup: `python -m item_assistant.main`

### Voice Components
- [ ] Say wake word and verify recognition
- [ ] Test voice command: "What time is it?"
- [ ] Test TTS response

### Desktop Automation
- [ ] Test: "Item, open Notepad"
- [ ] Test: "Item, close Notepad"

### API Server
- [ ] Test API: `curl http://localhost:8765/health`
- [ ] Test from phone (if setup)

### Online LLMs
- [ ] Test complex code generation
- [ ] Verify Groq connection in logs
- [ ] Verify Gemini fallback works

---

## ✅ Step 9: Optional Enhancements

### Auto-Start on Windows Login
- [ ] Run: `powershell -ExecutionPolicy Bypass -File scripts\setup_startup.ps1`

### Custom Wake Word
- [ ] Train "Item" keyword at [console.picovoice.ai](https://console.picovoice.ai)
- [ ] Download `.ppn` file
- [ ] Update wake word config

### System Tray Icon (Future)
- [ ] Install pystray dependencies
- [ ] Enable in config

---

## 📋 Configuration Summary

After completing this checklist, you should have:

1. ✅ All software installed (Python, Ollama)
2. ✅ API keys configured in `config.yaml`
3. ✅ Network settings noted (IPs, MAC address)
4. ✅ BIOS Wake-on-LAN enabled
5. ✅ Windows firewall configured
6. ✅ Android app connected
7. ✅ All tests passing

---

## 🆘 Stuck?

- Review [API_KEYS.md](API_KEYS.md) for API key issues
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common problems
- Verify `config.yaml` syntax (proper YAML formatting)
- Check logs in `C:\Users\Shreyash\ItemAssistant\logs\`

---

**When everything is checked off, you're ready to use Item! 🎉**

Start with:
```powershell
python -m item_assistant.main
```

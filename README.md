# Item AI Assistant

A comprehensive Jarvis-style AI assistant for Windows with Android phone integration, voice control, desktop automation, and both offline/online LLM capabilities.

## ✨ Features

- 🎤 **Voice Control**: Wake word detection ("Item") + multi-language STT (Hindi, Marathi, English)
- 🤖 **Dual AI Brain**: Local LLMs (Ollama) + free cloud APIs (Groq, Gemini) with smart routing
- 🖥️ **Desktop Automation**: Full control of Windows apps, mouse, keyboard, and browser
- 📱 **Android Integration**: Control from anywhere via custom Android app
- 🔒 **Safety First**: Per-app permissions, confirmation prompts, and folder restrictions
- 🌐 **Remote Access**: Works on same Wi-Fi or globally via Tailscale VPN
- 💻 **Code Assistant**: Generate, debug, and explain code in any language
- 🔄 **Offline Capable**: Full functionality without internet using local models

## 🏗️ Architecture

```
item-assistant/
├── item_assistant/          # Main Python package
│   ├── core/               # Orchestration & action execution
│   ├── llm/                # LLM clients & routing
│   ├── voice/              # Wake word, STT, TTS
│   ├── desktop/            # Desktop automation
│   ├── api/                # HTTP/WebSocket server
│   ├── permissions/        # Safety & permissions
│   ├── logging/            # Logging system
│   ├── config/             # Configuration
│   └── main.py             # Entry point
├── android_app/            # Android app source
├── scripts/                # Setup & utility scripts
├── docs/                   # Documentation
└── requirements.txt        # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Windows 11 (or Windows 10)
- Python 3.9+
- [Ollama](https://ollama.ai) installed
- 24 GB RAM (10 GB for LLMs)
- RTX 4060 or similar GPU (optional but recommended)

### Installation

1. **Clone the repository**
   ```powershell
   cd C:\Users\Shreyash\OneDrive\Desktop\Assistant
   # Project is already in: item-assistant/
   ```

2. **Run the installation script**
   ```powershell
   cd item-assistant
   powershell -ExecutionPolicy Bypass -File scripts\install.ps1
   ```

3. **Configure API keys**
   
   Edit `item_assistant\config\config.yaml` and add:
   - Picovoice access key (wake word)
   - Groq API key (online LLM)
   - Google Gemini API key (fallback)
   
   See [`docs/API_KEYS.md`](docs/API_KEYS.md) for detailed instructions.

4. **Start the assistant**
   ```powershell
   .\venv\Scripts\Activate.ps1
   python -m item_assistant.main
   ```

## 📖 Documentation

- **[Setup Guide](docs/SETUP.md)** - Detailed installation and configuration
- **[API Keys Guide](docs/API_KEYS.md)** - Step-by-step API key acquisition
- **[User Checklist](docs/USER_CHECKLIST.md)** - What you need to provide
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🎯 Usage Examples

### Voice Commands (Laptop)

Say "Item" followed by:
- "Open Chrome"
- "Search for Python tutorials"
- "Open YouTube and play Coldplay"
- "What time is it?"
- "Generate Python code to sort a list"
- "Close Notepad"

### Phone Control

1. Install Android app (APK in `android_app/` after building)
2. Enter auth token from `config.yaml`
3. Configure laptop IP address
4. Send voice or text commands remotely

### API Usage

```python
import requests

headers = {"Authorization": "Bearer YOUR_AUTH_TOKEN"}
data = {"command": "open notepad", "source": "api"}

response = requests.post(
    "http://your-laptop-ip:8765/api/command",
    json=data,
    headers=headers
)
print(response.json())
```

## 🔐 Security & Permissions

### Per-App Permissions

On first use of any app, Item asks for permission:
```
"Can I control Chrome? [Yes/No]"
```

Permissions are stored in `config/allowed_apps.json`.

### Safety Rules

- ✅ Can control apps, mouse, keyboard
- ✅ Can create/modify files in safe folders (Documents, Downloads, Projects)
- ❌ Cannot delete files (except in safe/temp folders)
- ❌ Cannot touch system folders (`C:\Windows`, `Program Files`)
- ❌ Cannot edit registry or network settings
- ⚠️ Requires confirmation for: closing apps, running commands, modifying files

## 🌐 Remote Access Setup

### Option 1: Same Wi-Fi (LAN)

Phone and laptop on same network - works automatically.

### Option 2: Tailscale VPN (Recommended)

1. Install [Tailscale](https://tailscale.com) on laptop and phone
2. Both devices will get IPs like `100.x.x.x`
3. Use Tailscale IP in Android app configuration
4. Works from anywhere in the world!

### Option 3: Port Forwarding (Advanced)

1. Configure router to forward port 8765 to your laptop
2. Set up DDNS for your public IP
3. Use public IP in Android app

## 💤 Wake-on-LAN

Turn on your laptop remotely from your phone!

1. **Run WoL setup**
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\setup_wol.ps1
   ```

2. **Enable in BIOS**
   - Restart → Enter BIOS (Del/F2/F12)
   - Enable "Wake on LAN" in Power Management
   - Save and exit

3. **Use from phone**
   - Tap "Turn on laptop" button in Android app
   - Laptop powers on and Item auto-starts

## 🤖 LLM Configuration

### Local Models (Ollama)

- **General**: `llama3.2:3b` (~2GB RAM)
- **Code**: `codegemma:7b` (~5GB RAM)
- **Total**: ~7GB RAM usage

### Online Models (Free Tier)

- **Primary**: Groq (`llama-3.3-70b-versatile`)
- **Fallback**: Google Gemini (`gemini-2.0-flash-exp`)

### Smart Routing

- No internet → Local
- Quick commands → Local
- Complex code/reasoning → Online (if available)
- Automatic fallback on failures

## 📱 Android App

### Building the App

```bash
cd android_app
# Follow Android Studio import instructions
# Build APK and install on phone
```

### Features

- ✅ Voice input (native Android speech recognition)
- ✅ Text input
- ✅ Real-time WebSocket connection
- ✅ Command history viewer
- ✅ Wake-on-LAN button
- ✅ Status indicator

## 🛠️ Development

### Project Structure

- `core/` - Main orchestration logic
- `llm/` - LLM integration and routing
- `voice/` - Voice input/output
- `desktop/` - Windows automation
- `api/` - REST/WebSocket server
- `permissions/` - Security layer
- `config/` - Configuration management
- `logging/` - Structured logging

### Key Components

1. **Orchestrator** - Coordinates command flow
2. **Intent Parser** - Converts voice → structured intent
3. **Action Executor** - Routes intents → desktop actions
4. **LLM Router** - Smart routing between local/online
5. **Safety Checker** - Enforces security rules

## 📊 System Requirements

### Laptop (Minimum)

- OS: Windows 10/11
- CPU: 4+ cores
- RAM: 16GB (24GB recommended)
- Storage: 20GB free space
- GPU: Optional (RTX 4060 or better for faster local LLM)

### Phone

- OS: Android 8.0+
- Internet: Wi-Fi or mobile data
- Microphone: For voice commands

## 🔧 Configuration

Key settings in `config.yaml`:

```yaml
system:
  user_name: "Shreyash"
  
security:
  auth_token: "auto-generated"
  
llm:
  routing:
    default_mode: "auto"  # auto, local, online
    
voice:
  wake_word:
    enabled: true
    word: "Item"
  stt:
    prefer_online: true
  tts:
    enabled: true
    rate: 175
```

## 🐛 Troubleshooting

### "Picovoice access key missing"

Get free key from [console.picovoice.ai](https://console.picovoice.ai) and add to `config.yaml`.

### "Ollama connection failed"

Ensure Ollama is running:
```powershell
ollama serve
```

### "Permission denied" errors

Run PowerShell as Administrator for certain operations.

### "Module not found" errors

Ensure virtual environment is activated:
```powershell
.\venv\Scripts\Activate.ps1
```

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more.

## 📜 License

This project is for personal use. API services used (Groq, Gemini, Picovoice) have their own terms of service for free tier usage.

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime
- **Groq** - Fast online LLM inference
- **Google Gemini** - Advanced AI capabilities
- **Picovoice Porcupine** - Wake word detection
- **OpenAI Whisper** - Speech recognition
- **FastAPI** - Modern Python web framework

## 📞 Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Review [API_KEYS.md](docs/API_KEYS.md) for setup
3. Check configuration in `config.yaml`

---

**Made with ❤️ for personal productivity and automation**

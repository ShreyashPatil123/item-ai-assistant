# Advanced Commands - Item AI Assistant

Complete reference for all system control and automation commands available in Item AI Assistant.

## 🔋 Power Management

### Shutdown
```
"Item, shutdown the computer"
"Item, shut down in 60 seconds"
```
- Initiates system shutdown
- 30 second default timeout (configurable)
- Confirmation prompt required

### Restart
```
"Item, restart the computer"
"Item, reboot the system"
```
- Restarts the computer
- 30 second default timeout
- Confirmation prompt required

### Sleep
```
"Item, put the computer to sleep"
"Item, sleep mode"
```
- Puts system into sleep/suspend mode
- Instant action (no timeout)

### Lock
```
"Item, lock the computer"
"Item, lock my screen"
```
- Locks the workstation immediately
- Requires password to unlock

### Logout
```
"Item, log me out"
"Item, logout"
```
- Logs out current user
- Confirmation prompt required

---

## 🔊 Volume Control

### Set Volume
```
"Item, set volume to 50"
"Item, volume 75"
"Item, set volume to maximum"
```
- Sets system volume (0-100%)
- Requires `nircmd` utility installed

### Mute/Unmute
```
"Item, mute"
"Item, unmute"
"Item, turn off sound"
```
- Mutes or unmutes system audio
- Requires `nircmd` utility

> **Note**: Volume control requires [NirCmd](https://www.nirsoft.net/utils/nircmd.html). Download and place `nircmd.exe` in Windows PATH or system32 folder.

---

## 💡 Brightness Control

### Set Brightness
```
"Item, set brightness to 50"
"Item, brightness 75"
"Item, dim the screen"
```
- Controls display brightness (0-100%)
- May not work on all systems (WMI support required)

---

## 🪟 Window Management

### Minimize Window
```
"Item, minimize this window"
"Item, minimize"
```
- Minimizes the active window

### Maximize Window
```
"Item, maximize this window"
"Item, maximize"
```
- Maximizes the active window to full screen

### Restore Window
```
"Item, restore window"
"Item, resize to normal"
```
- Restores window to normal size

### Close Window
```
"Item, close this window"
"Item, close active window"
```
- Closes the currently active window
- Safer than "close app" (doesn't force kill)

### Get Active Window
```
"Item, what window is active?"
"Item, which window is focused?"
```
- Returns information about the active window

---

## 📋 Clipboard Operations

### Copy to Clipboard
```
"Item, copy this text to clipboard: Hello World"
"Item, put this in clipboard: meeting at 3pm"
```
- Copies text to system clipboard
- Text can then be pasted anywhere

### Get Clipboard Content
```
"Item, what's in the clipboard?"
"Item, read clipboard"
```
- Retrieves and reads current clipboard content
- Useful for checking what you last copied

---

## 📁 File Operations

### Create File
```
"Item, create a file called test.txt in Documents"
"Item, make a new file notes.md in Downloads"
```
- Creates a new file
- Restricted to safe folders only
- Can optionally include initial content

### List Directory
```
"Item, list files in Documents"
"Item, show me what's in Downloads"
```
- Lists all files and folders in a directory
- Shows file sizes and modification dates
- Restricted to safe folders

### Create Directory
```
"Item, create a folder called Projects in Documents"
"Item, make a new directory"
```
- Creates a new directory
- Creates parent directories if needed

---

## 💻 System Information

### Get System Info
```
"Item, what's my system status?"
"Item, show system information"
"Item, how's my PC doing?"
```
- Shows CPU usage percentage
- Shows RAM usage (used/total GB)
- Shows disk usage percentage
- Shows battery status (if laptop)

### List Processes
```
"Item, list running processes"
"Item, what processes are running?"
```
- Shows top 20 processes by CPU usage
- Displays PID, name, CPU%, and memory%

---

## 🖱️ Desktop Automation (Existing)

### Open Application
```
"Item, open Notepad"
"Item, launch Chrome"
"Item, start Visual Studio Code"
```

### Close Application
```
"Item, close Notepad"
"Item, quit Chrome"
```

### Web Search
```
"Item, search for Python tutorials"
"Item, Google machine learning"
```

### Open URL
```
"Item, open YouTube.com"
"Item, go to reddit.com"
```

### Type Text
```
"Item, type Hello World"
```

### Take Screenshot
```
"Item, take a screenshot"
"Item, capture screen"
```

---

## 🤖 LLM Commands (Existing)

### General Query
```
"Item, what is artificial intelligence?"
"Item, explain quantum computing"
"Item, tell me a joke"
```

### Code Generation
```
"Item, generate Python code to sort a list"
"Item, write JavaScript function for factorial"
```

### Get Time
```
"Item, what time is it?"
"Item, what's the date today?"
```

---

## 📝 Command Syntax Guide

### Entity Extraction

Commands can include various entities:

- **Numbers**: "set volume to **50**" → level: 50
- **App Names**: "open **Chrome**" → app_name: "Chrome"
- **File Paths**: "create file **test.txt** in **Documents**"
- **Text Content**: "copy **this text** to clipboard"

### Confirmation Requirements

Some commands require confirmation:

- ✅ **Require Confirmation**:
  - Shutdown
  - Restart
  - Logout
  - Close app
  - Delete file

- ❌ **No Confirmation**:
  - Lock
  - Sleep
  - Volume/brightness changes
  - Open app
  - Create file

---

## 🔒 Safety Features

### Path Restrictions

File operations are restricted to **safe folders** configured in `config.yaml`:

```yaml
desktop:
  safe_folders:
    - "C:\\Users\\Shreyash\\Documents"
    - "C:\\Users\\Shreyash\\Downloads"
    - "C:\\Users\\Shreyash\\Desktop"
```

**Blocked Paths**:
- `C:\Windows\*`
- `C:\Program Files\*`
- System directories

### Permission System

- First use of any app requires permission
- Permissions stored in `config/allowed_apps.json`
- Can revoke permissions anytime

### Command Blocking

Dangerous commands are automatically blocked:
- Registry modifications
- System file deletions
- Network configuration changes
- Malicious shell commands

---

## 🛠️ Dependencies

### Required
- **Python 3.9+**
- **pyautogui** - Mouse/keyboard control
- **psutil** - System information
- **pywin32** - Windows API access
- **pyperclip** - Clipboard operations

### Optional
- **NirCmd** - Enhanced volume control
  - Download: https://www.nirsoft.net/utils/nircmd.html
  - Place in PATH or `C:\Windows\System32\`

---

## 🚀 Quick Start Examples

### Morning Routine
```
"Item, what's my system status?"
"Item, set brightness to 75"
"Item, set volume to 50"
"Item, open Chrome"
```

### Work Session
```
"Item, create a folder called ProjectX in Documents"
"Item, open Visual Studio Code"
"Item, what time is it?"
```

### End of Day
```
"Item, close all Chrome windows"
"Item, what's in my clipboard?"
"Item, lock the computer"
```

---

## 📞 Troubleshooting

### "Volume control requires nircmd"
- Download NirCmd from https://www.nirsoft.net/utils/nircmd.html
- Extract `nircmd.exe` to `C:\Windows\System32\`
- Restart Item assistant

### "Brightness control not supported"
- Some systems don't support WMI brightness control
- Try using dedicated graphics card software
- Laptops usually support this feature

### "Cannot access directory: restricted path"
- Add the directory to `safe_folders` in `config.yaml`
- Restart Item assistant
- Safety feature prevents system folder access

### "Permission denied to control app"
- Say "yes" when prompted for permission
- Check `config/allowed_apps.json`
- Reset permissions if needed

---

## 🎯 Best Practices

1. **Use specific commands**: "open Chrome" is better than "open browser"
2. **Include numbers explicitly**: "set volume to 50" not "medium volume"
3. **Specify full paths**: "Documents\\myfile.txt" instead of "myfile.txt"
4. **Check system info regularly**: Monitor CPU/RAM usage
5. **Lock before leaving**: Always lock computer when away

---

## 🔄 Updates & Improvements

The command system is continuously improved. Check for updates:

```powershell
cd item-assistant
git pull
pip install -r requirements.txt --upgrade
```

---

**Made with ❤️ for advanced PC automation**

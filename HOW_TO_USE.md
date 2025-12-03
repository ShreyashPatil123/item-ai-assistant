# How to Start and Use Item AI Assistant

## 🎯 QUICK ANSWER: Item is ALREADY RUNNING!

**Current Status**: ✅ Item has been running for 10+ minutes  
**Port 8765**: ✅ API server is active  
**No website needed**: ✅ Pure voice control system

---

## ✅ Current State (RIGHT NOW)

Item is **already running** in your terminal window. You can:
- **Start using voice immediately**: Say "Item, what time is it?"
- **No web UI required**: Item is a background service
- **API available**: Port 8765 is listening for API calls

---

## 🚀 Daily Use Guide (Copy-Paste Ready)

### Prerequisites (One-Time Setup - ALREADY DONE)
- [x] Ollama installed and models downloaded
- [x] Python 3.9+ with virtual environment
- [x] All API keys configured
- [x] Dependencies installed

---

### Starting Item (For Future Reference)

#### Option 1: Quick Launcher (Recommended)
```batch
:: Double-click this file or run in terminal:
C:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant\start_item.bat
```

#### Option 2: Manual Command (Full Control)
```powershell
# Step 1: Navigate to project
cd C:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant

# Step 2: Activate virtual environment
.\venv\Scripts\Activate.ps1

# Step 3: Start Item
python -m item_assistant.main
```

**What you'll see when it starts**:
```
✓ Loaded configuration from: C:\Users\Shreyash\OneDrive\Desktop\...
✓ Ensured directories exist
[2025-12-03 XX:XX:XX] [INFO] Item AI Assistant - Logging System Initialized
[2025-12-03 XX:XX:XX] [INFO] System controller initialized
[2025-12-03 XX:XX:XX] [INFO] Started listening for wake word
[2025-12-03 XX:XX:XX] [INFO] API server listening on 0.0.0.0:8765
```

---

### Confirming Item is Running

#### Method 1: Check Console Output
Look for these messages:
- ✅ "API server listening on 0.0.0.0:8765"
- ✅ "Started listening for wake word"
- ✅ "voice.ai is online and ready"

#### Method 2: Check Port 8765
```powershell
netstat -ano | findstr ":8765"
# Should show: TCP    0.0.0.0:8765    0.0.0.0:0    LISTENING
```

#### Method 3: API Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8765/health" -Method GET
# Should return: {"status": "healthy", ...}
```

#### Method 4: Check Logs
```powershell
Get-Content "C:\Users\Shreyash\ItemAssistant\logs\*" -Tail 20
# Should show recent activity
```

---

### Prerequisites Before Starting Item

#### 1. Start Ollama (Required for Local LLM)

**Check if Ollama is running**:
```powershell
ollama list
# Should show models: llama3.2:3b, codegemma:7b
```

**Start Ollama if not running**:
```powershell
# Open a separate PowerShell window
ollama serve
# Leave this running in background
```

#### 2. Verify Microphone (For Voice Control)

**Check Windows microphone permissions**:
1. Open: Settings → Privacy → Microphone
2. Ensure: "Allow apps to access your microphone" is ON
3. Test: Speak and see if microphone icon shows activity

---

## 🌐 Web UI: NOT REQUIRED

### Understanding Item's Architecture

**Item is a PURE VOICE/API ASSISTANT**:
- ❌ No web dashboard required
- ❌ No browser UI needed
- ✅ Works entirely via voice commands
- ✅ API available on port 8765 (for automation/phone app)

### What Port 8765 is For

Port 8765 is for:
- **API calls** from Android app (when built)
- **Programmatic control** (scripts, automation)
- **Health checks** (monitoring)
- **NOT** for a web browser UI

### Optional: API Testing (Not Daily Use)

If you want to test the API (optional):
```powershell
$token = "ia9dz57KRh3CjQPyN9R7gNRVwkHKBRJ1h73g4rXA7jQ"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}
$body = @{
    command = "what time is it"
    source = "api"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8765/api/command" `
    -Method POST -Headers $headers -Body $body
```

**But for daily use**: Just use your voice!

---

## 🎤 How to Use Item (Voice Control)

### Step-by-Step First Use

**1. Ensure Item is Running**
   - Check terminal shows "listening for wake word"

**2. Ensure Mic is Working**
   - Speak and check Windows detects audio
   - Minimize background noise

**3. Say Wake Word Clearly**
   ```
   Say: "Item"
   ```
   - Speak clearly, normal volume
   - Wait 1-2 seconds for detection

**4. Give Your Command**
   ```
   Say: "What time is it?"
   ```
   - Speak naturally
   - Wait for response

**5. Wait for Response**
   - Item processes speech
   - Executes command
   - Responds (via TTS if enabled)

---

### Testing Commands (Try These Now!)

#### ✅ Test 1: Time Query
```
Say: "Item, what time is it?"
Expected: Responds with current time
```

#### ✅ Test 2: System Lock
```
Say: "Item, lock my computer"
Expected: Windows locks immediately
```

#### ✅ Test 3: Open Application
```
Say: "Item, open Notepad"
Expected: Notepad launches
```

#### ✅ Test 4: System Info
```
Say: "Item, get system info"
Expected: Responds with CPU, RAM, disk usage
```

#### ✅ Test 5: LLM Query
```
Say: "Item, tell me a joke"
Expected: Groq/Gemini generates and responds with joke
```

---

## 📋 Minimal Daily Use Checklist

### Every Time You Use Item:

```
1. [Optional] Start Ollama
   powershell: ollama serve
   (Only if you want local LLM; online works without it)

2. Start Item
   Double-click: start_item.bat
   OR
   powershell: cd C:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant
               .\venv\Scripts\Activate.ps1
               python -m item_assistant.main

3. Wait for "listening for wake word" message

4. Start using voice:
   - Say: "Item"
   - Then: "What time is it?"

5. Done! Keep using voice commands
```

### That's It! No Website Required!

---

## 🛑 How to Stop Item

### Method 1: Keyboard (Recommended)
```
In the terminal running Item:
Press: Ctrl + C
```

### Method 2: Close Terminal
```
Click the X on the terminal window
Item will shut down gracefully
```

### Method 3: Kill Process (If Frozen)
```powershell
# Find Item process
Get-Process python | Where-Object {$_.Id -eq (Get-NetTCPConnection -LocalPort 8765).OwningProcess}

# Kill it
Stop-Process -Id <PID_FROM_ABOVE>
```

---

## 🔧 Troubleshooting

### "No wake word detected"

**Check**:
1. Microphone is enabled in Windows
2. Speak louder/clearer
3. Check logs for "wake word detected" events
4. Verify Picovoice key in config.yaml

**Test mic**:
```powershell
# Windows: Open Sound Settings → Test microphone
```

### "Command not understood"

**Solutions**:
1. Speak more clearly
2. Pause after "Item" before command
3. Check logs for speech recognition output
4. Try simpler commands first

### "Ollama connection failed"

**Fix**:
```powershell
# Start Ollama in separate window
ollama serve
```

### "API server timeout"

**Check**:
```powershell
# Verify port 8765 is listening
netstat -ano | findstr ":8765"

# If not, restart Item
```

---

## 📊 Complete Startup Sequence (Explicit Commands)

### From Scratch (Cold Start)

```powershell
# Terminal 1: Start Ollama (Optional - for local LLM)
ollama serve
# Leave this running

# Terminal 2: Start Item
cd C:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant
.\venv\Scripts\Activate.ps1
python -m item_assistant.main
# Leave this running

# You: Use your voice
# Say: "Item, what time is it?"
```

### What You'll See (Expected Output)

**Terminal 1 (Ollama)**:
```
Ollama is running
```

**Terminal 2 (Item)**:
```
✓ Loaded configuration
✓ System controller initialized
✓ File manager initialized
✓ Voice system online
[INFO] API server listening on 0.0.0.0:8765
[INFO] Started listening for wake word
```

**Your Voice**:
```
You: "Item"
[Item detects wake word]
You: "What time is it?"
Item: "It's 5:15 PM on December 3rd, 2025"
```

---

## 🎯 Summary: Website Required?

### NO WEBSITE REQUIRED! ❌

**Item AI Assistant is**:
- ✅ Background service
- ✅ Voice-controlled
- ✅ API-accessible (port 8765)
- ❌ NOT a web dashboard
- ❌ NOT browser-based

**When you might use the API** (port 8765):
- From Android app (when built)
- From automation scripts
- For health monitoring
- NOT for daily interaction

**Daily use is 100% voice**:
- Say: "Item"
- Then: Your command
- Done!

---

## 🚀 YOU'RE READY NOW!

**Item is ALREADY RUNNING** in your terminal.

### Try it RIGHT NOW:

1. **Say**: "Item"
2. **Wait**: 1 second
3. **Say**: "What time is it?"
4. **Listen**: Item responds!

No website. No setup. Just talk! 🎤

---

## 📞 Quick Reference

| Action | Command |
|--------|---------|
| **Start Item** | `start_item.bat` or `python -m item_assistant.main` |
| **Stop Item** | `Ctrl + C` in terminal |
| **Check Status** | `netstat -ano \| findstr ":8765"` |
| **View Logs** | `Get-Content C:\Users\Shreyash\ItemAssistant\logs\* -Tail 50` |
| **Test Voice** | Say "Item, what time is it?" |
| **Start Ollama** | `ollama serve` (separate terminal) |

---

**That's it! Item is running. Start talking now!** 🎉

# Troubleshooting Guide - Item AI Assistant

Common issues and their solutions.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Issues](#configuration-issues)
3. [Voice Issues](#voice-issues)
4. [LLM Issues](#llm-issues)
5. [Network & API Issues](#network--api-issues)
6. [Desktop Automation Issues](#desktop-automation-issues)
7. [Performance Issues](#performance-issues)
8. [Error Messages](#error-messages)

---

## Installation Issues

### "Python not found"

**Symptom**: `python: command not found` or `python is not recognized`

**Solution**:
1. Reinstall Python from [python.org](https://python.org)
2. **Check** "Add Python to PATH" during installation
3. Restart PowerShell
4. Verify: `python --version`

### "pip install fails"

**Symptom**: Errors during `pip install -r requirements.txt`

**Solutions**:
1. **Upgrade pip**: `python -m pip install --upgrade pip`
2. **Use system Python** (not Microsoft Store version)
3. **Check internet connection**
4. **Install Visual C++** build tools if needed (for some packages)

### "Virtual environment not activating"

**Symptom**: `.\venv\Scripts\Activate.ps1` fails

**Solution**:
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.\venv\Scripts\Activate.ps1
```

---

## Configuration Issues

### "Config file not found"

**Symptom**: `FileNotFoundError: config.yaml`

**Solution**:
```powershell
# Copy template
Copy-Item item_assistant\config\config.template.yaml `
          item_assistant\config\config.yaml
```

### "YAML parsing error"

**Symptom**: `yaml.scanner.ScannerError`

**Solution**:
- Check YAML syntax (proper indentation, no tabs)
- Quotes around values with special characters
- Use online YAML validator
- Example of correct format:
  ```yaml
  voice:
    wake_word:
      enabled: true  # Note: Space after colon
  ```

### "Invalid API key"

**Symptom**: `401 Unauthorized` or `Invalid API key`

**Solutions**:
1. **Verify key format**:
   - Groq: Starts with `gsk_`
   - Gemini: Starts with `AIza`
2. **Check for spaces**: Remove any leading/trailing spaces
3. **Re-copy key** from source
4. **Regenerate key** if still failing

---

## Voice Issues

### Wake word not detected

**Symptoms**:
- No response when saying "Item"
- No confirmation beep/sound

**Solutions**:

1. **Check Picovoice key**:
   ```yaml
   voice:
     wake_word:
       access_key: "YOUR_KEY"  # Must be set
   ```

2. **Adjust sensitivity**:
   ```yaml
   voice:
     wake_word:
       sensitivity: 0.7  # Try 0.5 to 0.9
   ```

3. **Check microphone**:
   - Windows Settings → Privacy → Microphone
   - Allow Python/app to access microphone

4. **Use built-in keyword temporarily**:
   Say "porcupine" instead of "Item" for testing

5. **Train custom keyword**:
   - Go to [console.picovoice.ai](https://console.picovoice.ai)
   - Train "Item" wake word
   - Download `.ppn` file

### STT (Speech-to-Text) not working

**Symptoms**:
- Wake word detected but command not transcribed
- "Failed to transcribe" error

**Solutions**:

1. **Check microphone input**:
   ```powershell
   # Test mic in Windows Sound settings
   ```

2. **Try offline-only**:
   ```yaml
   voice:
     stt:
       prefer_online: false
   ```

3. **Install/reinstall Whisper**:
   ```powershell
   pip install --upgrade openai-whisper
   ```

4. **Check audio devices**:
   ```python
   import sounddevice as sd
   print(sd.query_devices())
   ```

### TTS (Text-to-Speech) not working

**Symptoms**:
- Item receives command but doesn't speak response

**Solutions**:

1. **Check TTS enabled**:
   ```yaml
   voice:
     tts:
       enabled: true
   ```

2. **Test TTS manually**:
   ```python
   from item_assistant.voice import get_tts
   tts = get_tts()
   tts.speak("Test")
   ```

3. **List available voices**:
   ```python
   from item_assistant.voice import get_tts
   tts = get_tts()
   print(tts.list_voices())
   ```

4. **Change voice**:
   ```yaml
   voice:
     tts:
       voice_id: 1  # Try different IDs from list_voices()
   ```

---

## LLM Issues

### Ollama connection failed

**Symptoms**:
- "Connection refused" to `localhost:11434`
- Local LLM not available

**Solutions**:

1. **Check Ollama is running**:
   ```powershell
   ollama serve
   ```

2. **Verify models are pulled**:
   ```powershell
   ollama list
   # Should show: llama3.2:3b, codegemma:7b
   ```

3. **Pull models if missing**:
   ```powershell
   ollama pull llama3.2:3b
   ollama pull codegemma:7b
   ```

4. **Check port**:
   ```powershell
   netstat -an | findstr "11434"
   # Should show LISTENING
   ```

### Groq API errors

**Symptoms**:
- "Rate limit exceeded"
- "Invalid API key"

**Solutions**:

1. **Check API key**: Verify at [console.groq.com](https://console.groq.com)

2. **Rate limits**:
   - Free tier: 14,400 requests/day, 30/minute
   - Wait or use Gemini fallback

3. **Enable fallback**:
   ```yaml
   llm:
     online:
       fallback: "gemini"
   ```

### Gemini API errors

**Solutions**:

1. **Verify API key**: Check at [ai.google.dev](https://ai.google.dev)

2. **Enable API**: Ensure Gemini API is enabled in Google Cloud Console

3. **Quota limits**:
   - Free tier: 60 requests/min
   - Item will auto-fallback to local

### Slow LLM response

**Solutions**:

1. **Use GPU** for local LLM:
   - Ensure CUDA installed for NVIDIA GPU
   - Ollama auto-detects GPU

2. **Use smaller model**:
   ```powershell
   ollama pull llama3.2:1b  # Smaller, faster
   ```

3. **Prefer online for complex tasks**:
   ```yaml
   llm:
     routing:
       default_mode: "online"
   ```

---

## Network & API Issues

### API server won't start

**Symptoms**:
- "Address already in use" error
- Port 8765 taken

**Solutions**:

1. **Find what's using port**:
   ```powershell
   netstat -ano | findstr "8765"
   ```

2. **Kill process**:
   ```powershell
   taskkill /PID <PID> /F
   ```

3. **Use different port**:
   ```yaml
   network:
     api_port: 8766  # Change port
   ```

### Phone can't connect to laptop

**Symptoms**:
- Android app shows "Connection failed"
- API unreachable

**Solutions**:

1. **Verify same network**: Phone and laptop on same Wi-Fi

2. **Check laptop IP**:
   ```powershell
   ipconfig
   # Use IPv4 Address in Android app
   ```

3. **Test connectivity**:
   ```powershell
   # From phone browser
   http://laptop-ip:8765/health
   ```

4. **Check firewall**:
   ```powershell
   # Add firewall rule
   New-NetFirewallRule -DisplayName "Item API" `
     -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow
   ```

5. **Try Tailscale** instead:
   - Install on both devices
   - Use Tailscale IP (100.x.x.x)

### "Unauthorized" errors from API

**Symptom**: `401 Unauthorized`

**Solutions**:

1. **Check auth token**:
   - In `config.yaml`: `security.auth_token`
   - In Android app: Must match exactly

2. **Regenerate token**:
   ```yaml
   security:
     auth_token: ""  # Leave empty, will auto-generate on next start
   ```

---

## Desktop Automation Issues

### "Permission denied" to control apps

**Symptom**: App operations fail with permission errors

**Solutions**:

1. **Grant permission** when prompted

2. **Manually add to allowed list**:
   Edit `config/allowed_apps.json`:
   ```json
   {
     "chrome": true,
     "notepad": true
   }
   ```

3. **Check auto-approved list**:
   ```yaml
   permissions:
     auto_approved_apps:
       - "notepad"
       - "calculator"
   ```

### Apps won't open

**Solutions**:

1. **Check app name**: Use common names like `chrome`, `notepad`

2. **Use full path** in config if needed

3. **Test manually**:
   ```python
   from item_assistant.desktop import get_app_controller
   app = get_app_controller()
   result = app.open_app("notepad")
   print(result)
   ```

### Browser automation fails

**Symptoms**:
- Chrome won't open
- Selenium errors

**Solutions**:

1. **Install ChromeDriver** (automatic via webdriver-manager)

2. **Update browser**:
   - Chrome, Edge, or Firefox to latest version

3. **Specify browser**:
   ```yaml
   desktop:
     browser:
       default: "edge"  # Try different browser
   ```

---

## Performance Issues

### High RAM usage

**Symptoms**:
- System slow
- >10GB RAM used by Python

**Solutions**:

1. **Use smaller LLM models**:
   ```powershell
   ollama pull llama3.2:1b  # ~1.5GB instead of 3B
   ```

2. **Disable local LLM**:
   ```yaml
   llm:
     local:
       enabled: false
     routing:
       default_mode: "online"
   ```

3. **Close other apps** while using Item

### High CPU usage

**Solutions**:

1. **Lower wake word sensitivity**

2. **Increase STT recording duration**:
   ```yaml
   voice:
     stt:
       recording_duration: 3  # Shorter recordings
   ```

3. **Use CPU-only mode**:
   ```yaml
   resources:
     gpu_monitoring:
       enabled: false
   ```

---

## Error Messages

### "Module 'pvporcupine' not found"

**Solution**:
```powershell
pip install pvporcupine
```

### "Microsoft Visual C++ 14.0 required"

**Solution**:
Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### "PermissionError: [WinError 5] Access is denied"

**Solution**:
Run PowerShell as Administrator

### "CUDA not available"

**Note**: This is normal if you don't have NVIDIA GPU. Ollama will use CPU.

**For GPU users**:
1. Install [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
2. Restart Ollama

---

## Still Having Issues?

1. **Check logs**:
   ```powershell
   # View today's logs
   Get-Content C:\Users\Shreyash\ItemAssistant\logs\$(Get-Date -Format "yyyy-MM-dd").log -Tail 50
   ```

2. **Enable debug logging**:
   ```yaml
   logging:
     level: "DEBUG"
   ```

3. **Test individual components**:
   ```python
   # Test config
   from item_assistant.config import get_config
   print(get_config().get_all())
   
   # Test LLM
   from item_assistant.llm import get_llm_router
   router = get_llm_router()
   result = router.generate("Hello")
   print(result)
   ```

4. **Reinstall dependencies**:
   ```powershell
   pip install -r requirements.txt --force-reinstall
   ```

---

**For additional help, check the main [README.md](../README.md) and [SETUP.md](SETUP.md)**

# Run Item AI Assistant with Desktop UI

## Quick Start

### Prerequisites

Ensure you have:
- Python 3.8+
- All dependencies installed: `pip install -r requirements.txt`
- Picovoice API key configured
- Groq API key configured (optional but recommended)
- Windows 10/11

### Step 1: Verify Configuration

Check `item_assistant/config/config.yaml`:

```yaml
# Make sure these are set:
voice:
  wake_word:
    access_key: "YOUR_PICOVOICE_KEY"  # Required for wake word

llm:
  online:
    groq:
      api_key: "YOUR_GROQ_KEY"         # Required for STT

ui:
  enable_slideup_panel: true            # Enable the UI panel
  idle_hide_timeout_seconds: 5          # Auto-hide after 5 seconds
```

### Step 2: Run the Assistant

```bash
# Navigate to project directory
cd c:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant

# Run the assistant
python -m item_assistant.main
```

### Step 3: Wait for Startup

You should see:

```
================================================================================
✅ Item AI Assistant is now running
🎤 Say wake word (porcupine/picovoice/bumblebee) + command
⚡ Optimized: 3s recording, synchronous transcription, Groq STT
🎨 Desktop UI panel enabled
🛑 Press Ctrl+C to stop
================================================================================
```

### Step 4: Use the Panel

The panel will appear at the bottom of your screen when:

1. **Wake word detected** - Say "porcupine", "picovoice", or "bumblebee"
   - Panel shows: "Listening" (green)
   - Speak your command

2. **Mic button clicked** - Click the 🎤 button on the panel
   - Panel shows: "Listening" (green)
   - Speak your command

3. **Processing** - While assistant thinks
   - Panel shows: "Thinking" (orange)
   - Displays your command

4. **Response** - While assistant speaks
   - Panel shows: "Speaking" (blue)
   - Displays the response

5. **Idle** - After response
   - Panel shows: "Idle" (gray)
   - Auto-hides after 5 seconds

---

## Testing the UI

### Test 1: Wake Word Detection

```
1. Wait for "Idle" state (gray)
2. Say: "porcupine, what time is it?"
3. Panel should slide up and show:
   - Status: "Listening" (green)
   - User text: "what time is it?"
   - Status: "Thinking" (orange)
   - Assistant response appears
   - Status: "Speaking" (blue)
   - Panel auto-hides after 5 seconds
```

### Test 2: Mic Button Click

```
1. Wait for panel to hide
2. Move mouse to bottom of screen (panel should appear)
3. Click the 🎤 button
4. Panel should show "Listening" (green)
5. Speak a command: "turn on the lights"
6. Panel processes and responds
7. Panel auto-hides
```

### Test 3: Multiple Commands

```
1. Say wake word + command
2. Wait for response
3. Say wake word + another command
4. Verify panel updates correctly
5. Repeat 5+ times to ensure stability
```

### Test 4: UI Fallback

```
1. Disable UI in config:
   ui:
     enable_slideup_panel: false

2. Run assistant
3. Should start without UI
4. Voice commands should still work
5. No panel should appear
```

---

## Customization

### Change Auto-Hide Timeout

Edit `item_assistant/config/config.yaml`:

```yaml
ui:
  idle_hide_timeout_seconds: 10  # Hide after 10 seconds instead of 5
```

### Disable Auto-Hide

```yaml
ui:
  idle_hide_timeout_seconds: 0  # Never auto-hide
```

### Change Panel Colors

Edit `item_assistant/ui/panel.py` - find `COLORS` dictionary:

```python
COLORS = {
    "bg": "#1e1e1e",              # Background color
    "fg": "#ffffff",              # Text color
    "idle": "#666666",            # Idle state color
    "listening": "#00ff00",       # Listening state color
    "thinking": "#ffaa00",        # Thinking state color
    "speaking": "#0099ff",        # Speaking state color
    "button_bg": "#333333",       # Button background
    "button_hover": "#444444",    # Button hover color
}
```

Change any hex color to your preference. Examples:
- `#ff0000` = Red
- `#00ff00` = Green
- `#0000ff` = Blue
- `#ffff00` = Yellow
- `#ff00ff` = Magenta
- `#00ffff` = Cyan

### Change Animation Speed

Edit `item_assistant/ui/panel.py` - find `SlideUpPanel` class:

```python
ANIMATION_SPEED = 20      # ms per frame (lower = faster)
ANIMATION_STEP = 15       # pixels per frame (higher = faster)
```

Examples:
- Slower: `ANIMATION_SPEED = 40, ANIMATION_STEP = 8`
- Faster: `ANIMATION_SPEED = 10, ANIMATION_STEP = 25`

### Change Panel Size

Edit `item_assistant/ui/panel.py` - find `SlideUpPanel` class:

```python
PANEL_WIDTH = 1200   # Width in pixels
PANEL_HEIGHT = 140   # Height in pixels
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'tkinter'"

Tkinter is usually included with Python. If missing:

```bash
# Windows - reinstall Python with Tkinter
# Or install via pip:
pip install tk
```

### Panel doesn't appear

1. Check if enabled in config:
   ```yaml
   ui:
     enable_slideup_panel: true
   ```

2. Check logs for errors:
   ```
   tail -f logs/item_assistant.log | grep -i "ui\|panel"
   ```

3. Try disabling and re-enabling:
   ```yaml
   ui:
     enable_slideup_panel: false
   ```
   Then set back to `true`

### Panel appears but doesn't update

1. Verify wake word is working:
   - Say wake word
   - Check if "Listening" appears in logs

2. Check if STT is working:
   - Speak a command
   - Check if command appears in logs

3. Restart assistant:
   ```bash
   # Press Ctrl+C to stop
   # Run again
   python -m item_assistant.main
   ```

### Mic button doesn't work

1. Verify Picovoice key is set
2. Check microphone permissions
3. Test microphone:
   ```bash
   python -c "import sounddevice; print(sounddevice.query_devices())"
   ```

### Panel animation is jerky

1. Close other applications to free CPU
2. Increase animation speed:
   ```python
   ANIMATION_SPEED = 10  # Lower = faster
   ANIMATION_STEP = 25   # Higher = faster
   ```

### Assistant works but UI crashes

1. Disable UI:
   ```yaml
   ui:
     enable_slideup_panel: false
   ```

2. Check error logs:
   ```
   grep -i "error\|exception" logs/item_assistant.log | tail -20
   ```

3. Update tkinter:
   ```bash
   pip install --upgrade tk
   ```

---

## Performance Tips

### Optimize for Low-End Systems

```yaml
ui:
  enable_slideup_panel: true
  idle_hide_timeout_seconds: 3      # Hide faster
  animation_speed_ms: 40            # Slower animation
  animation_step_px: 8              # Smaller steps
```

### Optimize for High-End Systems

```yaml
ui:
  enable_slideup_panel: true
  idle_hide_timeout_seconds: 10     # Hide slower
  animation_speed_ms: 10            # Faster animation
  animation_step_px: 25             # Larger steps
```

---

## Advanced Usage

### Run Without UI (Headless)

```bash
# Edit config.yaml
ui:
  enable_slideup_panel: false

# Run
python -m item_assistant.main
```

### Run with Custom Config

```bash
# Create custom config
cp item_assistant/config/config.template.yaml custom_config.yaml

# Edit custom_config.yaml as needed

# Run with custom config (if supported)
python -m item_assistant.main --config custom_config.yaml
```

### Monitor Logs in Real-Time

```bash
# Windows PowerShell
Get-Content logs/item_assistant.log -Wait

# Or use tail if available
tail -f logs/item_assistant.log
```

### Debug UI Issues

Add this to `item_assistant/ui/panel.py` for extra logging:

```python
# In _on_state_change method, add:
logger.debug(f"UI State Change: {state.value}, User: {user_text}, Assistant: {assistant_text}")
```

---

## Common Commands to Test

Once the assistant is running, try these commands:

```
"porcupine, what time is it?"
"porcupine, open notepad"
"porcupine, turn on the lights"
"porcupine, what's the weather?"
"porcupine, play music"
"porcupine, close this window"
```

---

## Keyboard Shortcuts

While the assistant is running:

- **Ctrl+C** - Stop the assistant
- **Click mic button** - Start listening manually
- **Move mouse to bottom** - Panel appears (if hidden)

---

## Next Steps

After getting the UI working:

1. **Customize colors** - Match your theme
2. **Adjust timeout** - Set auto-hide to your preference
3. **Test commands** - Try various voice commands
4. **Integrate with automations** - Use assistant to control apps
5. **Share feedback** - Report issues or suggestions

---

## Support

For issues:

1. Check logs: `logs/item_assistant.log`
2. Review `DESKTOP_UI_GUIDE.md` for detailed documentation
3. Check GitHub issues: https://github.com/ShreyashPatil123/item-ai-assistant/issues
4. Create new issue with logs and steps to reproduce

---

**Happy using! 🎉**

For more details, see `DESKTOP_UI_GUIDE.md`

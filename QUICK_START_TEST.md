# Quick Start Test - Wake Word Loop Fix

## 30-Second Test

### Step 1: Start Item
```bash
cd c:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant
python -m item_assistant.main
```

Wait for:
```
✅ Item AI Assistant is now running
🎤 Say wake word (porcupine/picovoice/bumblebee) + command
```

### Step 2: Say 5 Commands in a Row

Say each of these (with 2-second pause between each):

1. **"porcupine, what time is it?"**
2. **"porcupine, lock computer"**
3. **"porcupine, open notepad"**
4. **"porcupine, what's the weather?"**
5. **"porcupine, play music"**

### Step 3: Check Results

✅ **SUCCESS**: All 5 commands work without restarting
❌ **FAILURE**: Any command after the first doesn't work

---

## Expected Log Output

For each command, you should see:

```
🎯 WAKE DETECTED: 'porcupine' (frame #XXXX)
🎯 Wake word detected! Listening for command...
🎤 Recording (3s)...
✅ Recording done
⚡ Groq STT: '[your command]'
📝 Heard command: [your command]
Processing command from laptop: [your command]
[... command execution ...]
Response: [response]
✅ READY FOR NEXT WAKE WORD
```

Then immediately (within 1-2 seconds):

```
🎯 WAKE DETECTED: 'porcupine' (frame #YYYY)
🎯 Wake word detected! Listening for command...
[... repeat ...]
```

---

## What to Look For

### ✅ Good Signs
- Frame count keeps increasing (e.g., frame #100, #200, #300, etc.)
- "READY FOR NEXT WAKE WORD" appears after each command
- Each wake word is detected immediately after the previous command finishes
- No "IGNORED: Still processing" messages

### ❌ Bad Signs
- Frame count stops increasing after first command
- "READY FOR NEXT WAKE WORD" doesn't appear
- Second wake word is not detected
- "IGNORED: Still processing" appears for second command
- Audio stream closes unexpectedly

---

## Troubleshooting

### Issue: Second wake word not detected

**Check 1**: Is the flag being reset?
```
Look for: ✅ READY FOR NEXT WAKE WORD
```
If missing, the finally block isn't running.

**Check 2**: Is the audio loop still running?
```
Look for: 🎤 Audio frame processed (frame #XXXX)
```
If frame count stops, the audio loop exited.

**Check 3**: Is there an exception?
```
Look for: Error processing wake word
```
Check the full error message.

### Issue: Transcription hangs

**Check**: Timeout should trigger after 30 seconds
```
Look for: ⏱️  Transcription timed out after 30s
```

### Issue: TTS is blocking

**Check**: All TTS calls should use wait=False
```
grep "self.tts.speak" item_assistant/main.py
```
Should see: `self.tts.speak(..., wait=False)`

---

## Files to Check

If test fails, verify these files were modified:

### 1. item_assistant/main.py
- Line 41-56: `on_wake_word_detected()` should return immediately
- Line 58-86: `_handle_command_async()` should exist
- Line 64, 77, 81: All TTS calls should have `wait=False`

### 2. item_assistant/voice/stt.py
- Line 7: `import threading` should be present
- Line 191-223: `listen_and_transcribe()` should have timeout logic

### 3. item_assistant/voice/wake_word.py
- Line 93: `frame_count = 0` should be present
- Line 105-107: Frame logging should be present

---

## Performance Expectations

- **Wake word detection**: Instant
- **Recording**: 3 seconds
- **Transcription**: 1-2 seconds (Groq) or 5-10 seconds (Whisper)
- **Command processing**: 1-5 seconds
- **Total latency**: 5-10 seconds per command
- **Audio loop**: Continuous, never stops

---

## Success Criteria

- [ ] Item starts without errors
- [ ] First command works
- [ ] Second command works (without restart)
- [ ] Third command works
- [ ] Fourth command works
- [ ] Fifth command works
- [ ] Logs show clean state transitions
- [ ] No "IGNORED" messages appear
- [ ] Frame count keeps increasing

---

## Next Steps

If test passes:
- ✅ The fix is working correctly
- ✅ You can use Item normally
- ✅ No restart required between commands

If test fails:
- ❌ Check the troubleshooting section
- ❌ Verify all 3 files were modified correctly
- ❌ Look for exceptions in the logs
- ❌ Refer to WAKE_WORD_BUG_FIX.md for detailed analysis

---

## Additional Resources

- **WAKE_WORD_BUG_FIX.md** - Detailed technical analysis
- **TEST_WAKE_WORD_LOOP.md** - Comprehensive test procedure
- **ARCHITECTURE_BEFORE_AFTER.md** - Visual comparison of the fix
- **FIX_SUMMARY.md** - Quick reference guide


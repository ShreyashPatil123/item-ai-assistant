# Wake Word Loop Bug Fix - Test Plan

## Summary of Fixes Applied

### 1. **Callback Thread Separation** (main.py)
- **Before**: `on_wake_word_detected()` directly called `asyncio.run()`, blocking the callback thread
- **After**: 
  - `on_wake_word_detected()` now just sets the flag and starts a new thread (returns immediately)
  - `_handle_command_async()` runs in a separate thread and does all the heavy lifting
  - The callback thread returns instantly, allowing the audio loop to continue processing frames

### 2. **Non-Blocking TTS** (main.py + tts.py)
- **Before**: TTS calls used `wait=True` (default), blocking until speech finishes
- **After**: All TTS calls now use `wait=False` for non-blocking speech
- This prevents the command thread from blocking while speaking

### 3. **Timeout Protection** (stt.py)
- **Before**: `listen_and_transcribe()` could hang indefinitely if Groq/Whisper failed
- **After**: Added 30-second timeout with thread-based implementation
- If transcription takes too long, the flag is reset and the system returns to listening

### 4. **Enhanced Logging** (wake_word.py + main.py)
- Added frame counting to verify continuous audio processing
- Added state transition logs: "WAKE DETECTED" → "READY FOR NEXT WAKE WORD"
- Logs show when wake words are ignored due to overlap prevention

---

## State Machine Flow (Fixed)

```
LISTENING (is_listening=True, processing_command=False)
    ↓
[Audio frames processed continuously]
    ↓
WAKE WORD DETECTED (keyword_index >= 0)
    ↓
on_wake_word_detected() called (returns immediately)
    ├─ Sets processing_command = True
    └─ Starts _handle_command_async() thread
    ↓
[Audio loop continues processing frames]
    ↓
_handle_command_async() runs in separate thread:
    ├─ Speaks "Yes?" (non-blocking)
    ├─ Records audio (3 seconds)
    ├─ Transcribes (Groq or Whisper)
    ├─ Processes command (asyncio.run)
    ├─ Speaks response (non-blocking)
    └─ Sets processing_command = False (finally block)
    ↓
READY FOR NEXT WAKE WORD (processing_command=False)
    ↓
[Audio loop continues listening]
    ↓
REPEAT: Next wake word detected...
```

---

## Test Procedure

### Prerequisites
1. Item assistant is running in debug mode
2. Porcupine wake words are configured: `porcupine`, `picovoice`, or `bumblebee`
3. Microphone is working
4. Logs are visible in the console

### Test Steps

**Step 1: Start Item in Debug Mode**
```bash
cd c:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant
python -m item_assistant.main
```

Wait for the greeting and the message:
```
✅ Item AI Assistant is now running
🎤 Say wake word (porcupine/picovoice/bumblebee) + command
```

**Step 2: Perform 5 Sequential Wake-Word Activations**

For each activation:
1. Say the wake word (e.g., "porcupine")
2. Wait for "Yes?" response
3. Say a command (e.g., "what time is it", "lock computer", "open notepad")
4. Wait for the response
5. Wait ~2 seconds before the next activation

Repeat 5 times in a row **without restarting the assistant**.

### Expected Log Output

For each activation, you should see this sequence:

```
🎯 WAKE DETECTED: 'porcupine' (frame #XXXX)
🎯 Wake word detected! Listening for command...
🎤 Recording (3s)...
✅ Recording done
⚡ Groq STT: 'what time is it'
📝 Heard command: what time is it
Processing command from laptop: what time is it
[... command execution ...]
Response: [time response]
✅ READY FOR NEXT WAKE WORD
```

Then immediately after (within 1-2 seconds):

```
🎯 WAKE DETECTED: 'porcupine' (frame #YYYY)
🎯 Wake word detected! Listening for command...
[... repeat ...]
```

### Success Criteria

✅ **All 5 activations work without restarting**
- First activation works
- Second activation works
- Third activation works
- Fourth activation works
- Fifth activation works

✅ **Logs show continuous audio processing**
- Frame count increases continuously (every 100 frames logged)
- No "Audio stream closed" or "Stopped listening" between activations

✅ **No "IGNORED: Still processing" messages**
- If you see this, the flag wasn't reset properly

✅ **State transitions are clean**
- Each activation shows: WAKE DETECTED → READY FOR NEXT WAKE WORD
- No gaps or errors in between

---

## Debugging If Test Fails

### Symptom: Second wake word is ignored

**Check 1: Is the flag being reset?**
```
Look for: ✅ READY FOR NEXT WAKE WORD
```
If you don't see this after the first command, the finally block isn't running.

**Check 2: Is the audio loop still running?**
```
Look for: 🎤 Audio frame processed (frame #XXXX)
```
If frame count stops after first activation, the audio loop exited.

**Check 3: Is the callback thread blocking?**
```
Look for: 🎯 WAKE DETECTED - Starting command handler thread
```
If this appears but "Recording" doesn't start immediately, the thread isn't running.

### Symptom: Transcription hangs

**Check**: Timeout should trigger after 30 seconds
```
Look for: ⏱️  Transcription timed out after 30s
```
If you don't see this, the timeout isn't working.

### Symptom: TTS is blocking

**Check**: All TTS calls should use `wait=False`
```
Grep for: self.tts.speak(..., wait=False)
```
If any call uses `wait=True`, it will block the command thread.

---

## Files Modified

1. **item_assistant/main.py**
   - Separated `on_wake_word_detected()` into quick callback + `_handle_command_async()` worker
   - Changed all TTS calls to `wait=False`
   - Added detailed logging

2. **item_assistant/voice/stt.py**
   - Added timeout wrapper to `listen_and_transcribe()`
   - Prevents infinite blocking if transcription hangs

3. **item_assistant/voice/wake_word.py**
   - Enhanced logging with frame counting
   - Verifies continuous audio processing

---

## Expected Behavior After Fix

The assistant should now:
1. ✅ Detect the first wake word and process the command
2. ✅ Detect the second wake word without restarting
3. ✅ Detect the third, fourth, fifth wake words in sequence
4. ✅ Handle errors gracefully without breaking the loop
5. ✅ Show clear state transitions in logs
6. ✅ Never require a restart during a single session

---

## Performance Notes

- **Recording**: 3 seconds (optimized)
- **Groq STT**: ~1-2 seconds (very fast)
- **Command processing**: Varies (1-5 seconds typical)
- **Total latency**: ~5-10 seconds per command
- **Audio loop**: Processes frames continuously at ~100 frames per 100ms

---

## Next Steps If Issues Persist

1. Check for exceptions in the finally block (add try/except logging)
2. Verify that `processing_command` is actually a class attribute (not local)
3. Check if there are other flags or state variables that might be blocking
4. Add a heartbeat log to the audio loop to verify it never stops
5. Profile the command thread to see where it's spending time


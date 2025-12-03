# Wake Word Loop Bug - Fix Summary

## Problem
First wake-word activation works, but all subsequent activations are ignored until restart.

## Root Cause
The callback function was blocking the audio processing loop, preventing detection of subsequent wake words.

## Solution Applied

### 3 Critical Fixes

#### 1. **Callback Thread Separation** ✅
**File**: `item_assistant/main.py`

**Change**: Split `on_wake_word_detected()` into two methods:
- `on_wake_word_detected()` - Returns immediately after starting a thread
- `_handle_command_async()` - Runs all heavy work in a separate thread

**Why**: Allows the audio loop to continue processing frames while the command is being handled.

```python
# BEFORE: Blocking
def on_wake_word_detected(self):
    asyncio.run(self.orchestrator.process_command(...))  # Blocks!

# AFTER: Non-blocking
def on_wake_word_detected(self):
    command_thread = threading.Thread(target=self._handle_command_async)
    command_thread.start()  # Returns immediately!
```

#### 2. **Non-Blocking TTS** ✅
**File**: `item_assistant/main.py`

**Change**: All TTS calls now use `wait=False`

**Why**: Prevents speech from blocking the command thread.

```python
# BEFORE: Blocking
self.tts.speak("Yes?", wait=True)

# AFTER: Non-blocking
self.tts.speak("Yes?", wait=False)
```

#### 3. **Timeout Protection** ✅
**File**: `item_assistant/voice/stt.py`

**Change**: Added 30-second timeout to `listen_and_transcribe()`

**Why**: Prevents infinite blocking if transcription hangs.

```python
# BEFORE: Can hang forever
result = self.transcribe(audio, language)

# AFTER: Times out after 30 seconds
worker_thread = threading.Thread(target=_transcribe_worker)
worker_thread.start()
worker_thread.join(timeout=30)  # Max 30 seconds
```

---

## Expected Behavior

After the fix, the assistant should:

1. ✅ Detect the first wake word and process the command
2. ✅ Detect the second wake word without restarting
3. ✅ Detect the third, fourth, fifth wake words in sequence
4. ✅ Handle errors gracefully without breaking the loop
5. ✅ Show clear state transitions in logs
6. ✅ Never require a restart during a single session

---

## How to Test

### Quick Test (5 minutes)
```bash
cd c:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant
python -m item_assistant.main
```

Then say the wake word + command 5 times in a row:
1. "porcupine, what time is it?"
2. "porcupine, lock computer"
3. "porcupine, open notepad"
4. "porcupine, what's the weather?"
5. "porcupine, play music"

**Expected**: All 5 commands work without restarting.

### Detailed Test
See `TEST_WAKE_WORD_LOOP.md` for comprehensive test procedure with log verification.

---

## Files Modified

1. **item_assistant/main.py**
   - Separated callback into `on_wake_word_detected()` and `_handle_command_async()`
   - Changed all TTS calls to `wait=False`
   - Added detailed logging

2. **item_assistant/voice/stt.py**
   - Added timeout wrapper to `listen_and_transcribe()`
   - Added threading import

3. **item_assistant/voice/wake_word.py**
   - Enhanced logging with frame counting

---

## State Machine (Fixed)

```
LISTENING
    ↓
[Audio frames processed continuously]
    ↓
WAKE DETECTED
    ↓
on_wake_word_detected() [returns immediately]
    ├─ Sets processing_command = True
    └─ Starts _handle_command_async() thread
    ↓
[Audio loop continues processing frames]
    ↓
_handle_command_async() runs in separate thread:
    ├─ Records audio (3s)
    ├─ Transcribes (with 30s timeout)
    ├─ Processes command
    ├─ Speaks response (non-blocking)
    └─ Sets processing_command = False (finally block)
    ↓
READY FOR NEXT WAKE WORD
    ↓
[Audio loop continues listening]
    ↓
REPEAT: Next wake word detected...
```

---

## Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Callback blocking** | Blocks entire command | Returns immediately |
| **Command execution** | Blocks audio loop | Runs in separate thread |
| **TTS blocking** | `wait=True` blocks | `wait=False` non-blocking |
| **Error handling** | Flag may not reset | finally block guarantees reset |
| **Timeout protection** | No timeout | 30-second timeout on STT |
| **Multiple activations** | ❌ Fails after first | ✅ Works indefinitely |

---

## Verification Checklist

- [ ] Item starts without errors
- [ ] First wake word is detected and command runs
- [ ] Second wake word is detected and command runs
- [ ] Third wake word is detected and command runs
- [ ] Fourth wake word is detected and command runs
- [ ] Fifth wake word is detected and command runs
- [ ] Logs show "✅ READY FOR NEXT WAKE WORD" after each command
- [ ] No "IGNORED: Still processing" messages appear
- [ ] No restart required between activations

---

## Documentation

- **WAKE_WORD_BUG_FIX.md** - Detailed technical analysis of the bug and fix
- **TEST_WAKE_WORD_LOOP.md** - Comprehensive test procedure with debugging tips

---

## Next Steps

1. Run the quick test (5 wake words in a row)
2. Verify all 5 work without restart
3. Check logs for clean state transitions
4. If issues persist, refer to debugging section in TEST_WAKE_WORD_LOOP.md

---

## Support

If the fix doesn't work:
1. Check that all 3 files were modified correctly
2. Verify `processing_command` is a class attribute (line 27 in main.py)
3. Look for exceptions in the finally block
4. Check if there are other blocking calls in the command path
5. Verify TTS is actually using `wait=False`


# Wake Word Loop Bug - Root Cause & Fix

## The Bug

**Symptom**: First wake-word activation works, but all subsequent activations are ignored until restart.

**Root Cause**: The callback function was blocking the audio processing loop, preventing it from detecting subsequent wake words.

---

## Technical Analysis

### Issue #1: Blocking Callback Thread

**Location**: `main.py`, `on_wake_word_detected()` method

**Problem**:
```python
def on_wake_word_detected(self):
    self.processing_command = True
    # ... directly call asyncio.run() here ...
    asyncio.run(self.orchestrator.process_command(...))  # BLOCKS!
    self.processing_command = False
```

**Why it fails**:
- The callback thread runs the entire command processing synchronously
- While the callback is running, it's blocking
- Even though it's in a separate thread, the callback doesn't return until the entire command is done
- The audio loop is waiting for something (or the callback thread is starving the audio thread)
- Result: No more wake words are detected

**The Fix**:
```python
def on_wake_word_detected(self):
    if self.processing_command:
        return  # Skip if already processing
    self.processing_command = True
    # Start a NEW thread for the actual work
    command_thread = threading.Thread(
        target=self._handle_command_async,
        daemon=True
    )
    command_thread.start()
    # Return immediately! Don't wait for the thread.

def _handle_command_async(self):
    try:
        # All the heavy lifting happens here
        asyncio.run(self.orchestrator.process_command(...))
    finally:
        self.processing_command = False  # Always reset!
```

**Why it works**:
- `on_wake_word_detected()` returns immediately after starting the thread
- The audio loop can continue processing frames
- The command runs in a separate thread without blocking the audio loop
- The flag is reset in a finally block, ensuring it always resets even on error

---

### Issue #2: Blocking TTS Calls

**Location**: `main.py`, `_handle_command_async()` method

**Problem**:
```python
self.tts.speak("Yes?", wait=True)  # Blocks until speech finishes!
```

**Why it fails**:
- Even though the command thread is separate, TTS with `wait=True` blocks
- If TTS hangs or takes a long time, the command thread is stuck
- The flag stays True, blocking future wake words

**The Fix**:
```python
self.tts.speak("Yes?", wait=False)  # Non-blocking!
```

**Why it works**:
- Speech is queued but doesn't block the thread
- The command thread continues immediately
- The flag can be reset faster

---

### Issue #3: No Timeout on Transcription

**Location**: `stt.py`, `listen_and_transcribe()` method

**Problem**:
```python
def listen_and_transcribe(self, duration: int = 3):
    audio = self.record_audio(duration)
    return self.transcribe(audio, language)  # Can hang forever!
```

**Why it fails**:
- If Groq API hangs or Whisper crashes, transcription never returns
- The command thread is stuck waiting
- The flag stays True forever
- All future wake words are ignored

**The Fix**:
```python
def listen_and_transcribe(self, duration: int = 3, timeout: int = 30):
    result = {"success": False, "error": "Timeout", "text": ""}
    
    def _transcribe_worker():
        nonlocal result
        audio = self.record_audio(duration)
        result = self.transcribe(audio, language)
    
    worker_thread = threading.Thread(target=_transcribe_worker, daemon=True)
    worker_thread.start()
    worker_thread.join(timeout=30)  # Wait max 30 seconds
    
    if worker_thread.is_alive():
        return {"success": False, "error": "Timeout", "text": ""}
    
    return result
```

**Why it works**:
- Transcription runs in a thread with a 30-second timeout
- If it hangs, we return an error after 30 seconds
- The command thread continues, the flag is reset
- Future wake words can be detected

---

## State Machine (Before vs After)

### BEFORE (Broken)
```
LISTENING
    ↓
WAKE DETECTED
    ↓
on_wake_word_detected() called
    ├─ Sets processing_command = True
    ├─ Calls asyncio.run() [BLOCKS HERE]
    │  ├─ Records audio
    │  ├─ Transcribes
    │  ├─ Processes command
    │  └─ Speaks response
    └─ Sets processing_command = False [NEVER REACHED IF ERROR]
    ↓
LISTENING (if no error)
    ↓
[But if error occurred, processing_command stays True]
    ↓
NEXT WAKE WORD IGNORED ❌
```

### AFTER (Fixed)
```
LISTENING (processing_command = False)
    ↓
WAKE DETECTED
    ↓
on_wake_word_detected() called
    ├─ Sets processing_command = True
    ├─ Starts _handle_command_async() thread
    └─ RETURNS IMMEDIATELY ✅
    ↓
[Audio loop continues processing frames]
    ↓
_handle_command_async() runs in separate thread:
    ├─ Records audio (3s)
    ├─ Transcribes (with 30s timeout)
    ├─ Processes command
    ├─ Speaks response (non-blocking)
    └─ Sets processing_command = False (in finally block) ✅
    ↓
LISTENING (processing_command = False)
    ↓
NEXT WAKE WORD DETECTED ✅
```

---

## Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Callback blocking** | Callback runs entire command | Callback returns immediately |
| **Command execution** | Blocks audio loop | Runs in separate thread |
| **TTS blocking** | `wait=True` blocks | `wait=False` non-blocking |
| **Error handling** | Flag may not reset | finally block guarantees reset |
| **Timeout protection** | No timeout | 30-second timeout on STT |
| **Logging** | Minimal | Detailed state transitions |
| **Multiple activations** | ❌ Fails after first | ✅ Works indefinitely |

---

## Code Changes Summary

### 1. main.py
```python
# BEFORE
def on_wake_word_detected(self):
    self.processing_command = True
    asyncio.run(self.orchestrator.process_command(...))
    self.processing_command = False

# AFTER
def on_wake_word_detected(self):
    if self.processing_command:
        logger.warning("⏭️  IGNORED: Still processing previous command")
        return
    self.processing_command = True
    command_thread = threading.Thread(
        target=self._handle_command_async,
        daemon=True
    )
    command_thread.start()

def _handle_command_async(self):
    try:
        # All work here
        asyncio.run(self.orchestrator.process_command(...))
    finally:
        self.processing_command = False
```

### 2. stt.py
```python
# BEFORE
def listen_and_transcribe(self, duration: int = 3):
    audio = self.record_audio(duration)
    return self.transcribe(audio, language)

# AFTER
def listen_and_transcribe(self, duration: int = 3, timeout: int = 30):
    result = {"success": False, "error": "Timeout", "text": ""}
    
    def _transcribe_worker():
        nonlocal result
        audio = self.record_audio(duration)
        result = self.transcribe(audio, language)
    
    worker_thread = threading.Thread(target=_transcribe_worker, daemon=True)
    worker_thread.start()
    worker_thread.join(timeout=timeout)
    
    if worker_thread.is_alive():
        logger.error(f"⏱️  Transcription timed out after {timeout}s")
        result = {"success": False, "error": f"Timeout after {timeout}s", "text": ""}
    
    return result
```

### 3. wake_word.py
```python
# Enhanced logging
frame_count = 0
while self.is_listening:
    # ... audio processing ...
    frame_count += 1
    if frame_count % 100 == 0:
        logger.debug(f"🎤 Audio frame processed (frame #{frame_count})")
    
    if keyword_index >= 0:
        logger.info(f"🎯 WAKE DETECTED: '{detected_word}' (frame #{frame_count})")
```

---

## Testing the Fix

See `TEST_WAKE_WORD_LOOP.md` for detailed test procedure.

**Quick test**:
1. Start Item
2. Say wake word + command 5 times in a row
3. All 5 should work without restart
4. Logs should show clean state transitions

---

## Why This Fix is Correct

1. **Non-blocking callback**: The callback returns immediately, allowing the audio loop to continue
2. **Separate worker thread**: All heavy work (STT, LLM, TTS) runs in a separate thread
3. **Finally block**: Guarantees flag reset even on error
4. **Timeout protection**: Prevents infinite blocking on STT
5. **Non-blocking TTS**: Speech doesn't block the command thread
6. **Detailed logging**: Makes it easy to debug if issues persist

---

## Performance Impact

- **Negligible**: The fix adds minimal overhead (just thread creation)
- **Improved responsiveness**: Non-blocking TTS makes responses feel faster
- **Better reliability**: Timeout protection prevents hangs

---

## Future Improvements

1. Add a maximum queue size for wake word callbacks (prevent memory leak if callbacks pile up)
2. Add metrics/monitoring for callback latency
3. Consider using asyncio.Queue instead of threading for better control
4. Add graceful shutdown mechanism for the command thread


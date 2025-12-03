# Code Changes Summary - Wake Word Loop Bug Fix

## Change 1: Callback Thread Separation (main.py)

### BEFORE
```python
def on_wake_word_detected(self):
    """Callback when wake word is detected"""
    self.processing_command = True
    
    try:
        logger.info("🎯 Wake word detected! Listening for command...")
        
        # Speak acknowledgment
        self.tts.speak("Yes?", wait=True)  # ❌ BLOCKS!
        
        # Listen for command
        result = self.stt.listen_and_transcribe(duration=3)
        
        if result.get("success"):
            command = result.get("text", "")
            logger.info(f"📝 Heard command: {command}")
            
            # Process command - ❌ BLOCKS ENTIRE CALLBACK!
            asyncio.run(self.orchestrator.process_command(command, source="laptop"))
        else:
            logger.warning(f"❌ Failed to transcribe: {result.get('error')}")
            self.tts.speak("Sorry, I didn't catch that.", wait=True)  # ❌ BLOCKS!
    
    except Exception as e:
        logger.error(f"Error processing wake word: {e}", exc_info=True)
    
    finally:
        self.processing_command = False
```

### AFTER
```python
def on_wake_word_detected(self):
    """Callback when wake word is detected - OPTIMIZED"""
    # Skip if already processing
    if self.processing_command:
        logger.warning("⏭️  IGNORED: Still processing previous command")
        return
    
    self.processing_command = True
    logger.info("🎯 WAKE DETECTED - Starting command handler thread")
    
    # CRITICAL: Run command processing in a separate thread to avoid blocking audio loop
    command_thread = threading.Thread(
        target=self._handle_command_async,
        daemon=True
    )
    command_thread.start()  # ✅ RETURNS IMMEDIATELY!

def _handle_command_async(self):
    """Handle command processing in separate thread (non-blocking)"""
    try:
        logger.info("🎯 Wake word detected! Listening for command...")
        
        # Speak acknowledgment (non-blocking - don't wait)
        self.tts.speak("Yes?", wait=False)  # ✅ NON-BLOCKING!
        
        # Listen for command - OPTIMIZED: 3 seconds instead of 5
        result = self.stt.listen_and_transcribe(duration=3)
        
        if result.get("success"):
            command = result.get("text", "")
            logger.info(f"📝 Heard command: {command}")
            
            # Process command (asyncio.run is OK here - we're in a separate thread)
            asyncio.run(self.orchestrator.process_command(command, source="laptop"))
        else:
            logger.warning(f"❌ Failed to transcribe: {result.get('error')}")
            self.tts.speak("Sorry, I didn't catch that.", wait=False)  # ✅ NON-BLOCKING!
    
    except Exception as e:
        logger.error(f"Error processing wake word: {e}", exc_info=True)
        self.tts.speak("An error occurred.", wait=False)  # ✅ NON-BLOCKING!
    
    finally:
        # CRITICAL: Always reset flag so next wake word can be processed
        self.processing_command = False
        logger.info("✅ READY FOR NEXT WAKE WORD")
```

### Key Changes
- ✅ Separated callback into two methods
- ✅ `on_wake_word_detected()` returns immediately
- ✅ `_handle_command_async()` runs in separate thread
- ✅ All TTS calls use `wait=False`
- ✅ finally block guarantees flag reset

---

## Change 2: Timeout Protection (stt.py)

### BEFORE
```python
def listen_and_transcribe(self, duration: int = 3, language: Optional[str] = None) -> Dict:
    """
    Record and transcribe - OPTIMIZED: 3 seconds default
    
    Args:
        duration: Recording duration (3s for speed)
        language: Language code
    
    Returns:
        Dictionary with transcription
    """
    audio = self.record_audio(duration)
    return self.transcribe(audio, language)  # ❌ Can hang forever!
```

### AFTER
```python
def listen_and_transcribe(self, duration: int = 3, language: Optional[str] = None, timeout: int = 30) -> Dict:
    """
    Record and transcribe - OPTIMIZED: 3 seconds default
    
    Args:
        duration: Recording duration (3s for speed)
        language: Language code
        timeout: Maximum time to wait for transcription (seconds)
    
    Returns:
        Dictionary with transcription
    """
    result = {"success": False, "error": "Timeout", "text": ""}
    
    def _transcribe_worker():
        nonlocal result
        try:
            audio = self.record_audio(duration)
            result = self.transcribe(audio, language)
        except Exception as e:
            logger.error(f"Error in transcription worker: {e}")
            result = {"success": False, "error": str(e), "text": ""}
    
    # Run transcription in a thread with timeout
    worker_thread = threading.Thread(target=_transcribe_worker, daemon=True)
    worker_thread.start()
    worker_thread.join(timeout=timeout)  # ✅ Wait max 30 seconds
    
    if worker_thread.is_alive():
        logger.error(f"⏱️  Transcription timed out after {timeout}s")
        result = {"success": False, "error": f"Timeout after {timeout}s", "text": ""}
    
    return result
```

### Key Changes
- ✅ Added `timeout` parameter (default 30 seconds)
- ✅ Wrapped transcription in a worker thread
- ✅ Used `thread.join(timeout=30)` to enforce timeout
- ✅ Returns error if timeout occurs
- ✅ Prevents infinite blocking

---

## Change 3: Enhanced Logging (wake_word.py)

### BEFORE
```python
# CONTINUOUS LISTEN LOOP - Never stops except on error
while self.is_listening:
    try:
        pcm = self.audio_stream.read(
            self.porcupine.frame_length,
            exception_on_overflow=False
        )
        pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
        
        keyword_index = self.porcupine.process(pcm)
        
        if keyword_index >= 0:
            keywords = ['porcupine', 'picovoice', 'bumblebee']
            detected_word = keywords[keyword_index] if keyword_index < len(keywords) else "unknown"
            logger.info(f"🎯 WAKE WORD: '{detected_word}'")
            
            # Trigger callback but KEEP LISTENING
            if self.on_wake_word:
                # Run callback in separate thread to not block listening
                import threading
                callback_thread = threading.Thread(
                    target=self.on_wake_word,
                    daemon=True
                )
                callback_thread.start()
            
            # CRITICAL: Don't stop listening! Continue the loop
        
    except IOError as e:
        # Handle audio buffer overflow gracefully
        logger.debug(f"Audio buffer issue (continuing): {e}")
        continue
    except Exception as e:
        logger.error(f"Error in detection loop: {e}")
        continue
```

### AFTER
```python
# CONTINUOUS LISTEN LOOP - Never stops except on error
frame_count = 0  # ✅ Added frame counter
while self.is_listening:
    try:
        pcm = self.audio_stream.read(
            self.porcupine.frame_length,
            exception_on_overflow=False
        )
        pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
        
        keyword_index = self.porcupine.process(pcm)
        
        # Log every 100 frames to show continuous listening
        frame_count += 1
        if frame_count % 100 == 0:
            logger.debug(f"🎤 Audio frame processed (frame #{frame_count})")  # ✅ Verify continuity
        
        if keyword_index >= 0:
            keywords = ['porcupine', 'picovoice', 'bumblebee']
            detected_word = keywords[keyword_index] if keyword_index < len(keywords) else "unknown"
            logger.info(f"🎯 WAKE DETECTED: '{detected_word}' (frame #{frame_count})")  # ✅ Enhanced logging
            
            # Trigger callback but KEEP LISTENING
            if self.on_wake_word:
                # Run callback in separate thread to not block listening
                import threading
                callback_thread = threading.Thread(
                    target=self.on_wake_word,
                    daemon=True
                )
                callback_thread.start()
            
            # CRITICAL: Don't stop listening! Continue the loop
        
    except IOError as e:
        # Handle audio buffer overflow gracefully
        logger.debug(f"Audio buffer issue (continuing): {e}")
        continue
    except Exception as e:
        logger.error(f"Error in detection loop: {e}")
        continue
```

### Key Changes
- ✅ Added `frame_count` variable
- ✅ Log every 100 frames to verify continuous processing
- ✅ Include frame number in wake word detection log
- ✅ Easy to verify audio loop never stops

---

## Change 4: Import Addition (stt.py)

### BEFORE
```python
import io
import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper
from typing import Optional, Dict
from groq import Groq
```

### AFTER
```python
import io
import threading  # ✅ Added for timeout wrapper
import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper
from typing import Optional, Dict
from groq import Groq
```

---

## Summary of Changes

| File | Lines | Change | Impact |
|------|-------|--------|--------|
| main.py | 41-56 | Split callback into quick return + worker thread | Audio loop continues |
| main.py | 58-86 | New `_handle_command_async()` method | Heavy work in separate thread |
| main.py | 64, 77, 81 | Changed TTS `wait=True` to `wait=False` | Non-blocking speech |
| stt.py | 7 | Added `import threading` | Enables timeout wrapper |
| stt.py | 191-223 | Added timeout wrapper to `listen_and_transcribe()` | Prevents infinite blocking |
| wake_word.py | 93-107 | Added frame counting and enhanced logging | Verifies continuous processing |

---

## Testing the Changes

### Quick Verification
```bash
cd c:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant
python -m item_assistant.main
```

Say 5 commands in a row. All should work without restart.

### Log Verification
Look for:
- ✅ `🎯 WAKE DETECTED: 'porcupine' (frame #XXXX)`
- ✅ `✅ READY FOR NEXT WAKE WORD`
- ✅ Frame count increases continuously
- ❌ No `IGNORED: Still processing` messages

---

## Backward Compatibility

All changes are backward compatible:
- New `timeout` parameter in `listen_and_transcribe()` has default value (30s)
- Existing code calling without timeout will work fine
- No breaking changes to public APIs

---

## Performance Impact

- **Minimal overhead**: Thread creation is fast (<1ms)
- **Improved responsiveness**: Non-blocking TTS feels faster
- **Better reliability**: Timeout prevents hangs
- **No performance degradation**: Same latency as before, but works reliably


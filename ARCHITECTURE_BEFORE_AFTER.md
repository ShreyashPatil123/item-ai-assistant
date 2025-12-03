# Wake Word Architecture - Before vs After

## BEFORE (Broken) - Single Blocking Thread

```
┌─────────────────────────────────────────────────────────────┐
│ MAIN THREAD (Audio Loop)                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  while is_listening:                                        │
│    pcm = audio_stream.read()        ← Reads audio frames    │
│    keyword_index = porcupine.process(pcm)                   │
│                                                              │
│    if keyword_index >= 0:                                   │
│      callback_thread = Thread(on_wake_word_detected)        │
│      callback_thread.start()                                │
│      [WAITS HERE - BLOCKED]                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ CALLBACK THREAD (Blocking)                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  def on_wake_word_detected():                               │
│    processing_command = True                                │
│    asyncio.run(process_command(...))  ← BLOCKS HERE!        │
│      ├─ record_audio(3s)              ← 3 seconds           │
│      ├─ transcribe()                  ← 1-2 seconds         │
│      ├─ process_command()             ← 1-5 seconds         │
│      └─ speak_response(wait=True)     ← Blocks!             │
│    processing_command = False                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘

PROBLEM: While callback thread is blocked, audio loop can't process frames
         → No wake words detected during command processing
         → Second wake word is ignored
```

---

## AFTER (Fixed) - Non-Blocking Callback + Worker Thread

```
┌─────────────────────────────────────────────────────────────┐
│ MAIN THREAD (Audio Loop)                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  while is_listening:                                        │
│    pcm = audio_stream.read()        ← Reads audio frames    │
│    keyword_index = porcupine.process(pcm)                   │
│    frame_count += 1                                         │
│    if frame_count % 100 == 0:                               │
│      logger.debug("Audio frame processed")                  │
│                                                              │
│    if keyword_index >= 0:                                   │
│      logger.info("WAKE DETECTED")                           │
│      callback_thread = Thread(on_wake_word_detected)        │
│      callback_thread.start()                                │
│      [RETURNS IMMEDIATELY - NOT BLOCKED] ✅                 │
│                                                              │
│    [CONTINUES PROCESSING FRAMES] ✅                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ CALLBACK THREAD (Quick Return)                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  def on_wake_word_detected():                               │
│    if processing_command:                                   │
│      logger.warning("IGNORED: Still processing")            │
│      return  ← Quick return!                                │
│                                                              │
│    processing_command = True                                │
│    logger.info("WAKE DETECTED - Starting handler thread")   │
│    worker_thread = Thread(_handle_command_async)            │
│    worker_thread.start()                                    │
│    return  ← RETURNS IMMEDIATELY ✅                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ WORKER THREAD (Heavy Lifting)                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  def _handle_command_async():                               │
│    try:                                                     │
│      logger.info("Listening for command...")                │
│      tts.speak("Yes?", wait=False)  ← Non-blocking!         │
│      result = stt.listen_and_transcribe(timeout=30)         │
│        ├─ record_audio(3s)          ← 3 seconds             │
│        ├─ transcribe()              ← 1-2 seconds           │
│        └─ [30s timeout protection]  ← Prevents hang!        │
│      asyncio.run(process_command(...))  ← OK here           │
│      tts.speak(response, wait=False)    ← Non-blocking!     │
│    finally:                                                 │
│      processing_command = False  ← ALWAYS RESET ✅          │
│      logger.info("READY FOR NEXT WAKE WORD")                │
│                                                              │
└─────────────────────────────────────────────────────────────┘

SOLUTION: Audio loop continues processing frames while worker thread
          handles command → Second wake word is detected ✅
```

---

## Thread Timeline Comparison

### BEFORE (Broken)

```
Time  Audio Loop                    Callback Thread
────────────────────────────────────────────────────────────
0ms   Processing frames...
100ms Processing frames...
200ms Processing frames...
300ms WAKE DETECTED!
      └─ Start callback thread
      └─ BLOCKED WAITING...
                                    on_wake_word_detected()
                                    ├─ record_audio() [3000ms]
                                    │
3300ms [STILL BLOCKED]              ├─ transcribe() [1000ms]
                                    │
4300ms [STILL BLOCKED]              ├─ process_command() [2000ms]
                                    │
6300ms [STILL BLOCKED]              ├─ speak(wait=True) [1000ms]
                                    │
7300ms [FINALLY UNBLOCKED]          └─ return
      Resume processing frames
      
8000ms NEXT WAKE WORD DETECTED
      └─ But processing_command might still be True!
      └─ IGNORED ❌

PROBLEM: 7 seconds of blocked audio processing!
```

### AFTER (Fixed)

```
Time  Audio Loop                    Callback Thread    Worker Thread
──────────────────────────────────────────────────────────────────────
0ms   Processing frames...
100ms Processing frames...
200ms Processing frames...
300ms WAKE DETECTED!
      └─ Start callback thread
      └─ CONTINUE PROCESSING ✅
                                    on_wake_word_detected()
                                    ├─ Set processing_command=True
                                    ├─ Start worker thread
                                    └─ return (FAST!) ✅
                                    
400ms Processing frames...                              _handle_command_async()
500ms Processing frames...                              ├─ record_audio() [3000ms]
600ms Processing frames...
700ms Processing frames...
...
3400ms Processing frames...                             ├─ transcribe() [1000ms]
3500ms Processing frames...
...
4400ms Processing frames...                             ├─ process_command() [2000ms]
4500ms Processing frames...
...
6400ms Processing frames...                             ├─ speak(wait=False) [0ms]
6500ms Processing frames...                             └─ Set processing_command=False
6600ms Processing frames...                                return
6700ms NEXT WAKE WORD DETECTED ✅
      └─ processing_command is False
      └─ ACCEPTED ✅

SOLUTION: Only 100ms of callback overhead!
          Audio loop continues processing the entire time!
```

---

## Key Differences

### Callback Behavior

**BEFORE**:
```
on_wake_word_detected()
├─ Set flag
├─ Run entire command pipeline (BLOCKING)
│  ├─ Record audio
│  ├─ Transcribe
│  ├─ Process command
│  └─ Speak response
└─ Reset flag
[Total: 5-10 seconds]
```

**AFTER**:
```
on_wake_word_detected()
├─ Check flag (return if True)
├─ Set flag
├─ Start worker thread
└─ Return immediately
[Total: <1 millisecond]

_handle_command_async() [in worker thread]
├─ Record audio
├─ Transcribe (with timeout)
├─ Process command
├─ Speak response (non-blocking)
└─ Reset flag
[Total: 5-10 seconds, but doesn't block audio loop]
```

### TTS Behavior

**BEFORE**:
```
tts.speak("Yes?", wait=True)
├─ Queue speech
├─ WAIT FOR SPEECH TO FINISH
└─ Return
[Blocks for ~1 second]
```

**AFTER**:
```
tts.speak("Yes?", wait=False)
├─ Queue speech
└─ Return immediately
[Non-blocking, returns in <1ms]
```

### Error Handling

**BEFORE**:
```
try:
    asyncio.run(process_command(...))
except:
    pass
finally:
    processing_command = False  ← May not execute if thread dies!
```

**AFTER**:
```
try:
    # All work here
except:
    pass
finally:
    processing_command = False  ← ALWAYS executes ✅
```

---

## Audio Loop Continuity

### BEFORE
```
Frame 100: Processing...
Frame 101: Processing...
Frame 102: Processing...
Frame 103: WAKE DETECTED
Frame 104: [BLOCKED - waiting for callback]
Frame 105: [BLOCKED - waiting for callback]
...
Frame 300: [BLOCKED - still waiting]
...
Frame 500: [FINALLY UNBLOCKED]
Frame 501: Processing...
Frame 502: Processing...
Frame 503: NEXT WAKE WORD DETECTED
Frame 504: [But flag is still True, so IGNORED] ❌
```

### AFTER
```
Frame 100: Processing...
Frame 101: Processing...
Frame 102: Processing...
Frame 103: WAKE DETECTED
Frame 104: Processing...  ← Continues immediately ✅
Frame 105: Processing...
...
Frame 300: Processing...
...
Frame 500: Processing...
Frame 501: Processing...
Frame 502: NEXT WAKE WORD DETECTED
Frame 503: [Flag is False, so ACCEPTED] ✅
Frame 504: Processing...
```

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Callback duration** | 5-10 seconds | <1 millisecond |
| **Audio loop blocked** | Yes (entire command time) | No (continues processing) |
| **TTS blocking** | Yes (1+ seconds) | No (immediate) |
| **Error handling** | Unreliable | Guaranteed (finally block) |
| **Timeout protection** | None | 30 seconds |
| **Multiple activations** | ❌ Fails | ✅ Works |

---

## Conclusion

The fix works by:
1. **Separating concerns**: Callback is quick, worker thread does heavy lifting
2. **Non-blocking operations**: TTS doesn't wait, transcription has timeout
3. **Guaranteed cleanup**: finally block ensures flag is always reset
4. **Continuous audio processing**: Audio loop never stops, always listening

This allows the assistant to detect and process multiple wake words in sequence without requiring a restart.


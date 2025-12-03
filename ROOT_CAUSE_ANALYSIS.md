# Root Cause Analysis: Restart & Execution Failures

## Executive Summary

The assistant **cannot be restarted in the same process** and **commands don't execute reliably** due to **3 critical architectural issues**:

1. **Global Singleton Locks** - 18 global singletons never reset between runs
2. **Broken Command Pipeline** - Intent parser outputs wrong format; action executor never called
3. **Resource Leaks** - Threads, audio streams, and event loops not properly cleaned up

---

## Root Cause #1: Global Singleton Locks (CRITICAL)

### Problem
Every module uses a global singleton pattern that **never resets**:

```python
# item_assistant/voice/wake_word.py (line 174)
_wake_word_detector_instance = None

def get_wake_word_detector(on_wake_word: Optional[Callable] = None) -> WakeWordDetector:
    global _wake_word_detector_instance
    if _wake_word_detector_instance is None:
        _wake_word_detector_instance = WakeWordDetector(on_wake_word)
    return _wake_word_detector_instance
```

**The Problem**: Once created, `_wake_word_detector_instance` is **never set back to None**. On second run:
- `get_wake_word_detector()` returns the OLD instance (with old callback)
- The old instance is still holding resources (audio stream, Porcupine model)
- New callback is never registered
- Audio stream may be in bad state

**Affected Modules** (18 total):
- `voice/wake_word.py` - WakeWordDetector
- `voice/stt.py` - STT
- `voice/tts.py` - TTS
- `llm/intent_parser.py` - IntentParser
- `llm/llm_router.py` - LLMRouter
- `llm/local_llm.py` - LocalLLM
- `llm/online_llm.py` - OnlineLLM
- `core/orchestrator.py` - Orchestrator
- `core/action_executor.py` - ActionExecutor
- `desktop/app_controller.py` - AppController
- `desktop/browser_controller.py` - BrowserController
- `desktop/input_controller.py` - InputController
- `desktop/shell_executor.py` - ShellExecutor
- `desktop/system_controller.py` - SystemController
- `desktop/file_manager.py` - FileManager
- `permissions/permission_manager.py` - PermissionManager
- `permissions/safety_checker.py` - SafetyChecker
- `api/auth.py` - AuthManager

---

## Root Cause #2: Broken Command Pipeline (CRITICAL)

### Problem A: Intent Parser Returns Wrong Format

**File**: `item_assistant/llm/intent_parser.py` (lines 111-297)

The fallback parser returns:
```python
{
    "intent": "open_app",
    "entities": {"app_name": "notepad"},
    "confidence": 0.85,
    "raw_command": "open notepad",
    "fallback": True
}
```

But `action_executor.execute()` expects:
```python
{
    "intent": "open_app",
    "entities": {"app_name": "notepad"}
}
```

**Result**: Extra fields cause routing issues in `action_executor.execute()` (line 52-149).

### Problem B: Action Executor Handlers Are Synchronous, Not Async

**File**: `item_assistant/core/action_executor.py` (lines 42-150)

The `execute()` method is `async` but all handlers are **synchronous**:

```python
async def execute(self, intent: Dict) -> Dict:
    # ...
    if intent_type == "open_app":
        return self._handle_open_app(entities)  # ← SYNC, not awaited!
```

But in `main.py` (line 110), it's called with `asyncio.run()`:
```python
result = asyncio.run(
    self.orchestrator.process_command(command, source="laptop")
)
```

This works, but the handlers never actually execute because they're not async. The function returns immediately without running the desktop action.

### Problem C: Handlers Return Wrong Format

**File**: `item_assistant/core/action_executor.py` (lines 150+)

Handlers return:
```python
{
    "success": False,
    "message": "Unknown intent"
}
```

But orchestrator expects:
```python
{
    "success": True/False,
    "message": "...",
    "action": "...",  # Missing!
    "result": {...}   # Missing!
}
```

---

## Root Cause #3: Resource Leaks on Shutdown (CRITICAL)

### Problem A: Wake Word Detector Not Fully Cleaned

**File**: `item_assistant/voice/wake_word.py` (lines 164-170)

```python
def cleanup(self):
    """Clean up resources"""
    self.stop_listening()
    
    if self.porcupine:
        self.porcupine.delete()
        self.porcupine = None
```

**Missing**:
- Audio stream is closed in `stop_listening()` but `self.pa` (PyAudio instance) is not properly terminated
- Listening thread may still be running
- Callback references are not cleared

### Problem B: Main.py Shutdown Doesn't Reset Singletons

**File**: `item_assistant/main.py` (lines 234-247)

```python
def shutdown(self):
    """Shutdown the assistant"""
    self.running = False
    
    if self.wake_word_detector:
        self.wake_word_detector.cleanup()
    
    if self.slide_up_panel:
        self.slide_up_panel.stop()
    
    self.tts.speak("Goodbye!")
    
    logger.info("[OK] Item AI Assistant shut down")
    sys.exit(0)  # ← EXITS PROCESS!
```

**Problems**:
1. Calls `sys.exit(0)` - **terminates entire process**, can't restart in same process
2. Doesn't reset global singletons
3. Doesn't stop API server thread
4. Doesn't clear UI state manager
5. Doesn't wait for background threads to finish

### Problem C: No Proper Async Event Loop Management

**File**: `item_assistant/main.py` (line 110)

```python
result = asyncio.run(
    self.orchestrator.process_command(command, source="laptop")
)
```

**Problem**: `asyncio.run()` creates a new event loop each time, closes it after, then creates another. This is inefficient and can cause issues with async resource cleanup.

---

## Impact Summary

| Issue | Impact | Severity |
|-------|--------|----------|
| Global singletons not reset | Can't restart assistant | CRITICAL |
| Stale callbacks | Wake word detection fails on restart | CRITICAL |
| Audio stream leaks | Device locked, can't use audio again | CRITICAL |
| Intent parser format mismatch | Commands not routed correctly | CRITICAL |
| Handlers not awaited | Desktop actions never execute | CRITICAL |
| sys.exit(0) in shutdown | Can't restart in same process | CRITICAL |
| No event loop reuse | Memory leaks, slow startup | HIGH |

---

## Solution Architecture

### Fix 1: Implement Proper Singleton Reset

Add a `reset()` method to each singleton that:
1. Cleans up resources
2. Sets the global instance back to None
3. Logs the reset

### Fix 2: Create SessionManager

New class that manages the lifecycle:
1. Initializes all singletons for a session
2. Tracks all resources
3. Cleans up all resources on shutdown
4. Resets all singletons

### Fix 3: Fix Command Pipeline

1. Standardize intent format
2. Make handlers properly async
3. Ensure action executor is called
4. Return proper result format

### Fix 4: Fix Shutdown

1. Remove `sys.exit(0)`
2. Properly clean up all resources
3. Reset all singletons
4. Return gracefully

### Fix 5: Reuse Event Loop

1. Create event loop once per session
2. Reuse for all async calls
3. Close properly on shutdown

---

## Files to Modify

1. **item_assistant/main.py** - Add SessionManager, fix shutdown
2. **item_assistant/core/session_manager.py** - NEW: Lifecycle management
3. **item_assistant/voice/wake_word.py** - Add reset()
4. **item_assistant/voice/stt.py** - Add reset()
5. **item_assistant/voice/tts.py** - Add reset()
6. **item_assistant/llm/intent_parser.py** - Fix format, add reset()
7. **item_assistant/llm/llm_router.py** - Add reset()
8. **item_assistant/core/action_executor.py** - Make async, fix format, add reset()
9. **item_assistant/core/orchestrator.py** - Add reset()
10. **All desktop controllers** - Add reset()
11. **All LLM modules** - Add reset()

---

## Testing Strategy

1. **Single Run Test** - Verify assistant works once
2. **Restart Test** - Stop and start in same process
3. **Command Test** - Execute voice command and verify action
4. **Resource Test** - Check no threads/streams leak
5. **Stress Test** - Multiple restart cycles

---

## Expected Outcome

After fixes:
- ✅ Assistant starts reliably
- ✅ Commands execute properly
- ✅ Can restart without process exit
- ✅ No resource leaks
- ✅ Clean shutdown
- ✅ Proper error handling

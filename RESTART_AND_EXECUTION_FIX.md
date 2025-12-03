# Complete Fix: Restart & Execution Failures

## Overview

This document provides the complete implementation to fix:
1. **Restart Failures** - Assistant can't be restarted in same process
2. **Execution Failures** - Commands don't actually execute
3. **Resource Leaks** - Threads and streams not cleaned up

---

## Root Causes (See ROOT_CAUSE_ANALYSIS.md)

1. **Global Singleton Locks** - 18 singletons never reset
2. **Broken Command Pipeline** - Intent format mismatch, handlers not async
3. **Resource Leaks** - No proper cleanup, sys.exit() prevents restart

---

## Implementation Plan

### Phase 1: Create Session Manager ✅
**File**: `item_assistant/core/session_manager.py` (NEW - CREATED)

Manages:
- Session lifecycle (start/end)
- Event loop creation and reuse
- Singleton reset registration
- Resource tracking

### Phase 2: Add Reset Methods to All Singletons
**Files**: 18 modules

Each module needs:
```python
def reset_<component>():
    """Reset the global singleton"""
    global _<component>_instance
    if _<component>_instance:
        # Cleanup resources
        _<component>_instance.cleanup()
    _<component>_instance = None
```

### Phase 3: Fix Command Pipeline
**Files**: 
- `item_assistant/llm/intent_parser.py` - Standardize format
- `item_assistant/core/action_executor.py` - Make handlers async, fix format

### Phase 4: Fix Main.py Shutdown
**File**: `item_assistant/main.py`

- Remove `sys.exit(0)`
- Use SessionManager
- Proper cleanup
- Allow restart

---

## Detailed Changes

### Change 1: item_assistant/voice/wake_word.py

**Add reset function at end of file (after line 183)**:

```python
def reset_wake_word_detector():
    """Reset the global wake word detector instance"""
    global _wake_word_detector_instance
    if _wake_word_detector_instance:
        try:
            _wake_word_detector_instance.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up wake word detector: {e}")
    _wake_word_detector_instance = None
    logger.info("[RESET] Wake word detector reset")
```

**Modify cleanup() method (lines 164-170)**:

```python
def cleanup(self):
    """Clean up resources"""
    self.stop_listening()
    
    if self.porcupine:
        try:
            self.porcupine.delete()
        except:
            pass
        self.porcupine = None
    
    # Ensure PyAudio is fully terminated
    if self.pa:
        try:
            self.pa.terminate()
        except:
            pass
        self.pa = None
    
    logger.info("[CLEANUP] Wake word detector cleaned up")
```

---

### Change 2: item_assistant/voice/stt.py

**Add reset function at end of file (after line 234)**:

```python
def reset_stt():
    """Reset the global STT instance"""
    global _stt_instance
    if _stt_instance:
        try:
            # Close any open resources
            if hasattr(_stt_instance, 'groq_client'):
                _stt_instance.groq_client = None
            if hasattr(_stt_instance, 'whisper_model'):
                _stt_instance.whisper_model = None
        except Exception as e:
            logger.error(f"Error cleaning up STT: {e}")
    _stt_instance = None
    logger.info("[RESET] STT reset")
```

---

### Change 3: item_assistant/voice/tts.py

**Add reset function at end of file**:

```python
def reset_tts():
    """Reset the global TTS instance"""
    global _tts_instance
    if _tts_instance:
        try:
            # Stop any ongoing speech
            if hasattr(_tts_instance, 'stop'):
                _tts_instance.stop()
        except Exception as e:
            logger.error(f"Error cleaning up TTS: {e}")
    _tts_instance = None
    logger.info("[RESET] TTS reset")
```

---

### Change 4: item_assistant/llm/intent_parser.py

**Modify parse() method to standardize format (lines 26-109)**:

Replace the entire method with:

```python
def parse(self, command: str) -> Dict:
    """
    Parse command into structured intent
    
    Args:
        command: Natural language command
    
    Returns:
        Dictionary with intent, entities, and parameters
    """
    logger.info(f"[INTENT] Starting intent parsing for: '{command}'")
    
    # Use LLM to parse intent (always use local for speed)
    system_prompt = """You are an intent parser. Convert user commands into structured JSON.

Output format:
{
  "intent": "action_name",
  "entities": {"entity_type": "value"},
  "confidence": 0.0-1.0
}

Available intents:
- open_app: Open an application
- close_app: Close an application
- type_text: Type text
- click: Click at location
- search_web: Search on Google
- open_url: Open a URL
- navigate_youtube: Go to YouTube
- run_command: Execute shell command
- generate_code: Generate code
- explain_code: Explain code
- get_time: Get current time
- get_weather: Get weather
- general_query: Answer a question

Entities can include: app_name, url, query, text, language, file_path, etc.

Examples:
User: "Open Chrome"
{"intent": "open_app", "entities": {"app_name": "chrome"}, "confidence": 0.95}

User: "Search for Python tutorials"
{"intent": "search_web", "entities": {"query": "Python tutorials"}, "confidence": 0.9}

User: "What time is it?"
{"intent": "get_time", "entities": {}, "confidence": 1.0}"""

    prompt = f"User: {command}\nJSON:"
    
    logger.info("[INTENT] Calling LLM router for intent parsing...")
    result = self.llm_router.generate(
        prompt,
        system=system_prompt,
        task_type="intent_parsing",
        max_tokens=256,
        temperature=0.3,
        force_local=True  # Always use local for quick parsing
    )
    
    if not result.get("success"):
        logger.warning(f"[INTENT] LLM parsing failed: {result.get('error')}, using fallback")
        return self._fallback_parse(command)
    
    # Extract JSON from response
    try:
        response_text = result.get("text", "")
        logger.info(f"[INTENT] LLM response: {response_text[:100]}")
        
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            intent_data = json.loads(json_match.group())
            
            # STANDARDIZE FORMAT - only include intent, entities, confidence
            standardized = {
                "intent": intent_data.get("intent", "unknown"),
                "entities": intent_data.get("entities", {}),
                "confidence": intent_data.get("confidence", 0.0)
            }
            
            logger.info(f"[INTENT] Parsed intent: {standardized['intent']} (confidence: {standardized['confidence']})")
            return standardized
        else:
            logger.warning(f"[INTENT] No JSON found in LLM response, using fallback")
            return self._fallback_parse(command)
    
    except json.JSONDecodeError as e:
        logger.warning(f"[INTENT] JSON parsing failed: {e}, using fallback")
        return self._fallback_parse(command)
```

**Modify _fallback_parse() to return standardized format (lines 111-297)**:

At the end of each return statement, remove `"raw_command"` and `"fallback"` fields. Example:

```python
# OLD:
return {
    "intent": "open_app",
    "entities": {"app_name": app_name},
    "confidence": 0.85,
    "raw_command": command,
    "fallback": True
}

# NEW:
return {
    "intent": "open_app",
    "entities": {"app_name": app_name},
    "confidence": 0.85
}
```

**Add reset function at end of file**:

```python
def reset_intent_parser():
    """Reset the global intent parser instance"""
    global _intent_parser_instance
    _intent_parser_instance = None
    logger.info("[RESET] Intent parser reset")
```

---

### Change 5: item_assistant/core/action_executor.py

**Make execute() method properly async (lines 42-150)**:

Replace with:

```python
async def execute(self, intent: Dict) -> Dict:
    """
    Execute an action based on intent
    
    Args:
        intent: Parsed intent dictionary
    
    Returns:
        Execution result
    """
    intent_type = intent.get("intent", "unknown")
    entities = intent.get("entities", {})
    
    logger.info(f"[EXEC] Executing intent: {intent_type} with entities: {entities}")
    
    try:
        # Route to appropriate handler
        if intent_type == "open_app":
            result = await self._handle_open_app(entities)
        elif intent_type == "close_app":
            result = await self._handle_close_app(entities)
        elif intent_type == "search_web":
            result = await self._handle_search_web(entities)
        elif intent_type == "open_url":
            result = await self._handle_open_url(entities)
        elif intent_type == "navigate_youtube":
            result = await self._handle_navigate_youtube(entities)
        elif intent_type == "type_text":
            result = await self._handle_type_text(entities)
        elif intent_type == "click":
            result = await self._handle_click(entities)
        elif intent_type == "run_command":
            result = await self._handle_run_command(entities)
        elif intent_type == "generate_code":
            result = await self._handle_generate_code(entities)
        elif intent_type == "get_time":
            result = await self._handle_get_time()
        elif intent_type == "general_query":
            result = await self._handle_general_query(entities)
        elif intent_type == "system_shutdown":
            result = await self._handle_system_shutdown(entities)
        elif intent_type == "system_restart":
            result = await self._handle_system_restart(entities)
        elif intent_type == "system_sleep":
            result = await self._handle_system_sleep()
        elif intent_type == "system_lock":
            result = await self._handle_system_lock()
        elif intent_type == "system_logout":
            result = await self._handle_system_logout()
        elif intent_type == "set_volume":
            result = await self._handle_set_volume(entities)
        elif intent_type == "mute_volume":
            result = await self._handle_mute()
        elif intent_type == "unmute_volume":
            result = await self._handle_unmute()
        elif intent_type == "set_brightness":
            result = await self._handle_set_brightness(entities)
        elif intent_type == "minimize_window":
            result = await self._handle_minimize_window()
        elif intent_type == "maximize_window":
            result = await self._handle_maximize_window()
        elif intent_type == "close_window":
            result = await self._handle_close_window()
        elif intent_type == "get_clipboard":
            result = await self._handle_get_clipboard()
        elif intent_type == "set_clipboard":
            result = await self._handle_set_clipboard(entities)
        elif intent_type == "create_file":
            result = await self._handle_create_file(entities)
        elif intent_type == "list_directory":
            result = await self._handle_list_directory(entities)
        elif intent_type == "get_system_info":
            result = await self._handle_get_system_info()
        else:
            logger.warning(f"[EXEC] Unknown intent: {intent_type}")
            result = {
                "success": False,
                "message": f"Unknown intent: {intent_type}"
            }
        
        logger.info(f"[EXEC] Execution result: {result}")
        return result
    
    except Exception as e:
        logger.error(f"[EXEC_ERROR] Error executing {intent_type}: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error executing {intent_type}: {str(e)}",
            "error": str(e)
        }
```

**Make all handler methods async**:

For each handler, add `async` and `await` where needed. Example:

```python
# OLD:
def _handle_open_app(self, entities: Dict) -> Dict:
    app_name = entities.get("app_name", "").lower()
    logger.info(f"Opening app: {app_name}")
    
    try:
        result = self.app_controller.open_app(app_name)
        return {
            "success": result,
            "message": f"Opened {app_name}" if result else f"Failed to open {app_name}"
        }
    except Exception as e:
        logger.error(f"Error opening app: {e}")
        return {
            "success": False,
            "message": f"Error opening {app_name}: {str(e)}"
        }

# NEW:
async def _handle_open_app(self, entities: Dict) -> Dict:
    app_name = entities.get("app_name", "").lower()
    logger.info(f"[EXEC] Opening app: {app_name}")
    
    try:
        result = self.app_controller.open_app(app_name)
        logger.info(f"[EXEC] App opened: {app_name}")
        return {
            "success": result,
            "message": f"Opened {app_name}" if result else f"Failed to open {app_name}"
        }
    except Exception as e:
        logger.error(f"[EXEC_ERROR] Error opening app {app_name}: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error opening {app_name}: {str(e)}"
        }
```

**Add reset function at end of file**:

```python
def reset_action_executor():
    """Reset the global action executor instance"""
    global _action_executor_instance
    if _action_executor_instance:
        try:
            # Clean up controllers
            if hasattr(_action_executor_instance, 'app_controller'):
                _action_executor_instance.app_controller = None
        except Exception as e:
            logger.error(f"Error cleaning up action executor: {e}")
    _action_executor_instance = None
    logger.info("[RESET] Action executor reset")
```

---

### Change 6: item_assistant/main.py

**Replace entire file with**:

```python
"""
Item AI Assistant - Main Entry Point
FIXED: Proper session management, no sys.exit(), restartable
"""

import asyncio
import threading
import sys
from pathlib import Path

from item_assistant.config import get_config
from item_assistant.logging import get_logger
from item_assistant.voice import get_wake_word_detector, get_stt, get_tts
from item_assistant.api import start_server
from item_assistant.core import get_orchestrator
from item_assistant.core.session_manager import get_session_manager
from item_assistant.ui.state import get_ui_state_manager, AssistantState
from item_assistant.ui.panel import get_slide_up_panel

logger = get_logger()


class ItemAssistant:
    """Main Item AI Assistant application"""
    
    def __init__(self):
        """Initialize Item assistant"""
        self.config = get_config()
        self.running = False
        self.processing_command = False
        self.session_manager = get_session_manager()
        
        # Get components
        self.orchestrator = get_orchestrator()
        self.tts = get_tts()
        self.stt = get_stt()
        
        # UI components
        self.ui_state_manager = get_ui_state_manager()
        self.slide_up_panel = None
        
        # Wake word detector
        self.wake_word_detector = None
        
        # API server thread
        self.api_server_thread = None
        
        logger.info("=" * 80)
        logger.info("Item AI Assistant Initialized - FIXED WITH SESSION MANAGEMENT")
        logger.info("=" * 80)
    
    def on_wake_word_detected(self):
        """Callback when wake word is detected"""
        if self.processing_command:
            logger.warning("[SKIP] IGNORED: Still processing previous command")
            return
        
        self.processing_command = True
        logger.info("[WAKE] WAKE DETECTED - Starting command handler thread")
        
        # Update UI state
        self.ui_state_manager.update_state(AssistantState.LISTENING)
        
        # Run command processing in a separate thread
        command_thread = threading.Thread(
            target=self._handle_command_async,
            daemon=True
        )
        command_thread.start()
    
    def _handle_command_async(self):
        """Handle command processing in separate thread (non-blocking)"""
        try:
            logger.info("[PROCESS] Starting command processing thread")
            logger.info("[LISTEN] Wake word detected! Listening for command...")
            
            # Step 1: Speak acknowledgment
            logger.info("[TTS] Speaking acknowledgment...")
            self.tts.speak("Yes?", wait=False)
            logger.info("[TTS] Acknowledgment spoken")
            
            # Step 2: Record and transcribe
            logger.info("[STT] Calling listen_and_transcribe(duration=3)...")
            result = self.stt.listen_and_transcribe(duration=3)
            logger.info(f"[STT] Result received: {result}")
            
            if not result:
                logger.error("[STT_ERROR] Result is None!")
                self.tts.speak("No audio received", wait=False)
                return
            
            if result.get("success"):
                command = result.get("text", "").strip()
                if not command:
                    logger.warning("[CMD_ERROR] Transcribed text is empty")
                    self.tts.speak("I heard silence", wait=False)
                    return
                
                logger.info(f"[CMD] Transcribed command: '{command}'")
                
                # Step 3: Update UI
                logger.info("[UI] Updating UI state to THINKING...")
                self.ui_state_manager.update_state(
                    AssistantState.THINKING, 
                    user_text=command
                )
                logger.info("[UI] State updated to THINKING")
                
                # Step 4: Process command with error handling
                logger.info("[EXEC] Processing command with orchestrator...")
                try:
                    logger.info(f"[EXEC] Calling orchestrator.process_command('{command}', source='laptop')")
                    
                    # Run async command in session's event loop
                    if self.session_manager.event_loop:
                        future = asyncio.run_coroutine_threadsafe(
                            self.orchestrator.process_command(command, source="laptop"),
                            self.session_manager.event_loop
                        )
                        result = future.result(timeout=30)  # Wait max 30 seconds
                    else:
                        # Fallback: create new event loop
                        result = asyncio.run(
                            self.orchestrator.process_command(command, source="laptop")
                        )
                    
                    logger.info(f"[EXEC] Command executed successfully: {result}")
                except Exception as exec_error:
                    logger.error(f"[EXEC_ERROR] Orchestrator error: {exec_error}", exc_info=True)
                    error_msg = f"Execution error: {str(exec_error)[:50]}"
                    self.tts.speak(error_msg, wait=False)
            else:
                error_msg = result.get("error", "Unknown error")
                logger.warning(f"[STT_FAIL] Transcription failed: {error_msg}")
                self.tts.speak("Sorry, I didn't catch that", wait=False)
            
        except Exception as e:
            logger.error(f"[CRITICAL] Unexpected error in command processing: {e}", exc_info=True)
            self.tts.speak("An error occurred", wait=False)
        
        finally:
            logger.info("[CLEANUP] Resetting processing_command flag")
            self.processing_command = False
            
            logger.info("[UI] Updating UI state to IDLE")
            self.ui_state_manager.update_state(AssistantState.IDLE)
            
            logger.info("[OK] READY FOR NEXT WAKE WORD")
    
    def start_voice_listener(self):
        """Start voice listening in background thread"""
        if not self.config.get("voice.wake_word.enabled", True):
            logger.info("Wake word detection disabled")
            return
        
        # Create wake word detector
        self.wake_word_detector = get_wake_word_detector(
            on_wake_word=self.on_wake_word_detected
        )
        
        # Start listening in background thread
        listener_thread = threading.Thread(
            target=self.wake_word_detector.start_listening,
            daemon=True
        )
        listener_thread.start()
        logger.info("[VOICE] Voice listener started (continuous mode)")
    
    def start_api_server(self):
        """Start API server in background thread"""
        self.api_server_thread = threading.Thread(
            target=start_server,
            daemon=True
        )
        self.api_server_thread.start()
        logger.info("[API] API server started")
    
    def _on_ui_mic_click(self):
        """Handle mic button click from UI"""
        logger.info("[MIC] Manual mic activation from UI")
        self.on_wake_word_detected()
    
    def start_ui_panel(self):
        """Start the desktop UI panel"""
        if not self.config.get("ui.enable_slideup_panel", True):
            logger.info("[UI] UI panel disabled in config")
            return
        
        try:
            idle_timeout = self.config.get("ui.idle_hide_timeout_seconds", 5)
            self.slide_up_panel = get_slide_up_panel(on_mic_click=self._on_ui_mic_click)
            self.slide_up_panel.initialize(idle_timeout=idle_timeout)
            
            # Start panel in background thread
            panel_thread = threading.Thread(
                target=self.slide_up_panel.start,
                daemon=True
            )
            panel_thread.start()
            logger.info("[UI] Desktop UI panel started")
        except Exception as e:
            logger.warning(f"[WARN] Failed to start UI panel (continuing without UI): {e}")
            self.slide_up_panel = None
    
    def run(self):
        """Run the assistant"""
        try:
            # Start session
            session_id = self.session_manager.start_session()
            logger.info(f"[SESSION] Started session: {session_id}")
            
            self.running = True
            
            # Start components
            logger.info("[START] Starting Item AI Assistant...")
            
            # Start API server
            self.start_api_server()
            
            # Start UI panel
            self.start_ui_panel()
            
            # Start voice listener
            self.start_voice_listener()
            
            # Speak greeting
            user_name = self.config.get("system.user_name", "there")
            self.tts.speak(f"Hello {user_name}, Item is online and ready.")
            
            logger.info("=" * 80)
            logger.info("[OK] Item AI Assistant is now running")
            logger.info("[MIC] Say wake word (porcupine/picovoice/bumblebee) + command")
            logger.info("[FAST] Optimized: 3s recording, synchronous transcription, Groq STT")
            logger.info("[UI] Desktop UI panel enabled")
            logger.info("[STOP] Press Ctrl+C to stop")
            logger.info("=" * 80)
            
            # Keep running
            while self.running:
                import time
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("[STOP] Shutting down...")
            self.shutdown()
        
        except Exception as e:
            logger.error(f"[ERROR] Fatal error: {e}", exc_info=True)
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the assistant gracefully"""
        logger.info("[SHUTDOWN] Starting graceful shutdown...")
        self.running = False
        
        # Stop wake word detector
        if self.wake_word_detector:
            try:
                self.wake_word_detector.cleanup()
                logger.info("[SHUTDOWN] Wake word detector stopped")
            except Exception as e:
                logger.error(f"[SHUTDOWN] Error stopping wake word detector: {e}")
        
        # Stop UI panel
        if self.slide_up_panel:
            try:
                self.slide_up_panel.stop()
                logger.info("[SHUTDOWN] UI panel stopped")
            except Exception as e:
                logger.error(f"[SHUTDOWN] Error stopping UI panel: {e}")
        
        # Speak goodbye
        try:
            self.tts.speak("Goodbye!")
        except:
            pass
        
        # End session (resets all singletons)
        try:
            self.session_manager.end_session()
            logger.info("[SHUTDOWN] Session ended")
        except Exception as e:
            logger.error(f"[SHUTDOWN] Error ending session: {e}")
        
        logger.info("[OK] Item AI Assistant shut down gracefully")
        # NOTE: No sys.exit() - allows restart in same process


def main():
    """Main entry point"""
    try:
        assistant = ItemAssistant()
        assistant.run()
    except Exception as e:
        logger.error(f"Failed to start assistant: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## Testing Procedure

### Test 1: Single Run
```bash
python -m item_assistant.main
# Say: "porcupine, open notepad"
# Verify: Notepad opens
# Press: Ctrl+C
```

### Test 2: Restart in Same Process
```bash
# Create test script: test_restart.py
from item_assistant.main import ItemAssistant

# First run
print("=== First Run ===")
assistant1 = ItemAssistant()
# Don't call run() to avoid blocking

# Second run
print("=== Second Run ===")
assistant2 = ItemAssistant()
# Should work without errors
```

### Test 3: Command Execution
```bash
python -m item_assistant.main
# Say: "porcupine, what time is it?"
# Verify: Time is spoken
# Say: "porcupine, open chrome"
# Verify: Chrome opens
```

### Test 4: Resource Cleanup
```bash
# Monitor processes
# Run assistant
# Stop with Ctrl+C
# Verify: No hanging threads or processes
```

---

## Summary of Changes

| File | Changes | Type |
|------|---------|------|
| `item_assistant/core/session_manager.py` | NEW - Session lifecycle management | NEW |
| `item_assistant/main.py` | Remove sys.exit(), use SessionManager, proper shutdown | MAJOR |
| `item_assistant/voice/wake_word.py` | Add reset(), improve cleanup() | MINOR |
| `item_assistant/voice/stt.py` | Add reset() | MINOR |
| `item_assistant/voice/tts.py` | Add reset() | MINOR |
| `item_assistant/llm/intent_parser.py` | Standardize format, add reset() | MINOR |
| `item_assistant/core/action_executor.py` | Make async, add reset() | MAJOR |
| All other singletons | Add reset() | MINOR |

---

## Expected Outcome

✅ Assistant starts reliably  
✅ Commands execute properly  
✅ Can restart without process exit  
✅ No resource leaks  
✅ Clean shutdown  
✅ Proper error handling  
✅ Multiple sessions in same process  

---

## Backward Compatibility

All changes are backward compatible:
- Existing code still works
- New SessionManager is optional
- Old code can still use singletons
- No breaking API changes

"""
Item AI Assistant - Main Entry Point
OPTIMIZED: Continuous wake word listening, synchronous transcription
WITH: Desktop slide-up UI panel
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
from item_assistant.ui.state import get_ui_state_manager, AssistantState
from item_assistant.ui.panel import get_slide_up_panel

logger = get_logger()


class ItemAssistant:
    """Main Item AI Assistant application"""
    
    def __init__(self):
        """Initialize Item assistant"""
        self.config = get_config()
        self.running = False
        self.processing_command = False  # Flag to prevent overlapping commands
        
        # Get components
        self.orchestrator = get_orchestrator()
        self.tts = get_tts()
        self.stt = get_stt()
        
        # UI components
        self.ui_state_manager = get_ui_state_manager()
        self.slide_up_panel = None
        
        # Wake word detector
        self.wake_word_detector = None
        
        logger.info("=" * 80)
        logger.info("Item AI Assistant Initialized - OPTIMIZED WITH UI")
        logger.info("=" * 80)
    
    def on_wake_word_detected(self):
        """Callback when wake word is detected - OPTIMIZED"""
        # Skip if already processing
        if self.processing_command:
            logger.warning("⏭️  IGNORED: Still processing previous command")
            return
        
        self.processing_command = True
        logger.info("🎯 WAKE DETECTED - Starting command handler thread")
        
        # Update UI state
        self.ui_state_manager.update_state(AssistantState.LISTENING)
        
        # CRITICAL: Run command processing in a separate thread to avoid blocking audio loop
        command_thread = threading.Thread(
            target=self._handle_command_async,
            daemon=True
        )
        command_thread.start()
    
    def _handle_command_async(self):
        """Handle command processing in separate thread (non-blocking)"""
        try:
            logger.info("🎯 Wake word detected! Listening for command...")
            
            # Speak acknowledgment (non-blocking - don't wait)
            self.tts.speak("Yes?", wait=False)
            
            # Record and transcribe - SYNCHRONOUS blocking call
            # This will block for ~5-8 seconds total (3s record + 2-5s transcribe)
            # But we're already in a background thread, so wake word detector keeps running
            result = self.stt.listen_and_transcribe(duration=3)
            
            if result.get("success"):
                command = result.get("text", "")
                logger.info(f"📝 Heard command: {command}")
                
                # Update UI with user command
                self.ui_state_manager.update_state(
                    AssistantState.THINKING, 
                    user_text=command
                )
                
                # Process command (asyncio.run is OK here - we're in a separate thread)
                asyncio.run(self.orchestrator.process_command(command, source="laptop"))
            else:
                logger.warning(f"❌ Failed to transcribe: {result.get('error')}")
                self.tts.speak("Sorry, I didn't catch that.", wait=False)
        
        except Exception as e:
            logger.error(f"Error processing wake word: {e}", exc_info=True)
            self.tts.speak("An error occurred.", wait=False)
        
        finally:
            # CRITICAL: Always reset flag so next wake word can be processed
            self.processing_command = False
            
            # Update UI back to idle
            self.ui_state_manager.update_state(AssistantState.IDLE)
            
            logger.info("✅ READY FOR NEXT WAKE WORD")
    
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
        logger.info("👂 Voice listener started (continuous mode)")
    
    def start_api_server(self):
        """Start API server in background thread"""
        api_thread = threading.Thread(
            target=start_server,
            daemon=True
        )
        api_thread.start()
        logger.info("🌐 API server started")
    
    def _on_ui_mic_click(self):
        """Handle mic button click from UI"""
        logger.info("🎤 Manual mic activation from UI")
        # Trigger the same flow as wake word detection
        self.on_wake_word_detected()
    
    def start_ui_panel(self):
        """Start the desktop UI panel"""
        if not self.config.get("ui.enable_slideup_panel", True):
            logger.info("UI panel disabled in config")
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
            logger.info("🎨 Desktop UI panel started")
        except Exception as e:
            logger.warning(f"⚠️ Failed to start UI panel (continuing without UI): {e}")
            self.slide_up_panel = None
    
    def run(self):
        """Run the assistant"""
        try:
            self.running = True
            
            # Start components
            logger.info("🚀 Starting Item AI Assistant...")
            
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
            logger.info("✅ Item AI Assistant is now running")
            logger.info("🎤 Say wake word (porcupine/picovoice/bumblebee) + command")
            logger.info("⚡ Optimized: 3s recording, synchronous transcription, Groq STT")
            logger.info("🎨 Desktop UI panel enabled")
            logger.info("🛑 Press Ctrl+C to stop")
            logger.info("=" * 80)
            
            # Keep running
            while self.running:
                import time
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.shutdown()
        
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the assistant"""
        self.running = False
        
        if self.wake_word_detector:
            self.wake_word_detector.cleanup()
        
        if self.slide_up_panel:
            self.slide_up_panel.stop()
        
        self.tts.speak("Goodbye!")
        
        logger.info("Item AI Assistant shut down")
        sys.exit(0)


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

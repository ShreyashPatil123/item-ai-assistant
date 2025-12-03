"""
Wake Word Detection - CONTINUOUS MODE
Listens for wake words using Picovoice Porcupine.
FIXED: Continuous listening without stopping after detection
"""

import struct
import pyaudio
import pvporcupine
from typing import Optional, Callable

from item_assistant.config import get_config
from item_assistant.logging import get_logger

logger = get_logger()


class WakeWordDetector:
    """Detects wake word using Porcupine - CONTINUOUS MODE"""
    
    def __init__(self, on_wake_word: Optional[Callable] = None):
        """
        Initialize wake word detector
        
        Args:
            on_wake_word: Callback function when wake word detected
        """
        self.config = get_config()
        self.on_wake_word = on_wake_word
        
        # Get configuration
        self.enabled = self.config.get("voice.wake_word.enabled", True)
        self.wake_word = self.config.get("voice.wake_word.word", "Item")
        self.sensitivity = 0.9  # MAXIMUM for reliability
        self.access_key = self.config.get("voice.wake_word.access_key", "")
        
        # Porcupine instance
        self.porcupine = None
        self.audio_stream = None
        self.pa = None
        self.is_listening = False
        
        if self.enabled and self.access_key:
            self._initialize_porcupine()
        else:
            logger.warning("Wake word detection disabled or access key missing")
    
    def _initialize_porcupine(self):
        """Initialize Porcupine engine"""
        try:
            keywords = ['porcupine', 'picovoice', 'bumblebee']
            sensitivity = 0.9  # MAXIMUM
            
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=keywords,
                sensitivities=[sensitivity] * len(keywords)
            )
            
            logger.info(f"✅ Wake word detector initialized - CONTINUOUS MODE")
            logger.info(f"🎤 Keywords: {', '.join(keywords)} (sensitivity: 0.9)")
        
        except Exception as e:
            logger.error(f"❌ Failed to initialize Porcupine: {e}")
            self.porcupine = None
    
    def start_listening(self):
        """Start listening for wake word - CONTINUOUS MODE"""
        if not self.porcupine:
            logger.error("❌ Porcupine not initialized")
            return
        
        if self.is_listening:
            logger.warning("⚠️ Already listening")
            return
        
        try:
            # Initialize PyAudio
            self.pa = pyaudio.PyAudio()
            
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            
            self.is_listening = True
            logger.info("👂 CONTINUOUS LISTENING MODE ACTIVE")
            
            # CONTINUOUS LISTEN LOOP - Never stops except on error
            frame_count = 0
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
                        logger.debug(f"🎤 Audio frame processed (frame #{frame_count})")
                    
                    if keyword_index >= 0:
                        keywords = ['porcupine', 'picovoice', 'bumblebee']
                        detected_word = keywords[keyword_index] if keyword_index < len(keywords) else "unknown"
                        logger.info(f"🎯 WAKE DETECTED: '{detected_word}' (frame #{frame_count})")
                        
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
        
        except Exception as e:
            logger.error(f"❌ Fatal error in wake word detection: {e}")
        
        finally:
            self.stop_listening()
    
    def stop_listening(self):
        """Stop listening for wake word"""
        self.is_listening = False
        
        if self.audio_stream:
            try:
                self.audio_stream.close()
            except:
                pass
            self.audio_stream = None
        
        if self.pa:
            try:
                self.pa.terminate()
            except:
                pass
            self.pa = None
        
        logger.info("🛑 Stopped listening")
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_listening()
        
        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None


# Global wake word detector instance
_wake_word_detector_instance = None


def get_wake_word_detector(on_wake_word: Optional[Callable] = None) -> WakeWordDetector:
    """Get the global wake word detector instance"""
    global _wake_word_detector_instance
    if _wake_word_detector_instance is None:
        _wake_word_detector_instance = WakeWordDetector(on_wake_word)
    return _wake_word_detector_instance

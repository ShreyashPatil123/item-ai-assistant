"""
Text-to-Speech (TTS)
Converts text to speech using pyttsx3 for offline multi-language support.
"""

import pyttsx3
from typing import Optional

from item_assistant.config import get_config
from item_assistant.logging import get_logger

logger = get_logger()


class TTS:
    """Text-to-speech engine"""
    
    def __init__(self):
        """Initialize TTS"""
        self.config = get_config()
        
        # Get configuration
        self.enabled = self.config.get("voice.tts.enabled", True)
        self.voice_id = self.config.get("voice.tts.voice_id", 0)
        self.rate = self.config.get("voice.tts.rate", 175)
        self.volume = self.config.get("voice.tts.volume", 0.9)
        self.language = self.config.get("voice.tts.language", "en")
        
        # Initialize pyttsx3 engine
        self.engine = None
        if self.enabled:
            self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize pyttsx3 engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Set properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            
            if voices and len(voices) > self.voice_id:
                self.engine.setProperty('voice', voices[self.voice_id].id)
                logger.info(f"TTS initialized with voice: {voices[self.voice_id].name}")
            else:
                logger.warning(f"Voice ID {self.voice_id} not found, using default")
            
            logger.info(f"TTS engine initialized (rate: {self.rate}, volume: {self.volume})")
        
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.engine = None
    
    def list_voices(self):
        """List available voices"""
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            voice_list = []
            for i, voice in enumerate(voices):
                voice_list.append({
                    "id": i,
                    "name": voice.name,
                    "languages": voice.languages,
                    "gender": getattr(voice, 'gender', 'unknown')
                })
            return voice_list
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []
    
    def speak(self, text: str, wait: bool = True):
        """
        Speak text
        
        Args:
            text: Text to speak
            wait: Wait for speech to complete
        """
        if not self.engine or not self.enabled:
            logger.warning("TTS not enabled or initialized")
            return
        
        try:
            logger.info(f"Speaking: '{text}'")
            self.engine.say(text)
            
            if wait:
                self.engine.runAndWait()
        
        except Exception as e:
            logger.error(f"TTS speaking failed: {e}")
    
    def speak_async(self, text: str):
        """
        Speak text asynchronously (non-blocking)
        
        Args:
            text: Text to speak
        """
        self.speak(text, wait=False)
    
    def stop(self):
        """Stop current speech"""
        if self.engine:
            try:
                self.engine.stop()
            except Exception as e:
                logger.error(f"Failed to stop TTS: {e}")
    
    def set_rate(self, rate: int):
        """
        Set speech rate
        
        Args:
            rate: Speech rate (words per minute)
        """
        if self.engine:
            self.engine.setProperty('rate', rate)
            self.rate = rate
            logger.info(f"TTS rate set to {rate}")
    
    def set_volume(self, volume: float):
        """
        Set volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.engine:
            volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', volume)
            self.volume = volume
            logger.info(f"TTS volume set to {volume}")
    
    def set_voice(self, voice_id: int):
        """
        Set voice
        
        Args:
            voice_id: Voice ID from list_voices()
        """
        if not self.engine:
            return
        
        try:
            voices = self.engine.getProperty('voices')
            if voice_id < len(voices):
                self.engine.setProperty('voice', voices[voice_id].id)
                self.voice_id = voice_id
                logger.info(f"TTS voice changed to: {voices[voice_id].name}")
        except Exception as e:
            logger.error(f"Failed to set voice: {e}")


# Global TTS instance
_tts_instance = None


def get_tts() -> TTS:
    """Get the global TTS instance"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTS()
    return _tts_instance

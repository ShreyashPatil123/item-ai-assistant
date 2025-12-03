"""
Speech-to-Text (STT)
OPTIMIZED FOR SPEED - 3s recording, synchronous blocking, Groq-first
"""

import io
import threading
import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper
from typing import Optional, Dict
from groq import Groq

from item_assistant.config import get_config
from item_assistant.logging import get_logger

logger = get_logger()


class STT:
    """Speech-to-text engine - OPTIMIZED"""
    
    def __init__(self):
        """Initialize STT"""
        self.config = get_config()
        
        # FORCE ONLINE FOR SPEED - Groq is 10x faster than local Whisper
        self.prefer_online = True  # Always use Groq for best latency
        self.offline_model_size = self.config.get("voice.stt.offline_model", "base")
        self.online_provider = "groq"
        self.languages = self.config.get("voice.stt.languages", ["hi", "en", "mr"])
        
        # Initialize offline Whisper model (fallback only)
        self.whisper_model = None
        # Skip loading Whisper to save memory - only load if Groq fails
        
        # Initialize Groq client (primary)
        self.groq_client = None
        api_key = self.config.get("llm.online.groq.api_key")
        if api_key:
            try:
                self.groq_client = Groq(api_key=api_key)
                logger.info("✅ Groq STT client initialized (FAST MODE)")
            except Exception as e:
                logger.error(f"Failed to initialize Groq STT: {e}")
                self._load_whisper_model()  # Load fallback
        else:
            logger.warning("No Groq API key - loading Whisper fallback")
            self._load_whisper_model()
        
        logger.info(f"STT initialized - OPTIMIZED (prefer: Groq)")
    
    def _load_whisper_model(self):
        """Load Whisper model for offline STT (fallback)"""
        if self.whisper_model:
            return  # Already loaded
        try:
            logger.info(f"Loading Whisper model: {self.offline_model_size}")
            self.whisper_model = whisper.load_model(self.offline_model_size)
            logger.info("Whisper model loaded")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.whisper_model = None
    
    def record_audio(self, duration: int = 3, sample_rate: int = 16000) -> np.ndarray:
        """
        Record audio from microphone - OPTIMIZED: 3 seconds default
        
        Args:
            duration: Recording duration (3s for faster response)
            sample_rate: Sample rate in Hz
        
        Returns:
            Audio data as numpy array
        """
        logger.info(f"🎤 Recording ({duration}s)...")
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        logger.info("✅ Recording done")
        return audio.flatten()
    
    def transcribe_offline(self, audio: np.ndarray, language: Optional[str] = None) -> Dict:
        """Transcribe using offline Whisper (SLOW - fallback only)"""
        if not self.whisper_model:
            self._load_whisper_model()  # Lazy load if needed
        
        if not self.whisper_model:
            return {
                "success": False,
                "error": "Whisper model not loaded",
                "text": ""
            }
        
        try:
            result = self.whisper_model.transcribe(
                audio,
                language=language,
                fp16=False
            )
            
            text = result.get("text", "").strip()
            detected_language = result.get("language", "unknown")
            
            logger.info(f"Offline STT: '{text}' (lang: {detected_language})")
            
            return {
                "success": True,
                "text": text,
                "language": detected_language,
                "provider": "whisper-offline"
            }
        
        except Exception as e:
            logger.error(f"Offline STT failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def transcribe_online(self, audio: np.ndarray, language: Optional[str] = None) -> Dict:
        """Transcribe using Groq (FAST - primary method)"""
        if not self.groq_client:
            return {
                "success": False,
                "error": "Groq STT not available",
                "text": ""
            }
        
        try:
            # Convert to WAV format in memory
            audio_bytes = io.BytesIO()
            sf.write(audio_bytes, audio, 16000, format='WAV')
            audio_bytes.seek(0)
            audio_bytes.name = "audio.wav"
            
            # Transcribe using Groq Whisper (VERY FAST)
            transcription = self.groq_client.audio.transcriptions.create(
                file=audio_bytes,
                model="whisper-large-v3",
                language=language,
                response_format="text"  # Faster than JSON
            )
            
            text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
            
            logger.info(f"⚡ Groq STT: '{text}'")
            
            return {
                "success": True,
                "text": text,
                "language": language or "auto",
                "provider": "groq-whisper"
            }
        
        except Exception as e:
            logger.error(f"Groq STT failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None,
                  force_offline: bool = False) -> Dict:
        """
        Transcribe audio - OPTIMIZED: Groq first, fallback to Whisper
        
        Returns:
            Dictionary with transcription
        """
        # Always try Groq first unless forced offline
        if not force_offline and self.groq_client:
            result = self.transcribe_online(audio, language)
            
            # Fallback to offline only if Groq completely fails
            if not result.get("success") and self.whisper_model:
                logger.warning("⚠️ Groq failed, falling back to offline")
                result = self.transcribe_offline(audio, language)
        else:
            result = self.transcribe_offline(audio, language)
        
        return result
    
    def listen_and_transcribe(self, duration: int = 3, language: Optional[str] = None) -> Dict:
        """
        Record and transcribe - SYNCHRONOUS (blocking)
        
        This method blocks for the duration of recording + transcription time.
        It's designed to be called from a background thread (command handler),
        so blocking here won't affect the wake word detector's continuous listening.
        
        Args:
            duration: Recording duration (3s for speed)
            language: Language code
        
        Returns:
            Dictionary with transcription result
        """
        try:
            logger.info(f"🎤 Recording ({duration}s)...")
            audio = self.record_audio(duration)  # Blocks for 'duration' seconds
            logger.info("✅ Recording done, transcribing...")
            
            result = self.transcribe(audio, language)  # Blocks for 2-5 seconds (Groq API)
            logger.info(f"🎯 Transcription complete: {result.get('text', '')}")
            return result
            
        except Exception as e:
            logger.error(f"Error in transcription: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }


# Global STT instance
_stt_instance = None


def get_stt() -> STT:
    """Get the global STT instance"""
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = STT()
    return _stt_instance

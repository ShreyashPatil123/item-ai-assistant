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
                logger.info("[STT] Groq STT client initialized (FAST MODE)")
                # Verify Groq connection at startup
                self._verify_groq_connection()
            except Exception as e:
                logger.error(f"[STT_ERROR] Failed to initialize Groq STT: {e}")
                self._load_whisper_model()  # Load fallback
        else:
            logger.warning("[STT_WARN] No Groq API key - loading Whisper fallback")
            self._load_whisper_model()
        
        logger.info(f"[STT] STT initialized - OPTIMIZED (prefer: Groq)")
    
    def _verify_groq_connection(self):
        """Verify Groq API connection at startup"""
        try:
            logger.info("[STT] Verifying Groq API connection...")
            # Try a simple test call
            import io
            import soundfile as sf
            # Create a tiny test audio
            test_audio = np.zeros(16000, dtype=np.float32)  # 1 second of silence
            audio_bytes = io.BytesIO()
            sf.write(audio_bytes, test_audio, 16000, format='WAV')
            audio_bytes.seek(0)
            audio_bytes.name = "test.wav"
            
            # Test the connection
            self.groq_client.audio.transcriptions.create(
                file=audio_bytes,
                model="whisper-large-v3",
                response_format="text"
            )
            logger.info("[STT] Groq API: Connected and working")
        except Exception as e:
            logger.warning(f"[STT_WARN] Groq API test failed: {e}")
    
    def _load_whisper_model(self):
        """Load Whisper model for offline STT (fallback)"""
        if self.whisper_model:
            return  # Already loaded
        try:
            logger.info("[STT] Loading Whisper model: {self.offline_model_size}")
            self.whisper_model = whisper.load_model(self.offline_model_size)
            logger.info("[STT] Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"[STT_ERROR] Failed to load Whisper model: {e}")
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
        logger.info(f"[STT] Starting audio capture ({duration}s at {sample_rate}Hz)...")
        try:
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            audio_flat = audio.flatten()
            logger.info(f"[STT] Audio captured: {len(audio_flat)} samples ({len(audio_flat)/sample_rate:.2f}s)")
            return audio_flat
        except Exception as e:
            logger.error(f"[STT_ERROR] Failed to record audio: {e}", exc_info=True)
            raise
    
    def transcribe_offline(self, audio: np.ndarray, language: Optional[str] = None) -> Dict:
        """Transcribe using offline Whisper (SLOW - fallback only)"""
        logger.info("[STT] Attempting offline transcription with Whisper...")
        if not self.whisper_model:
            self._load_whisper_model()  # Lazy load if needed
        
        if not self.whisper_model:
            logger.error("[STT_ERROR] Whisper model not loaded")
            return {
                "success": False,
                "error": "Whisper model not loaded",
                "text": ""
            }
        
        try:
            logger.info(f"[STT] Transcribing with Whisper (language: {language or 'auto'})...")
            result = self.whisper_model.transcribe(
                audio,
                language=language,
                fp16=False
            )
            
            text = result.get("text", "").strip()
            detected_language = result.get("language", "unknown")
            
            logger.info(f"[STT] Whisper result: '{text}' (lang: {detected_language})")
            
            return {
                "success": True,
                "text": text,
                "language": detected_language,
                "provider": "whisper-offline"
            }
        
        except Exception as e:
            logger.error(f"[STT_ERROR] Offline transcription failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def transcribe_online(self, audio: np.ndarray, language: Optional[str] = None) -> Dict:
        """Transcribe using Groq (FAST - primary method)"""
        logger.info("[STT] Attempting online transcription with Groq...")
        if not self.groq_client:
            logger.error("[STT_ERROR] Groq client not available")
            return {
                "success": False,
                "error": "Groq STT not available",
                "text": ""
            }
        
        try:
            # Convert to WAV format in memory
            logger.info("[STT] Converting audio to WAV format...")
            audio_bytes = io.BytesIO()
            sf.write(audio_bytes, audio, 16000, format='WAV')
            audio_bytes.seek(0)
            audio_bytes.name = "audio.wav"
            logger.info(f"[STT] WAV file created: {audio_bytes.getbuffer().nbytes} bytes")
            
            # Transcribe using Groq Whisper (VERY FAST)
            logger.info("[STT] Sending to Groq API (whisper-large-v3)...")
            transcription = self.groq_client.audio.transcriptions.create(
                file=audio_bytes,
                model="whisper-large-v3",
                language=language,
                response_format="text"  # Faster than JSON
            )
            
            text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
            logger.info(f"[STT] Groq response received: '{text}'")
            
            return {
                "success": True,
                "text": text,
                "language": language or "auto",
                "provider": "groq-whisper"
            }
        
        except Exception as e:
            logger.error(f"[STT_ERROR] Groq transcription failed: {e}", exc_info=True)
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
        logger.info("[STT] Starting transcription process...")
        # Always try Groq first unless forced offline
        if not force_offline and self.groq_client:
            logger.info("[STT] Trying Groq first...")
            result = self.transcribe_online(audio, language)
            
            # Fallback to offline only if Groq completely fails
            if not result.get("success"):
                logger.warning("[STT_WARN] Groq failed, falling back to offline Whisper...")
                result = self.transcribe_offline(audio, language)
        else:
            logger.info("[STT] Using offline Whisper (forced or Groq unavailable)...")
            result = self.transcribe_offline(audio, language)
        
        logger.info(f"[STT] Transcription complete: success={result.get('success')}, provider={result.get('provider')}")
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
            logger.info(f"[STT] Starting listen_and_transcribe (duration={duration}s)...")
            
            # Step 1: Record audio
            audio = self.record_audio(duration)  # Blocks for 'duration' seconds
            if audio is None or len(audio) == 0:
                logger.error("[STT_ERROR] No audio recorded")
                return {
                    "success": False,
                    "error": "No audio recorded",
                    "text": ""
                }
            
            # Step 2: Transcribe
            logger.info("[STT] Recording complete, starting transcription...")
            result = self.transcribe(audio, language)  # Blocks for 2-5 seconds (Groq API)
            
            # Step 3: Log result
            if result.get("success"):
                logger.info(f"[STT] Transcription successful: '{result.get('text', '')}'")
            else:
                logger.error(f"[STT_ERROR] Transcription failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"[STT_ERROR] Critical error in listen_and_transcribe: {e}", exc_info=True)
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

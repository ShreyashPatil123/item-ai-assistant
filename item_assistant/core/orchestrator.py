"""
Orchestrator
Main coordination logic for the Item AI Assistant.
"""

import time
from typing import Dict, Optional
from datetime import datetime

from item_assistant.config import get_config
from item_assistant.logging import get_logger, get_log_manager
from item_assistant.llm import get_intent_parser, get_local_llm, get_online_llm
from item_assistant.voice import get_tts
from item_assistant.core.action_executor import get_action_executor

logger = get_logger()
log_manager = get_log_manager()


class Orchestrator:
    """Main orchestrator for Item AI Assistant"""
    
    def __init__(self):
        """Initialize orchestrator"""
        self.config = get_config()
        self.intent_parser = get_intent_parser()
        self.action_executor = get_action_executor()
        self.tts = get_tts()
        
        self.start_time = time.time()
        
        logger.info("Orchestrator initialized")
    
    async def process_command(self, command: str, source: str = "laptop") -> Dict:
        """
        Process a user command
        
        Args:
            command: User command text
            source: Source of command ("laptop", "phone", "api")
        
        Returns:
            Result dictionary
        """
        logger.info(f"Processing command from {source}: {command}")
        log_manager.log_command(command, source)
        
        try:
            # Step 1: Parse intent
            intent = self.intent_parser.parse(command)
            
            if intent.get("intent") == "unknown":
                message = "Sorry, I didn't understand that command."
                self._respond(message, source)
                return {
                    "success": False,
                    "message": message
                }
            
            # Step 2: Execute action
            result = await self.action_executor.execute(intent)
            
            # Step 3: Respond
            message = result.get("message", "Command completed")
            self._respond(message, source)
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing command: {e}", exc_info=True)
            message = f"Sorry, an error occurred: {str(e)}"
            self._respond(message, source)
            
            return {
                "success": False,
                "message": message,
                "error": str(e)
            }
    
    def _respond(self, message: str, source: str):
        """
        Send response to user
        
        Args:
            message: Response message
            source: Original command source
        """
        # If command was from laptop (voice), speak response (non-blocking)
        if source == "laptop" and self.tts.enabled:
            self.tts.speak(message, wait=False)  # ✅ Non-blocking!
        
        # For API/phone, response is sent via API (no TTS needed)
        logger.info(f"Response: {message}")
    
    def get_status(self) -> Dict:
        """
        Get system status
        
        Returns:
            Status dictionary
        """
        uptime = time.time() - self.start_time
        
        # Check LLM availability
        local_llm = get_local_llm()
        online_llm = get_online_llm()
        
        return {
            "uptime": uptime,
            "voice_enabled": self.tts.enabled,
            "llm_available": {
                "local": local_llm.is_available(),
                "online": online_llm.is_available()
            },
            "timestamp": datetime.now().isoformat()
        }


# Global orchestrator instance
_orchestrator_instance = None


def get_orchestrator() -> Orchestrator:
    """Get the global orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance

"""
Intent Parser
Converts natural language commands to structured intents.
"""

import re
import json
from typing import Dict, Optional, List

from item_assistant.config import get_config
from item_assistant.logging import get_logger
from item_assistant.llm.llm_router import get_llm_router

logger = get_logger()


class IntentParser:
    """Parses natural language into structured intents"""
    
    def __init__(self):
        """Initialize intent parser"""
        self.config = get_config()
        self.llm_router = get_llm_router()
        logger.info("Intent parser initialized")
    
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
                intent_data["raw_command"] = command
                logger.info(f"[INTENT] Parsed intent: {intent_data.get('intent')} (confidence: {intent_data.get('confidence')})")
                return intent_data
            else:
                logger.warning(f"[INTENT] No JSON found in LLM response, using fallback")
                return self._fallback_parse(command)
        
        except json.JSONDecodeError as e:
            logger.warning(f"[INTENT] JSON parsing failed: {e}, using fallback")
            return self._fallback_parse(command)
    
    def _fallback_parse(self, command: str) -> Dict:
        """
        Fallback rule-based parsing when LLM fails
        Uses comprehensive keyword mapping for all supported intents
        
        Args:
            command: User command
        
        Returns:
            Parsed intent dict
        """
        command_lower = command.lower().strip()
        logger.info(f"[INTENT] Fallback parsing: '{command}'")
        
        # Comprehensive keyword mappings for all intents
        
        # OPEN/LAUNCH/START APP
        if re.search(r'\b(open|launch|start|run)\b', command_lower):
            app_name = re.sub(r'\b(open|launch|start|run)\s+', '', command_lower).strip()
            logger.info(f"[INTENT] Matched: open_app (app: {app_name})")
            return {
                "intent": "open_app",
                "entities": {"app_name": app_name},
                "confidence": 0.85,
                "raw_command": command,
                "fallback": True
            }
        
        # CLOSE/QUIT/EXIT APP
        if re.search(r'\b(close|quit|exit|shut down|kill)\b', command_lower):
            app_name = re.sub(r'\b(close|quit|exit|shut down|kill)\s+', '', command_lower).strip()
            logger.info(f"[INTENT] Matched: close_app (app: {app_name})")
            return {
                "intent": "close_app",
                "entities": {"app_name": app_name},
                "confidence": 0.85,
                "raw_command": command,
                "fallback": True
            }
        
        # SEARCH WEB
        if re.search(r'\b(search|google|look up|find|look for)\b', command_lower):
            query = re.sub(r'\b(search|google|look up|find|look for)\s+(for\s+)?', '', command_lower).strip()
            logger.info(f"[INTENT] Matched: search_web (query: {query})")
            return {
                "intent": "search_web",
                "entities": {"query": query},
                "confidence": 0.85,
                "raw_command": command,
                "fallback": True
            }
        
        # GET TIME
        if re.search(r'\b(what time|tell me the time|current time|what\'s the time|time is it)\b', command_lower):
            logger.info("[INTENT] Matched: get_time")
            return {
                "intent": "get_time",
                "entities": {},
                "confidence": 0.95,
                "raw_command": command,
                "fallback": True
            }
        
        # OPEN URL / VISIT
        if re.search(r'\b(open url|visit|go to|navigate to)\b', command_lower):
            url = re.sub(r'\b(open url|visit|go to|navigate to)\s+', '', command_lower).strip()
            logger.info(f"[INTENT] Matched: open_url (url: {url})")
            return {
                "intent": "open_url",
                "entities": {"url": url},
                "confidence": 0.8,
                "raw_command": command,
                "fallback": True
            }
        
        # LOCK COMPUTER
        if re.search(r'\b(lock|lock computer|lock screen)\b', command_lower):
            logger.info("[INTENT] Matched: system_lock")
            return {
                "intent": "system_lock",
                "entities": {},
                "confidence": 0.9,
                "raw_command": command,
                "fallback": True
            }
        
        # SHUTDOWN / TURN OFF
        if re.search(r'\b(shutdown|shut down|turn off|power off|restart|reboot)\b', command_lower):
            action = "restart" if "restart" in command_lower or "reboot" in command_lower else "shutdown"
            logger.info(f"[INTENT] Matched: system_shutdown (action: {action})")
            return {
                "intent": "system_shutdown",
                "entities": {"action": action},
                "confidence": 0.9,
                "raw_command": command,
                "fallback": True
            }
        
        # MUTE / UNMUTE VOLUME
        if re.search(r'\b(mute|unmute|silence|quiet)\b', command_lower):
            action = "unmute" if "unmute" in command_lower else "mute"
            logger.info(f"[INTENT] Matched: volume_control (action: {action})")
            return {
                "intent": "volume_control",
                "entities": {"action": action},
                "confidence": 0.85,
                "raw_command": command,
                "fallback": True
            }
        
        # YOUTUBE
        if re.search(r'\b(youtube|youtube\.com)\b', command_lower):
            logger.info("[INTENT] Matched: navigate_youtube")
            return {
                "intent": "navigate_youtube",
                "entities": {},
                "confidence": 0.8,
                "raw_command": command,
                "fallback": True
            }
        
        # TYPE TEXT
        if re.search(r'\b(type|write|enter)\b', command_lower):
            text = re.sub(r'\b(type|write|enter)\s+', '', command_lower).strip()
            logger.info(f"[INTENT] Matched: type_text (text: {text})")
            return {
                "intent": "type_text",
                "entities": {"text": text},
                "confidence": 0.75,
                "raw_command": command,
                "fallback": True
            }
        
        # CLICK
        if re.search(r'\b(click|press)\b', command_lower):
            target = re.sub(r'\b(click|press)\s+(on\s+)?', '', command_lower).strip()
            logger.info(f"[INTENT] Matched: click (target: {target})")
            return {
                "intent": "click",
                "entities": {"target": target},
                "confidence": 0.7,
                "raw_command": command,
                "fallback": True
            }
        
        # GENERATE CODE
        if re.search(r'\b(generate|write|create)\s+(code|script|program)\b', command_lower):
            logger.info("[INTENT] Matched: generate_code")
            return {
                "intent": "generate_code",
                "entities": {"prompt": command},
                "confidence": 0.75,
                "raw_command": command,
                "fallback": True
            }
        
        # EXPLAIN CODE
        if re.search(r'\b(explain|understand|what does|how does)\b.*\b(code|script|function)\b', command_lower):
            logger.info("[INTENT] Matched: explain_code")
            return {
                "intent": "explain_code",
                "entities": {"prompt": command},
                "confidence": 0.7,
                "raw_command": command,
                "fallback": True
            }
        
        # GET WEATHER
        if re.search(r'\b(weather|temperature|forecast|rain|snow)\b', command_lower):
            logger.info("[INTENT] Matched: get_weather")
            return {
                "intent": "get_weather",
                "entities": {},
                "confidence": 0.8,
                "raw_command": command,
                "fallback": True
            }
        
        # Default to general query
        logger.info("[INTENT] No specific match, using general_query")
        return {
            "intent": "general_query",
            "entities": {"query": command},
            "confidence": 0.5,
            "raw_command": command,
            "fallback": True
        }


# Global intent parser instance
_intent_parser_instance = None


def get_intent_parser() -> IntentParser:
    """Get the global intent parser instance"""
    global _intent_parser_instance
    if _intent_parser_instance is None:
        _intent_parser_instance = IntentParser()
    return _intent_parser_instance

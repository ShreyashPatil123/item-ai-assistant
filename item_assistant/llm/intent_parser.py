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
        
        result = self.llm_router.generate(
            prompt,
            system=system_prompt,
            task_type="intent_parsing",
            max_tokens=256,
            temperature=0.3,
            force_local=True  # Always use local for quick parsing
        )
        
        if not result.get("success"):
            logger.error(f"Intent parsing failed: {result.get('error')}")
            return {
                "intent": "unknown",
                "entities": {},
                "confidence": 0.0,
                "raw_command": command
            }
        
        # Extract JSON from response
        try:
            response_text = result.get("text", "")
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                intent_data = json.loads(json_match.group())
                intent_data["raw_command"] = command
                return intent_data
            else:
                logger.warning(f"No JSON found in LLM response: {response_text}")
                return self._fallback_parse(command)
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent JSON: {e}")
            return self._fallback_parse(command)
    
    def _fallback_parse(self, command: str) -> Dict:
        """
        Fallback rule-based parsing when LLM fails
        
        Args:
            command: User command
        
        Returns:
            Parsed intent dict
        """
        command_lower = command.lower().strip()
        
        # Rule-based patterns
        if command_lower.startswith(("open ", "launch ", "start ")):
            app_name = re.sub(r'^(open|launch|start)\s+', '', command_lower)
            return {
                "intent": "open_app",
                "entities": {"app_name": app_name},
                "confidence": 0.7,
                "raw_command": command,
                "fallback": True
            }
        
        if command_lower.startswith(("close ", "quit ", "exit ")):
            app_name = re.sub(r'^(close|quit|exit)\s+', '', command_lower)
            return {
                "intent": "close_app",
                "entities": {"app_name": app_name},
                "confidence": 0.7,
                "raw_command": command,
                "fallback": True
            }
        
        if command_lower.startswith(("search ", "google ", "look up ")):
            query = re.sub(r'^(search|google|look up|search for)\s+', '', command_lower)
            return {
                "intent": "search_web",
                "entities": {"query": query},
                "confidence": 0.7,
                "raw_command": command,
                "fallback": True
            }
        
        if "youtube" in command_lower:
            return {
                "intent": "navigate_youtube",
                "entities": {},
                "confidence": 0.6,
                "raw_command": command,
                "fallback": True
            }
        
        if command_lower in ["what time is it", "time", "what's the time"]:
            return {
                "intent": "get_time",
                "entities": {},
                "confidence": 0.9,
                "raw_command": command,
                "fallback": True
            }
        
        # Default to general query
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

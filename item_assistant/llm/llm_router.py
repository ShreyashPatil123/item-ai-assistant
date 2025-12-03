"""
LLM Router
Smart routing between local and online LLMs based on task complexity and internet availability.
"""

import requests
from typing import Dict, Optional, List

from item_assistant.config import get_config
from item_assistant.logging import get_logger
from item_assistant.llm.local_llm import get_local_llm
from item_assistant.llm.online_llm import get_online_llm

logger = get_logger()


class LLMRouter:
    """Routes requests to appropriate LLM (local vs online)"""
    
    def __init__(self):
        """Initialize LLM router"""
        self.config = get_config()
        self.local_llm = get_local_llm()
        self.online_llm = get_online_llm()
        
        # Get routing configuration
        self.default_mode = self.config.get("llm.routing.default_mode", "auto")
        self.online_tasks = self.config.get("llm.routing.use_online_for", [])
        self.local_tasks = self.config.get("llm.routing.use_local_for", [])
        
        logger.info(f"LLM Router initialized (default mode: {self.default_mode})")
    
    def is_internet_available(self) -> bool:
        """
        Check if internet is available
        
        Returns:
            True if internet is available
        """
        try:
            # Try to reach a reliable endpoint
            requests.get("https://www.google.com", timeout=3)
            return True
        except:
            return False
    
    def should_use_online(self, task_type: Optional[str] = None,
                         prompt_length: int = 0) -> bool:
        """
        Determine whether to use online LLM
        
        Args:
            task_type: Type of task (e.g., "complex_code", "quick_command")
            prompt_length: Length of prompt in characters
        
        Returns:
            True if online LLM should be used
        """
        # If default mode is local, use local
        if self.default_mode == "local":
            return False
        
        # If default mode is online, use online (if available)
        if self.default_mode == "online":
            return self.is_internet_available() and self.online_llm.is_available()
        
        # Auto mode - smart routing
        
        # No internet = always local
        if not self.is_internet_available():
            logger.info("No internet available, using local LLM")
            return False
        
        # Online LLM not configured = always local
        if not self.online_llm.is_available():
            logger.info("Online LLM not available, using local LLM")
            return False
        
        # Check task type
        if task_type:
            if task_type in self.online_tasks:
                logger.info(f"Task '{task_type}' configured for online LLM")
                return True
            
            if task_type in self.local_tasks:
                logger.info(f"Task '{task_type}' configured for local LLM")
                return False
        
        # Check prompt length (long prompts -> online for better context)
        if prompt_length > 2000:
            logger.info(f"Long prompt ({prompt_length} chars), using online LLM")
            return True
        
        # Default to local for quick tasks
        logger.info("Using local LLM for quick task")
        return False
    
    def generate(self, prompt: str, task_type: Optional[str] = None,
                system: Optional[str] = None, max_tokens: int = 2048,
                temperature: float = 0.7, force_local: bool = False,
                force_online: bool = False) -> Dict:
        """
        Generate text using appropriate LLM
        
        Args:
            prompt: User prompt
            task_type: Type of task (for routing decision)
            system: System prompt
            max_tokens: Max output tokens
            temperature: Sampling temperature
            force_local: Force local LLM usage
            force_online: Force online LLM usage
        
        Returns:
            Dictionary with generated text and metadata
        """
        # Determine which LLM to use
        use_online = False
        
        if force_online:
            use_online = True
        elif force_local:
            use_online = False
        else:
            use_online = self.should_use_online(task_type, len(prompt))
        
        # Try selected LLM
        if use_online:
            logger.info("Using online LLM")
            result = self.online_llm.generate(prompt, system, max_tokens, temperature)
            
            # Fallback to local if online fails
            if not result.get("success"):
                logger.warning("Online LLM failed, falling back to local")
                result = self.local_llm.generate(prompt, system=system,
                                               max_tokens=max_tokens, temperature=temperature)
                if result.get("success"):
                    result["fallback"] = True
                    result["fallback_reason"] = "Online LLM API failed"
        
        else:
            logger.info("Using local LLM")
            result = self.local_llm.generate(prompt, system=system,
                                           max_tokens=max_tokens, temperature=temperature)
            
            # If local fails and online is available, fallback
            if not result.get("success") and self.online_llm.is_available():
                logger.warning("Local LLM failed, falling back to online")
                result = self.online_llm.generate(prompt, system, max_tokens, temperature)
                if result.get("success"):
                    result["fallback"] = True
                    result["fallback_reason"] = "Local LLM failed"
        
        return result
    
    def generate_code(self, prompt: str, language: Optional[str] = None,
                     max_tokens: int = 4096) -> Dict:
        """
        Generate code (automatically routed to appropriate LLM)
        
        Args:
            prompt: Code generation prompt
            language: Programming language
            max_tokens: Max output tokens
        
        Returns:
            Dictionary with generated code
        """
        # Code generation is a task type that can be complex
        # Check if it's simple or complex based on prompt
        task_type = "simple_code" if len(prompt) < 500 else "complex_code"
        
        system = "You are an expert programmer. Generate clean, efficient code."
        if language:
            system += f" The language is {language}."
        
        return self.generate(prompt, task_type=task_type, system=system,
                           max_tokens=max_tokens, temperature=0.3)
    
    def chat(self, messages: List[Dict[str, str]], task_type: Optional[str] = None,
            max_tokens: int = 2048, temperature: float = 0.7) -> Dict:
        """
        Chat with appropriate LLM
        
        Args:
            messages: Message history
            task_type: Type of task
            max_tokens: Max tokens
            temperature: Temperature
        
        Returns:
            Dictionary with response
        """
        # Calculate total prompt length
        total_length = sum(len(m['content']) for m in messages)
        
        use_online = self.should_use_online(task_type, total_length)
        
        if use_online:
            result = self.online_llm.chat(messages, max_tokens, temperature)
            if not result.get("success"):
                result = self.local_llm.chat(messages, max_tokens=max_tokens,
                                           temperature=temperature)
        else:
            result = self.local_llm.chat(messages, max_tokens=max_tokens,
                                       temperature=temperature)
            if not result.get("success") and self.online_llm.is_available():
                result = self.online_llm.chat(messages, max_tokens, temperature)
        
        return result


# Global LLM router instance
_llm_router_instance = None


def get_llm_router() -> LLMRouter:
    """Get the global LLM router instance"""
    global _llm_router_instance
    if _llm_router_instance is None:
        _llm_router_instance = LLMRouter()
    return _llm_router_instance

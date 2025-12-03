"""
Local LLM Client using Ollama
Provides access to locally-running LLM models.
"""

import requests
import json
from typing import Dict, Optional, List

from item_assistant.config import get_config
from item_assistant.logging import get_log_manager

logger = get_log_manager().get_logger()
log_manager = get_log_manager()


class LocalLLM:
    """Client for local LLM via Ollama"""
    
    def __init__(self):
        """Initialize local LLM client"""
        self.config = get_config()
        self.base_url = self.config.get("llm.local.base_url", "http://localhost:11434")
        self.timeout = self.config.get("llm.local.timeout", 60)
        
        # Get model names from config
        self.general_model = self.config.get("llm.local.models.general", "llama3.2:3b")
        self.code_model = self.config.get("llm.local.models.code", "codegemma:7b")
        
        logger.info(f"Local LLM initialized (general: {self.general_model}, code: {self.code_model})")
    
    def is_available(self) -> bool:
        """
        Check if Ollama is running and available
        
        Returns:
            True if available
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """
        List available models
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def generate(self, prompt: str, model: Optional[str] = None, 
                system: Optional[str] = None, max_tokens: int = 2048,
                temperature: float = 0.7) -> Dict:
        """
        Generate text using local LLM
        
        Args:
            prompt: User prompt
            model: Model to use (defaults to general model)
            system: System prompt (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Dictionary with generated text and metadata
        """
        model = model or self.general_model
        
        # Build request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                generated_text = data.get('response', '')
                
                log_manager.log_llm_call("local", model, len(prompt), True)
                
                return {
                    "success": True,
                    "text": generated_text,
                    "model": model,
                    "provider": "local"
                }
            else:
                log_manager.log_llm_call("local", model, len(prompt), False)
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "text": ""
                }
        
        except Exception as e:
            log_manager.log_llm_call("local", model, len(prompt), False)
            logger.error(f"Local LLM generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def generate_code(self, prompt: str, language: Optional[str] = None,
                     max_tokens: int = 4096) -> Dict:
        """
        Generate code using code-specialized model
        
        Args:
            prompt: Code generation prompt
            language: Programming language (optional)
            max_tokens: Maximum tokens
        
        Returns:
            Dictionary with generated code
        """
        system_prompt = "You are an expert programmer. Generate clean, efficient code."
        if language:
            system_prompt += f" The language is {language}."
        
        return self.generate(
            prompt=prompt,
            model=self.code_model,
            system=system_prompt,
            max_tokens=max_tokens,
            temperature=0.3  # Lower temperature for code
        )
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None,
            max_tokens: int = 2048, temperature: float = 0.7) -> Dict:
        """
        Chat with local LLM using message history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
        
        Returns:
            Dictionary with response
        """
        model = model or self.general_model
        
        # Convert messages to Ollama format
        # Extract system message if present
        system = None
        prompt_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system = msg['content']
            else:
                prompt_messages.append(msg)
        
        # Build prompt from messages
        prompt = ""
        for msg in prompt_messages:
            role = msg['role']
            content = msg['content']
            if role == 'user':
                prompt += f"User: {content}\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n"
        
        prompt += "Assistant:"
        
        return self.generate(prompt, model=model, system=system,
                           max_tokens=max_tokens, temperature=temperature)


# Global local LLM instance
_local_llm_instance = None


def get_local_llm() -> LocalLLM:
    """Get the global local LLM instance"""
    global _local_llm_instance
    if _local_llm_instance is None:
        _local_llm_instance = LocalLLM()
    return _local_llm_instance

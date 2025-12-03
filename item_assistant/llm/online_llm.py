"""
Online LLM Clients
Provides access to free-tier cloud LLM APIs (Groq, Gemini, etc.)
"""

import os
from typing import Dict, Optional, List
import google.generativeai as genai
from groq import Groq

from item_assistant.config import get_config
from item_assistant.logging import get_log_manager

logger = get_log_manager().get_logger()
log_manager = get_log_manager()


class OnlineLLM:
    """Client for online LLM APIs"""
    
    def __init__(self):
        """Initialize online LLM client"""
        self.config = get_config()
        
        # Initialize Groq
        self.groq_client = None
        self.groq_enabled = self.config.get("llm.online.groq.enabled", False)
        self.groq_model = self.config.get("llm.online.groq.model", "llama-3.3-70b-versatile")
        
        if self.groq_enabled:
            api_key = self.config.get("llm.online.groq.api_key")
            if api_key:
                try:
                    self.groq_client = Groq(api_key=api_key)
                    logger.info("Groq client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Groq: {e}")
        
        # Initialize Gemini
        self.gemini_enabled = self.config.get("llm.online.gemini.enabled", False)
        self.gemini_model = self.config.get("llm.online.gemini.model", "gemini-2.0-flash-exp")
        
        if self.gemini_enabled:
            api_key = self.config.get("llm.online.gemini.api_key")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    logger.info("Gemini client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Gemini: {e}")
        
        # Get primary and fallback providers
        self.primary = self.config.get("llm.online.primary", "groq")
        self.fallback = self.config.get("llm.online.fallback", "gemini")
    
    def is_available(self) -> bool:
        """Check if any online LLM is available"""
        return (self.groq_enabled and self.groq_client is not None) or self.gemini_enabled
    
    def _generate_groq(self, prompt: str, system: Optional[str] = None,
                      max_tokens: int = 8000, temperature: float = 0.7) -> Dict:
        """Generate using Groq API"""
        if not self.groq_client:
            return {"success": False, "error": "Groq not initialized", "text": ""}
        
        try:
            # Build messages
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            # Call Groq API
            completion = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            text = completion.choices[0].message.content
            
            log_manager.log_llm_call("groq", self.groq_model, len(prompt), True)
            
            return {
                "success": True,
                "text": text,
                "model": self.groq_model,
                "provider": "groq"
            }
        
        except Exception as e:
            log_manager.log_llm_call("groq", self.groq_model, len(prompt), False)
            logger.error(f"Groq generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def _generate_gemini(self, prompt: str, system: Optional[str] = None,
                        max_tokens: int = 8000, temperature: float = 0.7) -> Dict:
        """Generate using Gemini API"""
        if not self.gemini_enabled:
            return {"success": False, "error": "Gemini not initialized", "text": ""}
        
        try:
            # Create model
            model = genai.GenerativeModel(
                model_name=self.gemini_model,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            
            # Build full prompt
            full_prompt = prompt
            if system:
                full_prompt = f"{system}\n\n{prompt}"
            
            # Generate
            response = model.generate_content(full_prompt)
            text = response.text
            
            log_manager.log_llm_call("gemini", self.gemini_model, len(prompt), True)
            
            return {
                "success": True,
                "text": text,
                "model": self.gemini_model,
                "provider": "gemini"
            }
        
        except Exception as e:
            log_manager.log_llm_call("gemini", self.gemini_model, len(prompt), False)
            logger.error(f"Gemini generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def generate(self, prompt: str, system: Optional[str] = None,
                max_tokens: int = 8000, temperature: float = 0.7,
                use_fallback: bool = True) -> Dict:
        """
        Generate using online LLM with automatic fallback
        
        Args:
            prompt: User prompt
            system: System prompt
            max_tokens: Max output tokens
            temperature: Sampling temperature
            use_fallback: Use fallback provider on failure
        
        Returns:
            Dictionary with generated text
        """
        # Try primary provider
        result = None
        
        if self.primary == "groq":
            result = self._generate_groq(prompt, system, max_tokens, temperature)
        elif self.primary == "gemini":
            result = self._generate_gemini(prompt, system, max_tokens, temperature)
        
        # If failed and fallback is enabled, try fallback
        if use_fallback and (not result or not result.get("success")):
            logger.info(f"Primary provider failed, trying fallback: {self.fallback}")
            
            if self.fallback == "groq":
                result = self._generate_groq(prompt, system, max_tokens, temperature)
            elif self.fallback == "gemini":
                result = self._generate_gemini(prompt, system, max_tokens, temperature)
        
        return result or {"success": False, "error": "No providers available", "text": ""}
    
    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 8000,
            temperature: float = 0.7) -> Dict:
        """
        Chat with online LLM using message history
        
        Args:
            messages: List of {role, content} dicts
            max_tokens: Max output tokens
            temperature: Sampling temperature
        
        Returns:
            Dictionary with response
        """
        # Extract system message if present
        system = None
        user_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system = msg['content']
            else:
                user_messages.append(msg)
        
        # Build prompt from messages
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in user_messages])
        
        return self.generate(prompt, system=system, max_tokens=max_tokens,
                           temperature=temperature)


# Global online LLM instance
_online_llm_instance = None


def get_online_llm() -> OnlineLLM:
    """Get the global online LLM instance"""
    global _online_llm_instance
    if _online_llm_instance is None:
        _online_llm_instance = OnlineLLM()
    return _online_llm_instance

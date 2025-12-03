"""
UI State Management for Item AI Assistant
Manages assistant state and broadcasts updates to UI components.
"""

from enum import Enum
from typing import Optional, Callable, List
from threading import Lock
from item_assistant.logging import get_logger

logger = get_logger()


class AssistantState(Enum):
    """Enum for assistant states"""
    IDLE = "Idle"
    LISTENING = "Listening"
    THINKING = "Thinking"
    SPEAKING = "Speaking"


class UIStateManager:
    """Manages UI state and broadcasts updates to listeners"""
    
    def __init__(self):
        """Initialize state manager"""
        self.current_state = AssistantState.IDLE
        self.last_user_text: Optional[str] = None
        self.last_assistant_text: Optional[str] = None
        self.listeners: List[Callable] = []
        self.lock = Lock()
        
        logger.info("UI State Manager initialized")
    
    def register_listener(self, callback: Callable):
        """
        Register a callback to be called on state changes
        
        Args:
            callback: Function that takes (state, user_text, assistant_text)
        """
        with self.lock:
            self.listeners.append(callback)
            logger.debug(f"Registered UI listener: {callback.__name__}")
    
    def update_state(self, state: AssistantState, 
                    user_text: Optional[str] = None,
                    assistant_text: Optional[str] = None):
        """
        Update assistant state and notify listeners
        
        Args:
            state: New assistant state
            user_text: Last user message (optional)
            assistant_text: Last assistant response (optional)
        """
        with self.lock:
            self.current_state = state
            if user_text is not None:
                self.last_user_text = user_text
            if assistant_text is not None:
                self.last_assistant_text = assistant_text
            
            logger.debug(f"State updated: {state.value}")
        
        # Notify all listeners (outside lock to avoid deadlock)
        self._notify_listeners()
    
    def _notify_listeners(self):
        """Notify all registered listeners of state change"""
        with self.lock:
            listeners_copy = self.listeners.copy()
            state = self.current_state
            user_text = self.last_user_text
            assistant_text = self.last_assistant_text
        
        for listener in listeners_copy:
            try:
                listener(state, user_text, assistant_text)
            except Exception as e:
                logger.error(f"Error calling UI listener: {e}")
    
    def get_state(self) -> tuple:
        """
        Get current state
        
        Returns:
            Tuple of (state, user_text, assistant_text)
        """
        with self.lock:
            return (self.current_state, self.last_user_text, self.last_assistant_text)


# Global state manager instance
_state_manager_instance: Optional[UIStateManager] = None


def get_ui_state_manager() -> UIStateManager:
    """Get the global UI state manager instance"""
    global _state_manager_instance
    if _state_manager_instance is None:
        _state_manager_instance = UIStateManager()
    return _state_manager_instance

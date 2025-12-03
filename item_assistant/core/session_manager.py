"""
Session Manager
Manages the lifecycle of an assistant session, ensuring proper initialization and cleanup.
Allows multiple sessions in the same process without resource leaks or singleton conflicts.
"""

import asyncio
import threading
from typing import Optional, Dict, List
from item_assistant.logging import get_logger

logger = get_logger()


class SessionManager:
    """Manages a single assistant session lifecycle"""
    
    def __init__(self):
        """Initialize session manager"""
        self.session_id = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.resources: List[str] = []  # Track resource names for cleanup
        self.singletons_to_reset: List[tuple] = []  # (module, function_name)
        self.running = False
        
        logger.info("[SESSION] SessionManager initialized")
    
    def start_session(self) -> str:
        """
        Start a new session
        
        Returns:
            Session ID
        """
        import uuid
        self.session_id = str(uuid.uuid4())[:8]
        self.running = True
        
        # Create event loop for this session
        try:
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            logger.info(f"[SESSION] Session {self.session_id} started with new event loop")
        except Exception as e:
            logger.error(f"[SESSION] Failed to create event loop: {e}")
            raise
        
        return self.session_id
    
    def register_singleton_reset(self, module_name: str, reset_function_name: str):
        """
        Register a singleton that needs to be reset on shutdown
        
        Args:
            module_name: Module name (e.g., 'item_assistant.voice.wake_word')
            reset_function_name: Function name to call for reset (e.g., 'reset_wake_word_detector')
        """
        self.singletons_to_reset.append((module_name, reset_function_name))
        logger.debug(f"[SESSION] Registered singleton reset: {module_name}.{reset_function_name}")
    
    def register_resource(self, resource_name: str):
        """
        Register a resource for tracking
        
        Args:
            resource_name: Name of resource (e.g., 'audio_stream', 'api_server')
        """
        self.resources.append(resource_name)
        logger.debug(f"[SESSION] Registered resource: {resource_name}")
    
    async def run_async(self, coro):
        """
        Run an async coroutine in this session's event loop
        
        Args:
            coro: Coroutine to run
        
        Returns:
            Result of coroutine
        """
        if not self.event_loop:
            raise RuntimeError("Session not started")
        
        return await coro
    
    def end_session(self):
        """
        End the session and clean up all resources
        """
        logger.info(f"[SESSION] Ending session {self.session_id}")
        self.running = False
        
        # Reset all registered singletons
        logger.info("[SESSION] Resetting singletons...")
        for module_name, reset_function_name in self.singletons_to_reset:
            try:
                # Import module and call reset function
                parts = module_name.rsplit('.', 1)
                if len(parts) == 2:
                    module_path, _ = parts
                    module = __import__(module_path, fromlist=[module_path.split('.')[-1]])
                    reset_func = getattr(module, reset_function_name, None)
                    if reset_func and callable(reset_func):
                        reset_func()
                        logger.info(f"[SESSION] Reset: {module_name}.{reset_function_name}")
                    else:
                        logger.warning(f"[SESSION] Reset function not found: {module_name}.{reset_function_name}")
            except Exception as e:
                logger.error(f"[SESSION] Failed to reset {module_name}.{reset_function_name}: {e}")
        
        # Close event loop
        if self.event_loop:
            try:
                # Cancel all pending tasks
                pending = asyncio.all_tasks(self.event_loop)
                for task in pending:
                    task.cancel()
                
                # Run loop one more time to process cancellations
                self.event_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
                # Close the loop
                self.event_loop.close()
                logger.info("[SESSION] Event loop closed")
            except Exception as e:
                logger.error(f"[SESSION] Error closing event loop: {e}")
        
        logger.info(f"[SESSION] Session {self.session_id} ended")
        self.session_id = None
        self.event_loop = None
        self.resources.clear()
        self.singletons_to_reset.clear()


# Global session manager instance
_session_manager_instance: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    global _session_manager_instance
    if _session_manager_instance is None:
        _session_manager_instance = SessionManager()
    return _session_manager_instance


def reset_session_manager():
    """Reset the session manager (for testing)"""
    global _session_manager_instance
    _session_manager_instance = None

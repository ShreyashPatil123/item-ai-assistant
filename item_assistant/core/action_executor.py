"""
Action Executor
Executes parsed actions and workflows.
"""

from typing import Dict, Optional
from datetime import datetime

from item_assistant.logging import get_logger, get_log_manager
from item_assistant.desktop import (
    get_app_controller,
    get_input_controller,
    get_browser_controller,
    get_shell_executor,
    get_system_controller,
    get_file_manager
)
from item_assistant.llm import get_llm_router
from item_assistant.voice import get_tts

logger = get_logger()
log_manager = get_log_manager()


class ActionExecutor:
    """Executes actions based on parsed intents"""
    
    def __init__(self):
        """Initialize action executor"""
        # Get controller instances
        self.app_controller = get_app_controller()
        self.input_controller = get_input_controller()
        self.browser_controller = get_browser_controller()
        self.shell_executor = get_shell_executor()
        self.system_controller = get_system_controller()
        self.file_manager = get_file_manager()
        self.llm_router = get_llm_router()
        self.tts = get_tts()
        
        logger.info("Action executor initialized")
    
    async def execute(self, intent: Dict) -> Dict:
        """
        Execute an action based on intent
        
        Args:
            intent: Parsed intent dictionary
        
        Returns:
            Execution result
        """
        intent_type = intent.get("intent", "unknown")
        entities = intent.get("entities", {})
        
        logger.info(f"Executing intent: {intent_type}")
        
        # Route to appropriate handler
        if intent_type == "open_app":
            return self._handle_open_app(entities)
        
        elif intent_type == "close_app":
            return self._handle_close_app(entities)
        
        elif intent_type == "search_web":
            return self._handle_search_web(entities)
        
        elif intent_type == "open_url":
            return self._handle_open_url(entities)
        
        elif intent_type == "navigate_youtube":
            return self._handle_navigate_youtube(entities)
        
        elif intent_type == "type_text":
            return self._handle_type_text(entities)
        
        elif intent_type == "click":
            return self._handle_click(entities)
        
        elif intent_type == "run_command":
            return self._handle_run_command(entities)
        
        elif intent_type == "generate_code":
            return self._handle_generate_code(entities)
        
        elif intent_type == "get_time":
            return self._handle_get_time()
        
        elif intent_type == "general_query":
            return self._handle_general_query(entities)
        
        # System control intents
        elif intent_type == "system_shutdown":
            return self._handle_system_shutdown(entities)
        
        elif intent_type == "system_restart":
            return self._handle_system_restart(entities)
        
        elif intent_type == "system_sleep":
            return self._handle_system_sleep()
        
        elif intent_type == "system_lock":
            return self._handle_system_lock()
        
        elif intent_type == "system_logout":
            return self._handle_system_logout()
        
        # Volume control
        elif intent_type == "set_volume":
            return self._handle_set_volume(entities)
        
        elif intent_type == "mute_volume":
            return self._handle_mute()
        
        elif intent_type == "unmute_volume":
            return self._handle_unmute()
        
        # Brightness control
        elif intent_type == "set_brightness":
            return self._handle_set_brightness(entities)
        
        # Window management
        elif intent_type == "minimize_window":
            return self._handle_minimize_window()
        
        elif intent_type == "maximize_window":
            return self._handle_maximize_window()
        
        elif intent_type == "close_window":
            return self._handle_close_window()
        
        # Clipboard
        elif intent_type == "get_clipboard":
            return self._handle_get_clipboard()
        
        elif intent_type == "set_clipboard":
            return self._handle_set_clipboard(entities)
        
        # File operations
        elif intent_type == "create_file":
            return self._handle_create_file(entities)
        
        elif intent_type == "list_directory":
            return self._handle_list_directory(entities)
        
        # System info
        elif intent_type == "get_system_info":
            return self._handle_get_system_info()
        
        else:
            return {
                "success": False,
                "message": f"Unknown intent: {intent_type}"
            }
    
    def _handle_open_app(self, entities: Dict) -> Dict:
        """Handle open app action"""
        app_name = entities.get("app_name", "")
        if not app_name:
            return {"success": False, "message": "No app name provided"}
        
        result = self.app_controller.open_app(app_name)
        return result
    
    def _handle_close_app(self, entities: Dict) -> Dict:
        """Handle close app action"""
        app_name = entities.get("app_name", "")
        if not app_name:
            return {"success": False, "message": "No app name provided"}
        
        # TODO: Add confirmation logic here
        result = self.app_controller.close_app(app_name)
        return result
    
    def _handle_search_web(self, entities: Dict) -> Dict:
        """Handle web search action"""
        query = entities.get("query", "")
        if not query:
            return {"success": False, "message": "No search query provided"}
        
        result = self.browser_controller.search_google(query)
        return result
    
    def _handle_open_url(self, entities: Dict) -> Dict:
        """Handle open URL action"""
        url = entities.get("url", "")
        if not url:
            return {"success": False, "message": "No URL provided"}
        
        result = self.browser_controller.open_url(url)
        return result
    
    def _handle_navigate_youtube(self, entities: Dict) -> Dict:
        """Handle YouTube navigation"""
        video_name = entities.get("video_name")
        result = self.browser_controller.navigate_to_youtube(video_name)
        return result
    
    def _handle_type_text(self, entities: Dict) -> Dict:
        """Handle type text action"""
        text = entities.get("text", "")
        if not text:
            return {"success": False, "message": "No text provided"}
        
        result = self.input_controller.type_text(text)
        return result
    
    def _handle_click(self, entities: Dict) -> Dict:
        """Handle click action"""
        x = entities.get("x")
        y = entities.get("y")
        
        result = self.input_controller.click(x, y)
        return result
    
    def _handle_run_command(self, entities: Dict) -> Dict:
        """Handle shell command execution"""
        command = entities.get("command", "")
        if not command:
            return {"success": False, "message": "No command provided"}
        
        # TODO: Add confirmation logic here
        result = self.shell_executor.run_command(command)
        return result
    
    def _handle_generate_code(self, entities: Dict) -> Dict:
        """Handle code generation"""
        prompt = entities.get("prompt", "")
        language = entities.get("language")
        
        if not prompt:
            return {"success": False, "message": "No code prompt provided"}
        
        result = self.llm_router.generate_code(prompt, language)
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Code generated successfully",
                "data": {"code": result.get("text")}
            }
        else:
            return {
                "success": False,
                "message": f"Code generation failed: {result.get('error')}"
            }
    
    def _handle_get_time(self) -> Dict:
        """Handle get time query"""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%B %d, %Y")
        
        message = f"It's {time_str} on {date_str}"
        
        return {
            "success": True,
            "message": message,
            "data": {
                "time": time_str,
                "date": date_str
            }
        }
    
    def _handle_general_query(self, entities: Dict) -> Dict:
        """Handle general query using LLM"""
        query = entities.get("query", "")
        
        if not query:
            return {"success": False, "message": "No query provided"}
        
        result = self.llm_router.generate(query, task_type="quick_command")
        
        if result.get("success"):
            response_text = result.get("text", "")
            return {
                "success": True,
                "message": response_text,
                "data": {"response": response_text}
            }
        else:
            return {
                "success": False,
                "message": "Failed to process query"
            }
    
    # ========================
    # System Control Handlers
    # ========================
    
    def _handle_system_shutdown(self, entities: Dict) -> Dict:
        """Handle system shutdown"""
        timeout = entities.get("timeout", 30)
        return self.system_controller.shutdown(timeout=timeout)
    
    def _handle_system_restart(self, entities: Dict) -> Dict:
        """Handle system restart"""
        timeout = entities.get("timeout", 30)
        return self.system_controller.restart(timeout=timeout)
    
    def _handle_system_sleep(self) -> Dict:
        """Handle system sleep"""
        return self.system_controller.sleep()
    
    def _handle_system_lock(self) -> Dict:
        """Handle system lock"""
        return self.system_controller.lock()
    
    def _handle_system_logout(self) -> Dict:
        """Handle system logout"""
        return self.system_controller.logout()
    
    # ========================
    # Volume Control Handlers
    # ========================
    
    def _handle_set_volume(self, entities: Dict) -> Dict:
        """Handle set volume"""
        level = entities.get("level", 50)
        return self.system_controller.set_volume(level)
    
    def _handle_mute(self) -> Dict:
        """Handle mute"""
        return self.system_controller.mute()
    
    def _handle_unmute(self) -> Dict:
        """Handle unmute"""
        return self.system_controller.unmute()
    
    # ========================
    # Brightness Control Handlers
    # ========================
    
    def _handle_set_brightness(self, entities: Dict) -> Dict:
        """Handle set brightness"""
        level = entities.get("level", 50)
        return self.system_controller.set_brightness(level)
    
    # ========================
    # Window Management Handlers
    # ========================
    
    def _handle_minimize_window(self) -> Dict:
        """Handle minimize window"""
        return self.system_controller.minimize_window()
    
    def _handle_maximize_window(self) -> Dict:
        """Handle maximize window"""
        return self.system_controller.maximize_window()
    
    def _handle_close_window(self) -> Dict:
        """Handle close window"""
        return self.system_controller.close_window()
    
    # ========================
    # Clipboard Handlers
    # ========================
    
    def _handle_get_clipboard(self) -> Dict:
        """Handle get clipboard"""
        return self.system_controller.get_clipboard()
    
    def _handle_set_clipboard(self, entities: Dict) -> Dict:
        """Handle set clipboard"""
        text = entities.get("text", "")
        return self.system_controller.set_clipboard(text)
    
    # ========================
    # File Operation Handlers
    # ========================
    
    def _handle_create_file(self, entities: Dict) -> Dict:
        """Handle create file"""
        filepath = entities.get("filepath", "")
        content = entities.get("content", "")
        
        if not filepath:
            return {"success": False, "message": "No filepath provided"}
        
        return self.file_manager.create_file(filepath, content)
    
    def _handle_list_directory(self, entities: Dict) -> Dict:
        """Handle list directory"""
        dirpath = entities.get("dirpath", "")
        
        if not dirpath:
            return {"success": False, "message": "No directory path provided"}
        
        return self.file_manager.list_directory(dirpath)
    
    # ========================
    # System Info Handlers
    # ========================
    
    def _handle_get_system_info(self) -> Dict:
        """Handle get system info"""
        result = self.system_controller.get_system_info()
        
        if result.get("success"):
            data = result.get("data", {})
            message = (
                f"CPU: {data.get('cpu_percent')}%, "
                f"RAM: {data.get('memory_percent')}% "
                f"({data.get('memory_used_gb')}GB/{data.get('memory_total_gb')}GB), "
                f"Disk: {data.get('disk_percent')}%"
            )
            result["message"] = message
        
        return result


# Global action executor instance
_action_executor_instance = None


def get_action_executor() -> ActionExecutor:
    """Get the global action executor instance"""
    global _action_executor_instance
    if _action_executor_instance is None:
        _action_executor_instance = ActionExecutor()
    return _action_executor_instance

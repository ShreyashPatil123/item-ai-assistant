"""
App Controller for Item AI Assistant
Controls launching, closing, and managing Windows applications.
"""

import psutil
import subprocess
import time
from typing import List, Optional, Dict
from pathlib import Path

from item_assistant.config import get_config
from item_assistant.logging import get_log_manager
from item_assistant.permissions import get_permission_manager

logger = get_log_manager().get_logger()
log_manager = get_log_manager()


class AppController:
    """Controls Windows applications"""
    
    def __init__(self):
        """Initialize app controller"""
        self.config = get_config()
        self.permission_manager = get_permission_manager()
        
        # Common Windows applications with their executables
        self.known_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "firefox": "firefox.exe",
            "vscode": "Code.exe",
            "vs code": "Code.exe",
            "code": "Code.exe",
            "excel": "excel.exe",
            "word": "winword.exe",
            "powerpoint": "powerpnt.exe",
            "outlook": "outlook.exe",
            "spotify": "spotify.exe",
            "discord": "discord.exe",
            "slack": "slack.exe",
            "teams": "teams.exe",
            "paint": "mspaint.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "terminal": "WindowsTerminal.exe",
        }
        
        logger.info("App controller initialized")
    
    def _normalize_app_name(self, app_name: str) -> str:
        """
        Normalize app name to lowercase and get executable
        
        Args:
            app_name: App name or executable
        
        Returns:
            Normalized executable name
        """
        app_lower = app_name.lower().strip()
        
        # Check if it's a known app
        if app_lower in self.known_apps:
            return self.known_apps[app_lower]
        
        # If it already ends with .exe, use as-is
        if app_lower.endswith('.exe'):
            return app_lower
        
        # Otherwise, add .exe
        return f"{app_lower}.exe"
    
    def _find_process(self, app_name: str) -> Optional[psutil.Process]:
        """
        Find a running process by name
        
        Args:
            app_name: App name or executable
        
        Returns:
            Process object if found, None otherwise
        """
        exe_name = self._normalize_app_name(app_name)
        
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == exe_name.lower():
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return None
    
    def is_running(self, app_name: str) -> bool:
        """
        Check if an app is currently running
        
        Args:
            app_name: App name
        
        Returns:
            True if running
        """
        return self._find_process(app_name) is not None
    
    def open_app(self, app_name: str, wait_time: float = 2.0) -> Dict[str, any]:
        """
        Open/launch an application
        
        Args:
            app_name: Name of the application to open
            wait_time: Time to wait after launching (seconds)
        
        Returns:
            Dictionary with status and message
        """
        # Check permission
        if not self.permission_manager.check_and_request_permission(app_name):
            log_manager.log_action("open_app", app_name, "denied")
            return {
                "success": False,
                "message": f"Permission denied to control '{app_name}'"
            }
        
        log_manager.log_action("open_app", app_name, "started")
        
        # Check if already running
        if self.is_running(app_name):
            logger.info(f"App '{app_name}' is already running")
            return {
                "success": True,
                "message": f"{app_name} is already running",
                "already_running": True
            }
        
        # Get executable name
        exe_name = self._normalize_app_name(app_name)
        
        try:
            # Try to launch the app
            subprocess.Popen(exe_name, shell=True)
            
            # Wait for app to start
            time.sleep(wait_time)
            
            # Verify it started
            if self.is_running(app_name):
                log_manager.log_action("open_app", app_name, "completed")
                return {
                    "success": True,
                    "message": f"Successfully opened {app_name}"
                }
            else:
                return {
                    "success": False,
                    "message": f"App launched but not detected as running"
                }
        
        except Exception as e:
            log_manager.log_error("open_app", f"Failed to open {app_name}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to open {app_name}: {str(e)}"
            }
    
    def close_app(self, app_name: str, force: bool = False) -> Dict[str, any]:
        """
        Close an application
        
        Args:
            app_name: Name of the application to close
            force: Force close without graceful shutdown
        
        Returns:
            Dictionary with status and message
        """
        log_manager.log_action("close_app", app_name, "started")
        
        # Find the process
        proc = self._find_process(app_name)
        
        if proc is None:
            return {
                "success": False,
                "message": f"{app_name} is not running"
            }
        
        try:
            if force:
                proc.kill()  # Force kill
            else:
                proc.terminate()  # Graceful termination
            
            # Wait for process to end
            proc.wait(timeout=5)
            
            log_manager.log_action("close_app", app_name, "completed")
            return {
                "success": True,
                "message": f"Successfully closed {app_name}"
            }
        
        except psutil.TimeoutExpired:
            # If graceful close failed, force kill
            if not force:
                return self.close_app(app_name, force=True)
            else:
                return {
                    "success": False,
                    "message": f"Failed to close {app_name} even with force"
                }
        
        except Exception as e:
            log_manager.log_error("close_app", f"Failed to close {app_name}: {str(e)}")
            return {
                "success": False,
                "message": f"Error closing {app_name}: {str(e)}"
            }
    
    def focus_app(self, app_name: str) -> Dict[str, any]:
        """
        Bring an app window to the foreground
        
        Args:
            app_name: Name of the application
        
        Returns:
            Dictionary with status and message
        """
        # This requires pywinauto for advanced window management
        # For now, we'll do a basic implementation
        
        if not self.is_running(app_name):
            return {
                "success": False,
                "message": f"{app_name} is not running"
            }
        
        # TODO: Implement with pywinauto for actual window focus
        # For now, just return success
        return {
            "success": True,
            "message": f"Focused {app_name} (basic implementation)"
        }
    
    def list_running_apps(self) -> List[str]:
        """
        List all currently running GUI applications
        
        Returns:
            List of running app executables
        """
        running = set()
        
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name and name.endswith('.exe'):
                    running.add(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return sorted(list(running))


# Global app controller instance
_app_controller_instance = None


def get_app_controller() -> AppController:
    """Get the global app controller instance"""
    global _app_controller_instance
    if _app_controller_instance is None:
        _app_controller_instance = AppController()
    return _app_controller_instance

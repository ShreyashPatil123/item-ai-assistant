"""
Input Controller for Item AI Assistant
Controls mouse and keyboard input using pyautogui.
"""

import pyautogui
import time
from typing import Tuple, Optional

from item_assistant.config import get_config
from item_assistant.logging import get_log_manager

logger = get_log_manager().get_logger()
log_manager = get_log_manager()

# Configure pyautogui safety features
pyautogui.PAUSE = 0.1  # Small pause between actions
pyautogui.FAILSAFE = True  # Move mouse to corner to abort


class InputController:
    """Controls mouse and keyboard input"""
    
    def __init__(self):
        """Initialize input controller"""
        self.config = get_config()
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"Input controller initialized (screen: {self.screen_width}x{self.screen_height})")
    
    def _validate_coordinates(self, x: int, y: int) -> bool:
        """
        Validate that coordinates are within screen bounds
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            True if valid
        """
        return 0 <= x < self.screen_width and 0 <= y < self.screen_height
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = 'left', clicks: int = 1) -> dict:
        """
        Click at coordinates
        
        Args:
            x: X coordinate (None for current position)
            y: Y coordinate (None for current position)
            button: 'left', 'right', or 'middle'
            clicks: Number of clicks
        
        Returns:
            Dictionary with status and message
        """
        try:
            if x is not None and y is not None:
                if not self._validate_coordinates(x, y):
                    return {
                        "success": False,
                        "message": f"Coordinates ({x}, {y}) out of screen bounds"
                    }
                pyautogui.click(x, y, clicks=clicks, button=button)
                log_manager.log_action("click", f"({x}, {y}) {button} x{clicks}", "completed")
            else:
                pyautogui.click(clicks=clicks, button=button)
                log_manager.log_action("click", f"current position {button} x{clicks}", "completed")
            
            return {
                "success": True,
                "message": f"Clicked at ({x}, {y})" if x and y else "Clicked at current position"
            }
        
        except Exception as e:
            log_manager.log_error("click", str(e))
            return {
                "success": False,
                "message": f"Click failed: {str(e)}"
            }
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> dict:
        """Double-click at coordinates"""
        return self.click(x, y, clicks=2)
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> dict:
        """Right-click at coordinates"""
        return self.click(x, y, button='right')
    
    def move_mouse(self, x: int, y: int, duration: float = 0.2) -> dict:
        """
        Move mouse to coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration in seconds
        
        Returns:
            Dictionary with status and message
        """
        try:
            if not self._validate_coordinates(x, y):
                return {
                    "success": False,
                    "message": f"Coordinates ({x}, {y}) out of screen bounds"
                }
            
            pyautogui.moveTo(x, y, duration=duration)
            log_manager.log_action("move_mouse", f"({x}, {y})", "completed")
            
            return {
                "success": True,
                "message": f"Moved mouse to ({x}, {y})"
            }
        
        except Exception as e:
            log_manager.log_error("move_mouse", str(e))
            return {
                "success": False,
                "message": f"Move failed: {str(e)}"
            }
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position
        
        Returns:
            Tuple of (x, y)
        """
        return pyautogui.position()
    
    def type_text(self, text: str, interval: float = 0.05) -> dict:
        """
        Type text
        
        Args:
            text: Text to type
            interval: Interval between keystrokes in seconds
        
        Returns:
            Dictionary with status and message
        """
        try:
            pyautogui.write(text, interval=interval)
            log_manager.log_action("type_text", f"{len(text)} characters", "completed")
            
            return {
                "success": True,
                "message": f"Typed {len(text)} characters"
            }
        
        except Exception as e:
            log_manager.log_error("type_text", str(e))
            return {
                "success": False,
                "message": f"Type failed: {str(e)}"
            }
    
    def press_key(self, key: str, presses: int = 1) -> dict:
        """
        Press a key
        
        Args:
            key: Key name (e.g., 'enter', 'esc', 'tab', 'a', 'ctrl')
            presses: Number of times to press
        
        Returns:
            Dictionary with status and message
        """
        try:
            for _ in range(presses):
                pyautogui.press(key)
            
            log_manager.log_action("press_key", f"{key} x{presses}", "completed")
            
            return {
                "success": True,
                "message": f"Pressed '{key}' {presses} time(s)"
            }
        
        except Exception as e:
            log_manager.log_error("press_key", str(e))
            return {
                "success": False,
                "message": f"Key press failed: {str(e)}"
            }
    
    def hotkey(self, *keys: str) -> dict:
        """
        Press a hotkey combination
        
        Args:
            *keys: Keys to press together (e.g., 'ctrl', 'c')
        
        Returns:
            Dictionary with status and message
        """
        try:
            pyautogui.hotkey(*keys)
            hotkey_str = '+'.join(keys)
            log_manager.log_action("hotkey", hotkey_str, "completed")
            
            return {
                "success": True,
                "message": f"Pressed hotkey: {hotkey_str}"
            }
        
        except Exception as e:
            log_manager.log_error("hotkey", str(e))
            return {
                "success": False,
                "message": f"Hotkey failed: {str(e)}"
            }
    
    def scroll(self, clicks: int) -> dict:
        """
        Scroll up (positive) or down (negative)
        
        Args:
            clicks: Number of scroll clicks (positive = up, negative = down)
        
        Returns:
            Dictionary with status and message
        """
        try:
            pyautogui.scroll(clicks)
            direction = "up" if clicks > 0 else "down"
            log_manager.log_action("scroll", f"{direction} {abs(clicks)} clicks", "completed")
            
            return {
                "success": True,
                "message": f"Scrolled {direction} {abs(clicks)} clicks"
            }
        
        except Exception as e:
            log_manager.log_error("scroll", str(e))
            return {
                "success": False,
                "message": f"Scroll failed: {str(e)}"
            }
    
    def screenshot(self, filepath: Optional[str] = None) -> dict:
        """
        Take a screenshot
        
        Args:
            filepath: Path to save screenshot (None = return image object)
        
        Returns:
            Dictionary with status, message, and optionally the image
        """
        try:
            screenshot = pyautogui.screenshot()
            
            if filepath:
                screenshot.save(filepath)
                log_manager.log_action("screenshot", filepath, "completed")
                return {
                    "success": True,
                    "message": f"Screenshot saved to {filepath}"
                }
            else:
                return {
                    "success": True,
                    "message": "Screenshot captured",
                    "image": screenshot
                }
        
        except Exception as e:
            log_manager.log_error("screenshot", str(e))
            return {
                "success": False,
                "message": f"Screenshot failed: {str(e)}"
            }


# Global input controller instance
_input_controller_instance = None


def get_input_controller() -> InputController:
    """Get the global input controller instance"""
    global _input_controller_instance
    if _input_controller_instance is None:
        _input_controller_instance = InputController()
    return _input_controller_instance

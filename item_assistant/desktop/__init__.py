"""Desktop automation module initialization"""

from .app_controller import AppController, get_app_controller
from .input_controller import InputController, get_input_controller
from .browser_controller import BrowserController, get_browser_controller
from .shell_executor import ShellExecutor, get_shell_executor
from .system_controller import SystemController, get_system_controller
from .file_manager import FileManager, get_file_manager

__all__ = [
    'AppController', 'get_app_controller',
    'InputController', 'get_input_controller',
    'BrowserController', 'get_browser_controller',
    'ShellExecutor', 'get_shell_executor',
    'SystemController', 'get_system_controller',
    'FileManager', 'get_file_manager',
]

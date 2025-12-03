"""
System Controller for Item AI Assistant
Controls system-level operations like power management, volume, brightness, clipboard, and window management.
"""

import os
import platform
import subprocess
import psutil
import pyperclip
import ctypes
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import win32gui
import win32con
import win32process

from item_assistant.config import get_config
from item_assistant.logging import get_log_manager

logger = get_log_manager().get_logger()
log_manager = get_log_manager()


class SystemController:
    """Controls system-level operations"""
    
    def __init__(self):
        """Initialize system controller"""
        self.config = get_config()
        self.user32 = ctypes.windll.user32
        logger.info("System controller initialized")
    
    # ========================
    # Power Management
    # ========================
    
    def shutdown(self, force: bool = False, timeout: int = 30) -> Dict:
        """
        Shutdown the computer
        
        Args:
            force: Force shutdown without prompting
            timeout: Seconds to wait before shutdown
        
        Returns:
            Dictionary with status and message
        """
        log_manager.log_action("system_shutdown", f"timeout={timeout}", "started")
        
        try:
            cmd = f"shutdown /s /t {timeout}"
            if force:
                cmd += " /f"
            
            subprocess.run(cmd, shell=True, check=True)
            log_manager.log_action("system_shutdown", f"timeout={timeout}", "completed")
            
            return {
                "success": True,
                "message": f"System will shutdown in {timeout} seconds"
            }
        except Exception as e:
            log_manager.log_error("system_shutdown", str(e))
            return {
                "success": False,
                "message": f"Shutdown failed: {str(e)}"
            }
    
    def restart(self, force: bool = False, timeout: int = 30) -> Dict:
        """
        Restart the computer
        
        Args:
            force: Force restart without prompting
            timeout: Seconds to wait before restart
        
        Returns:
            Dictionary with status and message
        """
        log_manager.log_action("system_restart", f"timeout={timeout}", "started")
        
        try:
            cmd = f"shutdown /r /t {timeout}"
            if force:
                cmd += " /f"
            
            subprocess.run(cmd, shell=True, check=True)
            log_manager.log_action("system_restart", f"timeout={timeout}", "completed")
            
            return {
                "success": True,
                "message": f"System will restart in {timeout} seconds"
            }
        except Exception as e:
            log_manager.log_error("system_restart", str(e))
            return {
                "success": False,
                "message": f"Restart failed: {str(e)}"
            }
    
    def cancel_shutdown(self) -> Dict:
        """
        Cancel a pending shutdown or restart
        
        Returns:
            Dictionary with status and message
        """
        try:
            subprocess.run("shutdown /a", shell=True, check=True)
            log_manager.log_action("cancel_shutdown", "", "completed")
            
            return {
                "success": True,
                "message": "Shutdown/restart cancelled"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Cancel failed: {str(e)}"
            }
    
    def sleep(self) -> Dict:
        """
        Put computer to sleep
        
        Returns:
            Dictionary with status and message
        """
        log_manager.log_action("system_sleep", "", "started")
        
        try:
            # Use rundll32 to call sleep
            subprocess.run(
                "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                shell=True,
                check=True
            )
            log_manager.log_action("system_sleep", "", "completed")
            
            return {
                "success": True,
                "message": "System going to sleep"
            }
        except Exception as e:
            log_manager.log_error("system_sleep", str(e))
            return {
                "success": False,
                "message": f"Sleep failed: {str(e)}"
            }
    
    def lock(self) -> Dict:
        """
        Lock the computer
        
        Returns:
            Dictionary with status and message
        """
        log_manager.log_action("system_lock", "", "started")
        
        try:
            # Lock workstation
            ctypes.windll.user32.LockWorkStation()
            log_manager.log_action("system_lock", "", "completed")
            
            return {
                "success": True,
                "message": "System locked"
            }
        except Exception as e:
            log_manager.log_error("system_lock", str(e))
            return {
                "success": False,
                "message": f"Lock failed: {str(e)}"
            }
    
    def logout(self) -> Dict:
        """
        Logout current user
        
        Returns:
            Dictionary with status and message
        """
        log_manager.log_action("system_logout", "", "started")
        
        try:
            subprocess.run("shutdown /l", shell=True, check=True)
            log_manager.log_action("system_logout", "", "completed")
            
            return {
                "success": True,
                "message": "Logging out"
            }
        except Exception as e:
            log_manager.log_error("system_logout", str(e))
            return {
                "success": False,
                "message": f"Logout failed: {str(e)}"
            }
    
    # ========================
    # Volume Control
    # ========================
    
    def set_volume(self, level: int) -> Dict:
        """
        Set system volume
        
        Args:
            level: Volume level 0-100
        
        Returns:
            Dictionary with status and message
        """
        if not 0 <= level <= 100:
            return {
                "success": False,
                "message": "Volume must be between 0 and 100"
            }
        
        log_manager.log_action("set_volume", str(level), "started")
        
        try:
            # Use nircmd for volume control
            # Volume level: 0-65535, so we convert percentage
            volume_value = int((level / 100) * 65535)
            cmd = f"nircmd.exe setsysvolume {volume_value}"
            
            result = subprocess.run(cmd, shell=True, capture_output=True)
            
            # If nircmd is not installed, use PowerShell alternative
            if result.returncode != 0:
                ps_cmd = f"(New-Object -ComObject WScript.Shell).SendKeys([char]174)"  # Volume down key
                # This is a fallback - we'll use a simpler approach
                return {
                    "success": False,
                    "message": "Volume control requires 'nircmd' to be installed. Download from https://www.nirsoft.net/utils/nircmd.html"
                }
            
            log_manager.log_action("set_volume", str(level), "completed")
            
            return {
                "success": True,
                "message": f"Volume set to {level}%"
            }
        except Exception as e:
            log_manager.log_error("set_volume", str(e))
            return {
                "success": False,
                "message": f"Volume control failed: {str(e)}"
            }
    
    def mute(self) -> Dict:
        """
        Mute system volume
        
        Returns:
            Dictionary with status and message
        """
        log_manager.log_action("mute_volume", "", "started")
        
        try:
            cmd = "nircmd.exe mutesysvolume 1"
            result = subprocess.run(cmd, shell=True, capture_output=True)
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": "Volume control requires 'nircmd' to be installed"
                }
            
            log_manager.log_action("mute_volume", "", "completed")
            
            return {
                "success": True,
                "message": "System muted"
            }
        except Exception as e:
            log_manager.log_error("mute_volume", str(e))
            return {
                "success": False,
                "message": f"Mute failed: {str(e)}"
            }
    
    def unmute(self) -> Dict:
        """
        Unmute system volume
        
        Returns:
            Dictionary with status and message
        """
        log_manager.log_action("unmute_volume", "", "started")
        
        try:
            cmd = "nircmd.exe mutesysvolume 0"
            result = subprocess.run(cmd, shell=True, capture_output=True)
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": "Volume control requires 'nircmd' to be installed"
                }
            
            log_manager.log_action("unmute_volume", "", "completed")
            
            return {
                "success": True,
                "message": "System unmuted"
            }
        except Exception as e:
            log_manager.log_error("unmute_volume", str(e))
            return {
                "success": False,
                "message": f"Unmute failed: {str(e)}"
            }
    
    # ========================
    # Brightness Control
    # ========================
    
    def set_brightness(self, level: int) -> Dict:
        """
        Set screen brightness
        
        Args:
            level: Brightness level 0-100
        
        Returns:
            Dictionary with status and message
        """
        if not 0 <= level <= 100:
            return {
                "success": False,
                "message": "Brightness must be between 0 and 100"
            }
        
        log_manager.log_action("set_brightness", str(level), "started")
        
        try:
            # Use PowerShell WMI to set brightness
            ps_script = f"""
            $brightness = Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods
            $brightness.WmiSetBrightness(1, {level})
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                log_manager.log_action("set_brightness", str(level), "completed")
                return {
                    "success": True,
                    "message": f"Brightness set to {level}%"
                }
            else:
                return {
                    "success": False,
                    "message": "Brightness control may not be supported on this system"
                }
        except Exception as e:
            log_manager.log_error("set_brightness", str(e))
            return {
                "success": False,
                "message": f"Brightness control failed: {str(e)}"
            }
    
    # ========================
    # Window Management
    # ========================
    
    def get_active_window(self) -> Dict:
        """
        Get information about the active window
        
        Returns:
            Dictionary with window information
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            
            # Get process info
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            
            return {
                "success": True,
                "data": {
                    "hwnd": hwnd,
                    "title": title,
                    "pid": pid,
                    "process_name": process.name()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get active window: {str(e)}"
            }
    
    def minimize_window(self, hwnd: Optional[int] = None) -> Dict:
        """
        Minimize a window
        
        Args:
            hwnd: Window handle (None for active window)
        
        Returns:
            Dictionary with status and message
        """
        try:
            if hwnd is None:
                hwnd = win32gui.GetForegroundWindow()
            
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            log_manager.log_action("minimize_window", str(hwnd), "completed")
            
            return {
                "success": True,
                "message": "Window minimized"
            }
        except Exception as e:
            log_manager.log_error("minimize_window", str(e))
            return {
                "success": False,
                "message": f"Minimize failed: {str(e)}"
            }
    
    def maximize_window(self, hwnd: Optional[int] = None) -> Dict:
        """
        Maximize a window
        
        Args:
            hwnd: Window handle (None for active window)
        
        Returns:
            Dictionary with status and message
        """
        try:
            if hwnd is None:
                hwnd = win32gui.GetForegroundWindow()
            
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            log_manager.log_action("maximize_window", str(hwnd), "completed")
            
            return {
                "success": True,
                "message": "Window maximized"
            }
        except Exception as e:
            log_manager.log_error("maximize_window", str(e))
            return {
                "success": False,
                "message": f"Maximize failed: {str(e)}"
            }
    
    def restore_window(self, hwnd: Optional[int] = None) -> Dict:
        """
        Restore a window to normal size
        
        Args:
            hwnd: Window handle (None for active window)
        
        Returns:
            Dictionary with status and message
        """
        try:
            if hwnd is None:
                hwnd = win32gui.GetForegroundWindow()
            
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            log_manager.log_action("restore_window", str(hwnd), "completed")
            
            return {
                "success": True,
                "message": "Window restored"
            }
        except Exception as e:
            log_manager.log_error("restore_window", str(e))
            return {
                "success": False,
                "message": f"Restore failed: {str(e)}"
            }
    
    def close_window(self, hwnd: Optional[int] = None) -> Dict:
        """
        Close a window
        
        Args:
            hwnd: Window handle (None for active window)
        
        Returns:
            Dictionary with status and message
        """
        try:
            if hwnd is None:
                hwnd = win32gui.GetForegroundWindow()
            
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            log_manager.log_action("close_window", str(hwnd), "completed")
            
            return {
                "success": True,
                "message": "Window closed"
            }
        except Exception as e:
            log_manager.log_error("close_window", str(e))
            return {
                "success": False,
                "message": f"Close failed: {str(e)}"
            }
    
    def list_windows(self) -> List[Dict]:
        """
        List all visible windows
        
        Returns:
            List of window information dictionaries
        """
        windows = []
        
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:  # Only include windows with titles
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        windows.append({
                            "hwnd": hwnd,
                            "title": title,
                            "pid": pid,
                            "process_name": process.name()
                        })
                    except:
                        pass
            return True
        
        win32gui.EnumWindows(callback, None)
        return windows
    
    # ========================
    # Clipboard Operations
    # ========================
    
    def get_clipboard(self) -> Dict:
        """
        Get clipboard content
        
        Returns:
            Dictionary with clipboard text
        """
        try:
            text = pyperclip.paste()
            log_manager.log_action("get_clipboard", f"{len(text)} chars", "completed")
            
            return {
                "success": True,
                "data": {"text": text},
                "message": f"Clipboard contains {len(text)} characters"
            }
        except Exception as e:
            log_manager.log_error("get_clipboard", str(e))
            return {
                "success": False,
                "message": f"Failed to get clipboard: {str(e)}"
            }
    
    def set_clipboard(self, text: str) -> Dict:
        """
        Set clipboard content
        
        Args:
            text: Text to copy to clipboard
        
        Returns:
            Dictionary with status and message
        """
        try:
            pyperclip.copy(text)
            log_manager.log_action("set_clipboard", f"{len(text)} chars", "completed")
            
            return {
                "success": True,
                "message": f"Copied {len(text)} characters to clipboard"
            }
        except Exception as e:
            log_manager.log_error("set_clipboard", str(e))
            return {
                "success": False,
                "message": f"Failed to set clipboard: {str(e)}"
            }
    
    # ========================
    # System Information
    # ========================
    
    def get_system_info(self) -> Dict:
        """
        Get comprehensive system information
        
        Returns:
            Dictionary with system information
        """
        try:
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory info
            memory = psutil.virtual_memory()
            memory_total_gb = memory.total / (1024 ** 3)
            memory_used_gb = memory.used / (1024 ** 3)
            memory_percent = memory.percent
            
            # Disk info
            disk = psutil.disk_usage('C:\\')
            disk_total_gb = disk.total / (1024 ** 3)
            disk_used_gb = disk.used / (1024 ** 3)
            disk_percent = disk.percent
            
            # Battery info (if laptop)
            battery_info = {}
            try:
                battery = psutil.sensors_battery()
                if battery:
                    battery_info = {
                        "percent": battery.percent,
                        "plugged_in": battery.power_plugged
                    }
            except:
                pass
            
            info = {
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "memory_total_gb": round(memory_total_gb, 2),
                "memory_used_gb": round(memory_used_gb, 2),
                "memory_percent": memory_percent,
                "disk_total_gb": round(disk_total_gb, 2),
                "disk_used_gb": round(disk_used_gb, 2),
                "disk_percent": disk_percent,
                "platform": platform.system(),
                "platform_version": platform.version(),
            }
            
            if battery_info:
                info["battery"] = battery_info
            
            log_manager.log_action("get_system_info", "", "completed")
            
            return {
                "success": True,
                "data": info,
                "message": "System information retrieved"
            }
        except Exception as e:
            log_manager.log_error("get_system_info", str(e))
            return {
                "success": False,
                "message": f"Failed to get system info: {str(e)}"
            }
    
    def get_process_list(self) -> Dict:
        """
        Get list of running processes
        
        Returns:
            Dictionary with process list
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_percent": proc.info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            return {
                "success": True,
                "data": {"processes": processes[:20]},  # Top 20 processes
                "message": f"Found {len(processes)} processes"
            }
        except Exception as e:
            log_manager.log_error("get_process_list", str(e))
            return {
                "success": False,
                "message": f"Failed to get process list: {str(e)}"
            }
    
    def kill_process(self, pid: int, force: bool = False) -> Dict:
        """
        Kill a process by PID
        
        Args:
            pid: Process ID
            force: Force kill
        
        Returns:
            Dictionary with status and message
        """
        log_manager.log_action("kill_process", str(pid), "started")
        
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            if force:
                process.kill()
            else:
                process.terminate()
            
            process.wait(timeout=5)
            
            log_manager.log_action("kill_process", str(pid), "completed")
            
            return {
                "success": True,
                "message": f"Process {process_name} (PID: {pid}) terminated"
            }
        except psutil.NoSuchProcess:
            return {
                "success": False,
                "message": f"Process {pid} not found"
            }
        except psutil.AccessDenied:
            return {
                "success": False,
                "message": f"Access denied to kill process {pid}"
            }
        except Exception as e:
            log_manager.log_error("kill_process", str(e))
            return {
                "success": False,
                "message": f"Failed to kill process: {str(e)}"
            }


# Global system controller instance
_system_controller_instance = None


def get_system_controller() -> SystemController:
    """Get the global system controller instance"""
    global _system_controller_instance
    if _system_controller_instance is None:
        _system_controller_instance = SystemController()
    return _system_controller_instance

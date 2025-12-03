"""
Shell Executor for Item AI Assistant
Safely executes shell commands with confirmations and sandboxing.
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Optional

from item_assistant.config import get_config
from item_assistant.logging import get_log_manager
from item_assistant.permissions import get_safety_checker

logger = get_log_manager().get_logger()
log_manager = get_log_manager()


class ShellExecutor:
    """Executes shell commands with safety checks"""
    
    def __init__(self):
        """Initialize shell executor"""
        self.config = get_config()
        self.safety_checker = get_safety_checker()
        logger.info("Shell executor initialized")
    
    def run_command(self, command: str, cwd: Optional[str] = None, 
                   timeout: int = 30, shell: bool = True) -> Dict:
        """
        Execute a shell command
        
        Args:
            command: Command to execute
            cwd: Working directory (optional)
            timeout: Timeout in seconds
            shell: Run in shell (default True)
        
        Returns:
            Dictionary with status, output, and errors
        """
        # Safety check
        is_safe, reason = self.safety_checker.can_execute_command(command)
        if not is_safe:
            log_manager.log_action("run_command", command, "blocked")
            return {
                "success": False,
                "message": f"Command blocked: {reason}",
                "output": "",
                "error": reason
            }
        
        log_manager.log_action("run_command", command, "started")
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=shell,
                cwd=cwd,
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            success = result.returncode == 0
            status = "completed" if success else "failed"
            
            log_manager.log_action("run_command", command, status)
            
            return {
                "success": success,
                "message": f"Command {'succeeded' if success else 'failed'}",
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            log_manager.log_error("run_command", f"Command timed out: {command}")
            return {
                "success": False,
                "message": f"Command timed out after {timeout} seconds",
                "output": "",
                "error": "Timeout"
            }
        
        except Exception as e:
            log_manager.log_error("run_command", f"Command failed: {str(e)}")
            return {
                "success": False,
                "message": f"Command execution failed: {str(e)}",
                "output": "",
                "error": str(e)
            }
    
    def run_python_script(self, script_path: str, args: Optional[list] = None) -> Dict:
        """
        Run a Python script
        
        Args:
            script_path: Path to Python script
            args: Command-line arguments (optional)
        
        Returns:
            Dictionary with status and output
        """
        # Check if file exists
        if not Path(script_path).exists():
            return {
                "success": False,
                "message": f"Script not found: {script_path}",
                "output": "",
                "error": "File not found"
            }
        
        # Build command
        cmd = f"python \"{script_path}\""
        if args:
            cmd += " " + " ".join(f"\"{arg}\"" for arg in args)
        
        return self.run_command(cmd, cwd=Path(script_path).parent)
    
    def run_build_command(self, language: str, file_path: str) -> Dict:
        """
        Run build/execute command for a programming language
        
        Args:
            language: Programming language
            file_path: Source file path
        
        Returns:
            Dictionary with status and output
        """
        # Get build command template from config
        build_commands = self.config.get("desktop.projects.build_commands", {})
        
        if language.lower() not in build_commands:
            return {
                "success": False,
                "message": f"No build command configured for {language}",
                "output": "",
                "error": "Unsupported language"
            }
        
        # Get command template
        cmd_template = build_commands[language.lower()]
        
        # Replace placeholders
        file_obj = Path(file_path)
        cmd = cmd_template.format(
            file=file_path,
            class_name=file_obj.stem,
            output=file_obj.stem
        )
        
        return self.run_command(cmd, cwd=file_obj.parent)
    
    def get_working_directory(self) -> str:
        """Get current working directory"""
        return os.getcwd()
    
    def change_directory(self, path: str) -> Dict:
        """
        Change working directory
        
        Args:
            path: Directory path
        
        Returns:
            Dictionary with status and message
        """
        try:
            # Check if path is safe
            is_safe, reason = self.safety_checker.is_path_safe(path)
            if not is_safe:
                return {
                    "success": False,
                    "message": f"Cannot change to directory: {reason}"
                }
            
            os.chdir(path)
            log_manager.log_action("change_directory", path, "completed")
            
            return {
                "success": True,
                "message": f"Changed directory to {path}"
            }
        
        except Exception as e:
            log_manager.log_error("change_directory", str(e))
            return {
                "success": False,
                "message": f"Failed to change directory: {str(e)}"
            }


# Global shell executor instance
_shell_executor_instance = None


def get_shell_executor() -> ShellExecutor:
    """Get the global shell executor instance"""
    global _shell_executor_instance
    if _shell_executor_instance is None:
        _shell_executor_instance = ShellExecutor()
    return _shell_executor_instance

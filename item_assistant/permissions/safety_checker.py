"""
Safety Checker for Item AI Assistant
Enforces safety rules to prevent dangerous operations.
"""

import os
from pathlib import Path
from typing import List, Tuple

from item_assistant.config import get_config
from item_assistant.logging import get_logger

logger = get_logger()


class SafetyChecker:
    """Enforces safety rules for file and system operations"""
    
    def __init__(self):
        """Initialize safety checker"""
        self.config = get_config()
        
        # Get safe and forbidden folders from config
        self.safe_folders = [
            Path(f) for f in self.config.get("desktop.safe_folders", [])
        ]
        self.forbidden_folders = [
            Path(f) for f in self.config.get("desktop.forbidden_folders", [])
        ]
        
        logger.info(f"Safety checker initialized with {len(self.safe_folders)} safe folders "
                   f"and {len(self.forbidden_folders)} forbidden folders")
    
    def is_path_safe(self, path: str) -> Tuple[bool, str]:
        """
        Check if a file path is safe to access
        
        Args:
            path: File or directory path to check
        
        Returns:
            Tuple of (is_safe, reason)
        """
        try:
            path_obj = Path(path).resolve()
        except Exception as e:
            return False, f"Invalid path: {str(e)}"
        
        # Check if path is in forbidden folders
        for forbidden in self.forbidden_folders:
            try:
                path_obj.relative_to(forbidden)
                return False, f"Path is in forbidden system folder: {forbidden}"
            except ValueError:
                # Not in this forbidden folder, continue checking
                continue
        
        # For file operations, path should be in safe folders
        # (unless it's just reading)
        return True, "Path is safe"
    
    def can_delete_file(self, path: str) -> Tuple[bool, str]:
        """
        Check if a file can be deleted
        
        Args:
            path: File path
        
        Returns:
            Tuple of (can_delete, reason)
        """
        # First check if path is safe
        is_safe, reason = self.is_path_safe(path)
        if not is_safe:
            return False, reason
        
        # Check if file is in a safe folder
        path_obj = Path(path).resolve()
        in_safe_folder = False
        
        for safe in self.safe_folders:
            try:
                path_obj.relative_to(safe)
                in_safe_folder = True
                break
            except ValueError:
                continue
        
        if not in_safe_folder:
            return False, "File deletion only allowed in safe folders"
        
        return True, "File can be deleted"
    
    def can_modify_file(self, path: str) -> Tuple[bool, str]:
        """
        Check if a file can be modified
        
        Args:
            path: File path
        
        Returns:
            Tuple of (can_modify, reason)
        """
        return self.is_path_safe(path)
    
    def can_execute_command(self, command: str) -> Tuple[bool, str]:
        """
        Check if a shell command is safe to execute
        
        Args:
            command: Shell command to check
        
        Returns:
            Tuple of (can_execute, reason)
        """
        # List of dangerous commands/patterns
        dangerous_patterns = [
            "del ", "rm ", "rmdir",  # File deletion
            "format", "diskpart",  # Disk operations
            "reg ", "regedit",  # Registry operations
            "netsh", "ipconfig /release",  # Network config
            "shutdown", "restart",  # System power
            "taskkill /f",  # Force kill
            "attrib +h",  # Hide files
            "> null", "2>&1"  # Output redirection (can be used maliciously)
        ]
        
        command_lower = command.lower()
        
        for pattern in dangerous_patterns:
            if pattern.lower() in command_lower:
                return False, f"Command contains dangerous pattern: {pattern}"
        
        # Check for writing to forbidden folders
        for forbidden in self.forbidden_folders:
            if str(forbidden).lower() in command_lower:
                return False, f"Command targets forbidden folder: {forbidden}"
        
        return True, "Command appears safe (confirmation still required)"
    
    def needs_confirmation(self, action: str) -> bool:
        """
        Check if an action requires user confirmation
        
        Args:
            action: Action type (e.g., "close_app", "run_command")
        
        Returns:
            True if confirmation required
        """
        required_confirmations = self.config.get("security.require_confirmation_for", [])
        return action in required_confirmations


# Global safety checker instance
_safety_checker_instance = None


def get_safety_checker() -> SafetyChecker:
    """Get the global safety checker instance"""
    global _safety_checker_instance
    if _safety_checker_instance is None:
        _safety_checker_instance = SafetyChecker()
    return _safety_checker_instance

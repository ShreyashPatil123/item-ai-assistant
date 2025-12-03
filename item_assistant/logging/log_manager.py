"""
Logging Manager for Item AI Assistant
Provides comprehensive logging with daily rotation and structured output.
"""

import os
import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from item_assistant.config import get_config


class LogManager:
    """Manages application logging with file and console output"""
    
    def __init__(self):
        """Initialize logging system"""
        self.config = get_config()
        self.log_dir = Path(self.config.get("system.log_directory"))
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """
        Set up the main application logger
        
        Returns:
            Configured logger instance
        """
        # Create logger
        logger = logging.getLogger("item_assistant")
        
        # Get log level from config
        log_level_str = self.config.get("logging.level", "INFO")
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Get log format
        log_format = self.config.get("logging.format",
                                     "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        
        # Console handler
        if self.config.get("logging.console_output", True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.config.get("logging.file_output", True):
            # Create daily log file
            log_filename = self._get_log_filename()
            log_filepath = self.log_dir / log_filename
            
            max_bytes = self.config.get("logging.max_file_size_mb", 10) * 1024 * 1024
            backup_count = self.config.get("logging.backup_count", 30)
            
            file_handler = RotatingFileHandler(
                log_filepath,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        logger.info("=" * 80)
        logger.info("Item AI Assistant - Logging System Initialized")
        logger.info("=" * 80)
        
        return logger
    
    def _get_log_filename(self) -> str:
        """
        Get the current log filename based on date
        
        Returns:
            Log filename (e.g., "2025-12-01.log")
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return f"{today}.log"
    
    def log_command(self, command: str, source: str, language: Optional[str] = None):
        """
        Log a user command
        
        Args:
            command: The command text
            source: Source of command ("laptop", "phone", "api")
            language: Detected language (optional)
        """
        lang_str = f" [{language}]" if language else ""
        self.logger.info(f"COMMAND [{source}]{lang_str}: {command}")
    
    def log_action(self, action: str, target: str, status: str = "started"):
        """
        Log an action being performed
        
        Args:
            action: Action type (e.g., "open_app", "run_command")
            target: Target of action (e.g., app name, command)
            status: Action status ("started", "completed", "failed")
        """
        self.logger.info(f"ACTION [{action}] {status.upper()}: {target}")
    
    def log_confirmation(self, prompt: str, user_response: bool):
        """
        Log a confirmation prompt and response
        
        Args:
            prompt: Confirmation prompt shown to user
            user_response: User's response (True = confirmed, False = denied)
        """
        response_str = "CONFIRMED" if user_response else "DENIED"
        self.logger.info(f"CONFIRMATION [{response_str}]: {prompt}")
    
    def log_llm_call(self, provider: str, model: str, prompt_length: int, success: bool):
        """
        Log an LLM API call
        
        Args:
            provider: LLM provider ("local", "groq", "gemini")
            model: Model name
            prompt_length: Length of prompt in characters
            success: Whether call succeeded
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"LLM [{provider}/{model}] {status}: prompt_length={prompt_length}")
    
    def log_error(self, error_type: str, message: str, exception: Optional[Exception] = None):
        """
        Log an error
        
        Args:
            error_type: Type of error
            message: Error message
            exception: Exception object (optional)
        """
        error_msg = f"ERROR [{error_type}]: {message}"
        if exception:
            self.logger.error(error_msg, exc_info=True)
        else:
            self.logger.error(error_msg)
    
    def get_recent_logs(self, lines: int = 100) -> str:
        """
        Get recent log entries
        
        Args:
            lines: Number of lines to retrieve
        
        Returns:
            Recent log content
        """
        log_filename = self._get_log_filename()
        log_filepath = self.log_dir / log_filename
        
        if not log_filepath.exists():
            return "No log file found for today."
        
        try:
            with open(log_filepath, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:]
                return ''.join(recent_lines)
        except Exception as e:
            return f"Error reading log file: {str(e)}"
    
    def get_logger(self) -> logging.Logger:
        """
        Get the logger instance
        
        Returns:
            Logger instance
        """
        return self.logger


# Global log manager instance
_log_manager_instance: Optional[LogManager] = None


def get_logger() -> logging.Logger:
    """Get the global logger instance"""
    global _log_manager_instance
    if _log_manager_instance is None:
        _log_manager_instance = LogManager()
    return _log_manager_instance.get_logger()


def get_log_manager() -> LogManager:
    """Get the global log manager instance"""
    global _log_manager_instance
    if _log_manager_instance is None:
        _log_manager_instance = LogManager()
    return _log_manager_instance

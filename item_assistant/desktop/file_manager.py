"""
File Manager for Item AI Assistant
Handles file operations with safety checks and path restrictions.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from item_assistant.config import get_config
from item_assistant.logging import get_log_manager
from item_assistant.permissions import get_safety_checker

logger = get_log_manager().get_logger()
log_manager = get_log_manager()


class FileManager:
    """Manages file operations with safety checks"""
    
    def __init__(self):
        """Initialize file manager"""
        self.config = get_config()
        self.safety_checker = get_safety_checker()
        
        # Get safe folders from config
        self.safe_folders = self.config.get("desktop.safe_folders", [])
        logger.info(f"File manager initialized with {len(self.safe_folders)} safe folders")
    
    def _is_path_safe(self, path: str) -> tuple[bool, str]:
        """
        Check if a path is within safe folders
        
        Args:
            path: Path to check
        
        Returns:
            Tuple of (is_safe, reason)
        """
        return self.safety_checker.is_path_safe(path)
    
    def create_file(self, filepath: str, content: str = "") -> Dict:
        """
        Create a new file with optional content
        
        Args:
            filepath: Path to the file
            content: Initial content (optional)
        
        Returns:
            Dictionary with status and message
        """
        is_safe, reason = self._is_path_safe(filepath)
        if not is_safe:
            log_manager.log_action("create_file", filepath, "blocked")
            return {
                "success": False,
                "message": f"Cannot create file: {reason}"
            }
        
        log_manager.log_action("create_file", filepath, "started")
        
        try:
            file_path = Path(filepath)
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            log_manager.log_action("create_file", filepath, "completed")
            
            return {
                "success": True,
                "message": f"Created file: {filepath}",
                "data": {"path": str(file_path)}
            }
        except Exception as e:
            log_manager.log_error("create_file", str(e))
            return {
                "success": False,
                "message": f"Failed to create file: {str(e)}"
            }
    
    def copy_file(self, source: str, destination: str) -> Dict:
        """
        Copy a file
        
        Args:
            source: Source file path
            destination: Destination file path
        
        Returns:
            Dictionary with status and message
        """
        # Check both paths are safe
        is_safe_src, reason_src = self._is_path_safe(source)
        is_safe_dst, reason_dst = self._is_path_safe(destination)
        
        if not is_safe_src:
            return {
                "success": False,
                "message": f"Cannot access source: {reason_src}"
            }
        
        if not is_safe_dst:
            return {
                "success": False,
                "message": f"Cannot access destination: {reason_dst}"
            }
        
        log_manager.log_action("copy_file", f"{source} -> {destination}", "started")
        
        try:
            src_path = Path(source)
            dst_path = Path(destination)
            
            if not src_path.exists():
                return {
                    "success": False,
                    "message": f"Source file not found: {source}"
                }
            
            # Create destination directory if needed
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(src_path, dst_path)
            
            log_manager.log_action("copy_file", f"{source} -> {destination}", "completed")
            
            return {
                "success": True,
                "message": f"Copied {src_path.name} to {dst_path}"
            }
        except Exception as e:
            log_manager.log_error("copy_file", str(e))
            return {
                "success": False,
                "message": f"Failed to copy file: {str(e)}"
            }
    
    def move_file(self, source: str, destination: str) -> Dict:
        """
        Move a file
        
        Args:
            source: Source file path
            destination: Destination file path
        
        Returns:
            Dictionary with status and message
        """
        # Check both paths are safe
        is_safe_src, reason_src = self._is_path_safe(source)
        is_safe_dst, reason_dst = self._is_path_safe(destination)
        
        if not is_safe_src:
            return {
                "success": False,
                "message": f"Cannot access source: {reason_src}"
            }
        
        if not is_safe_dst:
            return {
                "success": False,
                "message": f"Cannot access destination: {reason_dst}"
            }
        
        log_manager.log_action("move_file", f"{source} -> {destination}", "started")
        
        try:
            src_path = Path(source)
            dst_path = Path(destination)
            
            if not src_path.exists():
                return {
                    "success": False,
                    "message": f"Source file not found: {source}"
                }
            
            # Create destination directory if needed
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(src_path), str(dst_path))
            
            log_manager.log_action("move_file", f"{source} -> {destination}", "completed")
            
            return {
                "success": True,
                "message": f"Moved {src_path.name} to {dst_path}"
            }
        except Exception as e:
            log_manager.log_error("move_file", str(e))
            return {
                "success": False,
                "message": f"Failed to move file: {str(e)}"
            }
    
    def delete_file(self, filepath: str, force: bool = False) -> Dict:
        """
        Delete a file (restricted to safe folders)
        
        Args:
            filepath: Path to the file
            force: Force delete without confirmation
        
        Returns:
            Dictionary with status and message
        """
        is_safe, reason = self._is_path_safe(filepath)
        if not is_safe:
            log_manager.log_action("delete_file", filepath, "blocked")
            return {
                "success": False,
                "message": f"Cannot delete file: {reason}"
            }
        
        log_manager.log_action("delete_file", filepath, "started")
        
        try:
            file_path = Path(filepath)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {filepath}"
                }
            
            # Delete file
            file_path.unlink()
            
            log_manager.log_action("delete_file", filepath, "completed")
            
            return {
                "success": True,
                "message": f"Deleted file: {filepath}"
            }
        except Exception as e:
            log_manager.log_error("delete_file", str(e))
            return {
                "success": False,
                "message": f"Failed to delete file: {str(e)}"
            }
    
    def create_directory(self, dirpath: str) -> Dict:
        """
        Create a directory
        
        Args:
            dirpath: Path to the directory
        
        Returns:
            Dictionary with status and message
        """
        is_safe, reason = self._is_path_safe(dirpath)
        if not is_safe:
            log_manager.log_action("create_directory", dirpath, "blocked")
            return {
                "success": False,
                "message": f"Cannot create directory: {reason}"
            }
        
        log_manager.log_action("create_directory", dirpath, "started")
        
        try:
            dir_path = Path(dirpath)
            dir_path.mkdir(parents=True, exist_ok=True)
            
            log_manager.log_action("create_directory", dirpath, "completed")
            
            return {
                "success": True,
                "message": f"Created directory: {dirpath}"
            }
        except Exception as e:
            log_manager.log_error("create_directory", str(e))
            return {
                "success": False,
                "message": f"Failed to create directory: {str(e)}"
            }
    
    def list_directory(self, dirpath: str) -> Dict:
        """
        List contents of a directory
        
        Args:
            dirpath: Path to the directory
        
        Returns:
            Dictionary with file list
        """
        is_safe, reason = self._is_path_safe(dirpath)
        if not is_safe:
            return {
                "success": False,
                "message": f"Cannot access directory: {reason}"
            }
        
        try:
            dir_path = Path(dirpath)
            
            if not dir_path.exists():
                return {
                    "success": False,
                    "message": f"Directory not found: {dirpath}"
                }
            
            if not dir_path.is_dir():
                return {
                    "success": False,
                    "message": f"Path is not a directory: {dirpath}"
                }
            
            # List contents
            items = []
            for item in dir_path.iterdir():
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            
            # Sort: directories first, then files
            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            
            return {
                "success": True,
                "data": {"items": items, "count": len(items)},
                "message": f"Found {len(items)} items in {dirpath}"
            }
        except Exception as e:
            log_manager.log_error("list_directory", str(e))
            return {
                "success": False,
                "message": f"Failed to list directory: {str(e)}"
            }
    
    def get_file_info(self, filepath: str) -> Dict:
        """
        Get information about a file
        
        Args:
            filepath: Path to the file
        
        Returns:
            Dictionary with file information
        """
        try:
            file_path = Path(filepath)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {filepath}"
                }
            
            stat = file_path.stat()
            
            info = {
                "name": file_path.name,
                "path": str(file_path),
                "is_dir": file_path.is_dir(),
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": file_path.suffix
            }
            
            return {
                "success": True,
                "data": info,
                "message": f"File info for {file_path.name}"
            }
        except Exception as e:
            log_manager.log_error("get_file_info", str(e))
            return {
                "success": False,
                "message": f"Failed to get file info: {str(e)}"
            }
    
    def search_files(self, directory: str, pattern: str) -> Dict:
        """
        Search for files matching a pattern
        
        Args:
            directory: Directory to search in
            pattern: File name pattern (supports wildcards)
        
        Returns:
            Dictionary with matching files
        """
        is_safe, reason = self._is_path_safe(directory)
        if not is_safe:
            return {
                "success": False,
                "message": f"Cannot search directory: {reason}"
            }
        
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists() or not dir_path.is_dir():
                return {
                    "success": False,
                    "message": f"Invalid directory: {directory}"
                }
            
            # Search for files
            matches = list(dir_path.glob(f"**/{pattern}"))
            
            results = []
            for match in matches:
                results.append({
                    "name": match.name,
                    "path": str(match),
                    "is_dir": match.is_dir(),
                    "size": match.stat().st_size if match.is_file() else 0
                })
            
            return {
                "success": True,
                "data": {"matches": results, "count": len(results)},
                "message": f"Found {len(results)} matches for '{pattern}'"
            }
        except Exception as e:
            log_manager.log_error("search_files", str(e))
            return {
                "success": False,
                "message": f"Search failed: {str(e)}"
            }


# Global file manager instance
_file_manager_instance = None


def get_file_manager() -> FileManager:
    """Get the global file manager instance"""
    global _file_manager_instance
    if _file_manager_instance is None:
        _file_manager_instance = FileManager()
    return _file_manager_instance

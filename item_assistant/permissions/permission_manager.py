"""
Permission Manager for Item AI Assistant
Manages per-app permissions and user consent.
"""

import json
from pathlib import Path
from typing import Dict, Optional

from item_assistant.config import get_config
from item_assistant.logging import get_logger

logger = get_logger()


class PermissionManager:
    """Manages application control permissions"""
    
    def __init__(self):
        """Initialize permission manager"""
        self.config = get_config()
        
        # Get permissions file path
        perms_filename = self.config.get("permissions.permissions_file", "allowed_apps.json")
        config_dir = Path(__file__).parent.parent / "config"
        self.permissions_file = config_dir / perms_filename
        
        # Load permissions
        self.permissions: Dict[str, bool] = self._load_permissions()
        
        # Get auto-approved and blocked apps
        self.auto_approved = self.config.get("permissions.auto_approved_apps", [])
        self.blocked_apps = self.config.get("permissions.blocked_apps", [])
        
        logger.info(f"Permission manager initialized with {len(self.permissions)} stored permissions")
    
    def _load_permissions(self) -> Dict[str, bool]:
        """
        Load permissions from file
        
        Returns:
            Dictionary of app permissions
        """
        # Check if permissions file exists
        if not self.permissions_file.exists():
            # Try to copy from template
            template_file = self.permissions_file.parent / "allowed_apps.template.json"
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                with open(self.permissions_file, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                logger.info(f"Created permissions file from template")
            else:
                # Create empty permissions file
                with open(self.permissions_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                logger.info(f"Created new permissions file")
        
        # Load permissions
        try:
            with open(self.permissions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading permissions: {e}")
            return {}
    
    def _save_permissions(self):
        """Save permissions to file"""
        try:
            with open(self.permissions_file, 'w', encoding='utf-8') as f:
                json.dump(self.permissions, f, indent=2)
            logger.info(f"Saved permissions to {self.permissions_file}")
        except Exception as e:
            logger.error(f"Error saving permissions: {e}")
    
    def is_app_allowed(self, app_name: str) -> Optional[bool]:
        """
        Check if an app is allowed to be controlled
        
        Args:
            app_name: Name of the application (lowercase)
        
        Returns:
            True if allowed, False if denied, None if not yet decided
        """
        app_name_lower = app_name.lower()
        
        # Check if app is blocked
        if app_name_lower in [a.lower() for a in self.blocked_apps]:
            logger.warning(f"App '{app_name}' is in blocked list")
            return False
        
        # Check if app is auto-approved
        if app_name_lower in [a.lower() for a in self.auto_approved]:
            return True
        
        # Check stored permissions
        if app_name_lower in self.permissions:
            return self.permissions[app_name_lower]
        
        # Not yet decided
        return None
    
    def request_permission(self, app_name: str) -> bool:
        """
        Request permission to control an app (placeholder for actual UI)
        
        This would normally show a UI dialog or voice prompt.
        For now, it returns True by default (you'll implement the UI layer later)
        
        Args:
            app_name: Name of the application
        
        Returns:
            True if permission granted, False otherwise
        """
        app_name_lower = app_name.lower()
        
        logger.info(f"Permission request for app: {app_name}")
        
        # In a real implementation, this would:
        # 1. Show a popup or speak: "Can I control {app_name}? [Yes/No]"
        # 2. Wait for user response (voice or button click)
        # 3. Store the decision
        
        # For now, auto-grant (you'll replace this with actual UI)
        granted = True
        
        # Store the decision
        self.permissions[app_name_lower] = granted
        self._save_permissions()
        
        logger.info(f"Permission {'granted' if granted else 'denied'} for app: {app_name}")
        
        return granted
    
    def grant_permission(self, app_name: str):
        """
        Manually grant permission for an app
        
        Args:
            app_name: Name of the application
        """
        app_name_lower = app_name.lower()
        self.permissions[app_name_lower] = True
        self._save_permissions()
        logger.info(f"Manually granted permission for app: {app_name}")
    
    def deny_permission(self, app_name: str):
        """
        Manually deny permission for an app
        
        Args:
            app_name: Name of the application
        """
        app_name_lower = app_name.lower()
        self.permissions[app_name_lower] = False
        self._save_permissions()
        logger.info(f"Manually denied permission for app: {app_name}")
    
    def revoke_permission(self, app_name: str):
        """
        Revoke permission for an app (remove from list)
        
        Args:
            app_name: Name of the application
        """
        app_name_lower = app_name.lower()
        if app_name_lower in self.permissions:
            del self.permissions[app_name_lower]
            self._save_permissions()
            logger.info(f"Revoked permission for app: {app_name}")
    
    def list_permissions(self) -> Dict[str, bool]:
        """
        Get all stored permissions
        
        Returns:
            Dictionary of app permissions
        """
        return self.permissions.copy()
    
    def check_and_request_permission(self, app_name: str) -> bool:
        """
        Check permission and request if not yet decided
        
        Args:
            app_name: Name of the application
        
        Returns:
            True if allowed (either already or newly granted)
        """
        permission = self.is_app_allowed(app_name)
        
        if permission is None:
            # Not yet decided, request permission
            return self.request_permission(app_name)
        
        return permission


# Global permission manager instance
_permission_manager_instance = None


def get_permission_manager() -> PermissionManager:
    """Get the global permission manager instance"""
    global _permission_manager_instance
    if _permission_manager_instance is None:
        _permission_manager_instance = PermissionManager()
    return _permission_manager_instance

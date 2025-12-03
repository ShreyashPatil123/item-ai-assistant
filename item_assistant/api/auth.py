"""
Authentication middleware
Token-based authentication for API endpoints.
"""

from fastapi import Header, HTTPException, status
from typing import Optional

from item_assistant.config import get_config
from item_assistant.logging import get_logger

logger = get_logger()


class AuthManager:
    """Manages authentication for API"""
    
    def __init__(self):
        """Initialize auth manager"""
        self.config = get_config()
        self.auth_token = self.config.get("security.auth_token", "")
        self.enable_ip_whitelist = self.config.get("security.enable_ip_whitelist", False)
        self.allowed_ips = self.config.get("security.allowed_ips", [])
        
        logger.info(f"Auth manager initialized (IP whitelist: {self.enable_ip_whitelist})")
    
    def verify_token(self, authorization: Optional[str] = None) -> bool:
        """
        Verify authorization token
        
        Args:
            authorization: Authorization header value
        
        Returns:
            True if valid
        """
        if not authorization:
            return False
        
        # Expected format: "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return False
        
        token = parts[1]
        return token == self.auth_token
    
    def verify_ip(self, client_ip: str) -> bool:
        """
        Verify client IP against whitelist
        
        Args:
            client_ip: Client IP address
        
        Returns:
            True if allowed
        """
        if not self.enable_ip_whitelist:
            return True
        
        # Simple IP matching (for subnet, use ipaddress module)
        for allowed in self.allowed_ips:
            if allowed in client_ip or client_ip.startswith(allowed.replace("/24", "")):
                return True
        
        return False


# Dependency for FastAPI routes
async def verify_auth(authorization: Optional[str] = Header(None)):
    """FastAPI dependency for auth verification"""
    auth_manager = get_auth_manager()
    
    if not auth_manager.verify_token(authorization):
        logger.warning(f"Unauthorized access attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return True


# Global auth manager instance
_auth_manager_instance = None


def get_auth_manager() -> AuthManager:
    """Get the global auth manager instance"""
    global _auth_manager_instance
    if _auth_manager_instance is None:
        _auth_manager_instance = AuthManager()
    return _auth_manager_instance

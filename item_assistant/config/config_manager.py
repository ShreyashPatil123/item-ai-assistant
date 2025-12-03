"""
Configuration Manager for Item AI Assistant
Handles loading, validation, and access to configuration settings.
"""

import os
import yaml
import secrets
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import getnode


class ConfigManager:
    """Manages application configuration from YAML file"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to config.yaml (defaults to config/config.yaml)
        """
        if config_path is None:
            config_dir = Path(__file__).parent
            config_path = config_dir / "config.yaml"
        
        self.config_path = Path(config_path)
        self.template_path = Path(__file__).parent / "config.template.yaml"
        self.config: Dict[str, Any] = {}
        
        # Load or create config
        self._load_or_create_config()
        
        # Ensure required directories exist
        self._ensure_directories()
        
        # Auto-generate missing values
        self._auto_generate_values()
    
    def _load_or_create_config(self):
        """Load config from file or create from template"""
        if not self.config_path.exists():
            print(f"Config file not found. Creating from template...")
            
            # Copy template to config.yaml
            if self.template_path.exists():
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                
                print(f"✓ Created config file at: {self.config_path}")
            else:
                raise FileNotFoundError(f"Template config not found: {self.template_path}")
        
        # Load the config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        print(f"✓ Loaded configuration from: {self.config_path}")
    
    def _ensure_directories(self):
        """Create required directories if they don't exist"""
        log_dir = Path(self.get("system.log_directory"))
        data_dir = Path(self.get("system.data_directory"))
        
        log_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✓ Ensured directories exist")
    
    def _auto_generate_values(self):
        """Auto-generate missing configuration values"""
        updated = False
        
        # Generate auth token if missing
        if not self.get("security.auth_token"):
            token = secrets.token_urlsafe(32)
            self.set("security.auth_token", token)
            updated = True
            print(f"✓ Generated auth token: {token[:16]}...")
        
        # Detect MAC address for Wake-on-LAN
        if not self.get("wol.mac_address"):
            mac = self._get_mac_address()
            if mac:
                self.set("wol.mac_address", mac)
                updated = True
                print(f"✓ Detected MAC address: {mac}")
        
        # Save if updated
        if updated:
            self.save()
    
    def _get_mac_address(self) -> str:
        """Get the MAC address of this machine"""
        mac_num = getnode()
        mac_hex = ':'.join(['{:02x}'.format((mac_num >> elements) & 0xff)
                           for elements in range(0, 8*6, 8)][::-1])
        return mac_hex.upper()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., "llm.local.models.general")
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., "llm.local.models.general")
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """Save configuration to file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        
        print(f"✓ Saved configuration to: {self.config_path}")
    
    def reload(self):
        """Reload configuration from file"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        print(f"✓ Reloaded configuration")
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary"""
        return self.config.copy()
    
    def validate(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        errors = []
        
        # Check required API keys if services are enabled
        if self.get("voice.wake_word.enabled") and not self.get("voice.wake_word.access_key"):
            errors.append("Picovoice access key required when wake word is enabled")
        
        if self.get("llm.online.groq.enabled") and not self.get("llm.online.groq.api_key"):
            errors.append("Groq API key required when Groq is enabled")
        
        if self.get("llm.online.gemini.enabled") and not self.get("llm.online.gemini.api_key"):
            errors.append("Google Gemini API key required when Gemini is enabled")
        
        # Check directories exist
        for key in ["system.log_directory", "system.data_directory"]:
            dir_path = Path(self.get(key))
            if not dir_path.exists():
                errors.append(f"Directory does not exist: {dir_path}")
        
        if errors:
            raise ValueError("Configuration validation failed:\n- " + "\n- ".join(errors))
        
        return True


# Global config instance
_config_instance: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def reload_config():
    """Reload the global configuration"""
    global _config_instance
    if _config_instance is not None:
        _config_instance.reload()

"""Configuration and data validation utilities."""

import re
from typing import Optional, List, Tuple
from pathlib import Path


class ConfigValidator:
    """Validator for application configuration."""
    
    # Common IMAP server ports
    COMMON_IMAP_SERVERS = {
        'imap.gmail.com': 993,
        'imap.163.com': 993,
        'imap.qq.com': 993,
        'imap.outlook.com': 993,
        'imap.mail.yahoo.com': 993,
    }
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email address is required"
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, f"Invalid email format: {email}"
        
        return True, None
    
    @staticmethod
    def validate_imap_url(imap_url: str) -> Tuple[bool, Optional[str]]:
        """Validate IMAP server URL.
        
        Args:
            imap_url: IMAP server URL to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not imap_url:
            return False, "IMAP URL is required"
        
        # Check if it's a known IMAP server
        if imap_url in ConfigValidator.COMMON_IMAP_SERVERS:
            return True, None
        
        # Check for basic domain format
        pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, imap_url):
            return False, f"Invalid IMAP server format: {imap_url}"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str, field_name: str = "Password") -> Tuple[bool, Optional[str]]:
        """Validate password is not empty.
        
        Args:
            password: Password to validate
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, f"{field_name} is required"
        
        if len(password) < 6:
            return False, f"{field_name} must be at least 6 characters"
        
        return True, None
    
    @staticmethod
    def validate_notion_token(token: str) -> Tuple[bool, Optional[str]]:
        """Validate Notion API token format.
        
        Args:
            token: Notion integration token
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not token:
            return False, "Notion token is required"
        
        # Notion tokens typically start with 'secret_' and are quite long
        if not token.startswith('secret_'):
            return False, "Notion token should start with 'secret_'"
        
        if len(token) < 50:
            return False, "Notion token appears to be too short"
        
        return True, None
    
    @staticmethod
    def validate_notion_data_source_id(data_source_id: str) -> Tuple[bool, Optional[str]]:
        """Validate Notion data source ID format.
        
        Args:
            data_source_id: Notion data source ID
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not data_source_id:
            return False, "Notion data source ID is required"
        
        # Data source IDs are UUIDs without dashes (32 hex characters)
        if len(data_source_id) not in [32, 36]:  # With or without dashes
            return False, f"Notion data source ID has invalid length: {len(data_source_id)}"
        
        # Remove dashes and check if it's valid hex
        clean_id = data_source_id.replace('-', '')
        if not re.match(r'^[a-f0-9]{32}$', clean_id, re.IGNORECASE):
            return False, "Notion data source ID must be a valid UUID"
        
        return True, None
    
    @staticmethod
    def validate_config(
        username: str,
        password: str,
        imap_url: str,
        data_source_id: str,
        token: str
    ) -> List[str]:
        """Validate all configuration parameters.
        
        Args:
            username: Email username
            password: Email password
            imap_url: IMAP server URL
            data_source_id: Notion data source ID
            token: Notion integration token
            
        Returns:
            List of error messages (empty if all valid)
            
        Raises:
            ConfigurationError: If validation fails
        """
        errors = []
        
        # Validate email username
        valid, error = ConfigValidator.validate_email(username)
        if not valid:
            errors.append(f"EMAIL_USERNAME: {error}")
        
        # Validate email password
        valid, error = ConfigValidator.validate_password(password, "EMAIL_PASSWORD")
        if not valid:
            errors.append(f"EMAIL_PASSWORD: {error}")
        
        # Validate IMAP URL
        valid, error = ConfigValidator.validate_imap_url(imap_url)
        if not valid:
            errors.append(f"EMAIL_IMAP_URL: {error}")
        
        # Validate Notion data source ID
        valid, error = ConfigValidator.validate_notion_data_source_id(data_source_id)
        if not valid:
            errors.append(f"NOTION_DATA_SOURCE_ID: {error}")
        
        # Validate Notion token
        valid, error = ConfigValidator.validate_notion_token(token)
        if not valid:
            errors.append(f"NOTION_TOKEN: {error}")
        
        if errors:
            # Import here to avoid circular dependency
            from src.core.exceptions import ConfigurationError
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ConfigurationError(error_msg)
        
        return errors


class PathValidator:
    """Validator for file system paths."""
    
    @staticmethod
    def validate_directory_writable(path: Path) -> Tuple[bool, Optional[str]]:
        """Check if directory exists and is writable.
        
        Args:
            path: Directory path to check
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            
            # Try to create a test file
            test_file = path / '.write_test'
            try:
                test_file.touch()
                test_file.unlink()
                return True, None
            except Exception as e:
                return False, f"Directory is not writable: {e}"
                
        except Exception as e:
            return False, f"Cannot create directory: {e}"
    
    @staticmethod
    def validate_file_readable(path: Path) -> Tuple[bool, Optional[str]]:
        """Check if file exists and is readable.
        
        Args:
            path: File path to check
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not path.exists():
            return False, f"File does not exist: {path}"
        
        if not path.is_file():
            return False, f"Path is not a file: {path}"
        
        try:
            with open(path, 'r') as f:
                f.read(1)
            return True, None
        except Exception as e:
            return False, f"File is not readable: {e}"


class PlatformValidator:
    """Validator for payment platform parameters."""
    
    SUPPORTED_PLATFORMS = ['alipay', 'wechatpay']
    
    @staticmethod
    def validate_platform(platform: str) -> Tuple[bool, Optional[str]]:
        """Validate payment platform name.
        
        Args:
            platform: Platform name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not platform:
            return False, "Platform name is required"
        
        if platform not in PlatformValidator.SUPPORTED_PLATFORMS:
            return False, (
                f"Unsupported platform: {platform}. "
                f"Supported platforms: {', '.join(PlatformValidator.SUPPORTED_PLATFORMS)}"
            )
        
        return True, None

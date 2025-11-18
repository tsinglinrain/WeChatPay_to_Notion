import os
from pathlib import Path
import shutil
from typing import Tuple
from dotenv import load_dotenv

def _ensure_env_file_exists():
    """Ensures the .env file exists by copying it from .env.template if needed."""
    env_file = Path('.env')
    template_file = Path('.env.template')

    if not env_file.exists():
        try:
            shutil.copy(template_file, env_file)
            print("Copied .env.template to .env. Please review and update it.")
        except FileNotFoundError:
            # Import here to avoid circular dependency
            from src.core.exceptions import ConfigurationError
            raise ConfigurationError("'.env.template' not found. Please create one.")

def load_config(validate: bool = True) -> Tuple[str, str, str, str, str]:
    """Loads all necessary configurations from the .env file.
    
    Args:
        validate: Whether to validate configuration (default: True)
        
    Returns:
        Tuple of (username, password, imap_url, data_source_id, token)
        
    Raises:
        ConfigurationError: If configuration is missing or invalid
    """
    # Import here to avoid circular dependency
    from src.core.exceptions import ConfigurationError
    from src.utils.validators import ConfigValidator
    
    _ensure_env_file_exists()
    load_dotenv()

    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')
    imap_url = os.getenv('EMAIL_IMAP_URL')
    data_source_id = os.getenv('NOTION_DATA_SOURCE_ID')
    token = os.getenv('NOTION_TOKEN')

    # Check for missing values
    missing = []
    if not username:
        missing.append('EMAIL_USERNAME')
    if not password:
        missing.append('EMAIL_PASSWORD')
    if not imap_url:
        missing.append('EMAIL_IMAP_URL')
    if not data_source_id:
        missing.append('NOTION_DATA_SOURCE_ID')
    if not token:
        missing.append('NOTION_TOKEN')
    
    if missing:
        raise ConfigurationError(
            f"Missing required environment variables in .env file:\n" +
            "\n".join(f"  - {var}" for var in missing)
        )
    
    # Validate configuration if requested
    if validate:
        ConfigValidator.validate_config(
            username, password, imap_url, data_source_id, token
        )

    return username, password, imap_url, data_source_id, token

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
            raise Exception("'.env.template' not found. Please create one.")

def load_config() -> Tuple[str, str, str, str, str]:
    """Loads all necessary configurations from the .env file."""
    _ensure_env_file_exists()
    load_dotenv()

    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')
    imap_url = os.getenv('EMAIL_IMAP_URL')
    data_source_id = os.getenv('NOTION_DATA_SOURCE_ID')
    token = os.getenv('NOTION_TOKEN')

    if not all([username, password, imap_url, data_source_id, token]):
        raise ValueError("Missing one or more required environment variables in .env file.")

    return username, password, imap_url, data_source_id, token

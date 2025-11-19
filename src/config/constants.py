from pathlib import Path

# Directory and filename constants
DATA_PATH = Path("./data")
RAW_PATH = Path("raw")
PROCESSED_PATH = Path("processed")
ATTACHMENT_DIR = DATA_PATH / RAW_PATH / "attachment"
BILL_RAW_DIR = DATA_PATH / RAW_PATH / "csv"
PROCESSED_DIR = DATA_PATH / PROCESSED_PATH
PROJECT_ROOT = Path(".")

# Filename prefixes / templates (can be overridden by envs later)
RAW_FILENAME_PREFIX = {
    "alipay": "alipay_raw",
    "wechatpay": "wechatpay_raw",
}

STD_FILENAME_TEMPLATE = "{platform}_standard.csv"

def ensure_dirs():
    """Ensure base directories exist."""
    ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)
    BILL_RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

from pathlib import Path

# Directory and filename constants
ATTACHMENT_DIR = Path("attachment")
BILL_RAW_DIR = Path("bill_csv_raw")
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

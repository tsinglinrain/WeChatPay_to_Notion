from pathlib import Path

# Directory and filename constants
data_path = Path("./data")
ATTACHMENT_DIR = data_path / "attachment"
BILL_RAW_DIR = data_path / "bill_csv_raw"
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

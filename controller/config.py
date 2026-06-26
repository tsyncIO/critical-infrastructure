import os

WINDOWS_HOST = "http://127.0.0.1:5000"
OPENBMC_HOST = "http://127.0.0.1:5001"
LOG_DIR = "logs"
REPORT_DIR = "reports"


def ensure_dirs():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
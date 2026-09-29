import logging
import os
from datetime  import datetime

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

_run_started_at = datetime.now().strftime("%y%m%d_%H%M%S")

RUN_LOG_FILE = os.path.join(LOGS_DIR,f"run_{_run_started_at}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(RUN_LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
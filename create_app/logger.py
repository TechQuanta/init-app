import logging
import os
from pathlib import Path

# --- SETUP LOG DIRECTORY ---
LOG_DIR = Path.cwd() / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "py-create.log"

class CustomLogger:
    def __init__(self):
        self.logger = logging.getLogger("py_create")
        self.logger.setLevel(logging.DEBUG)

        # Prevent double logging if logger is already initialized
        if not self.logger.handlers:
            # 1. File Handler (Detailed logs)
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s | %(message)s'
            )
            file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)

            # 2. Console Handler (Brief logs for the dev)
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO) # Change to DEBUG to see everything
            console_handler.setFormatter(console_formatter)

            self.logger.addHandler(file_handler)
            # Optional: Uncomment if you want raw logs in console alongside your UI
            # self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

# Global Instance
logger = CustomLogger().get_logger()
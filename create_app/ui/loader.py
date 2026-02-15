import time
import itertools
import threading
import sys
from colorama import Fore, Style

# 🟢 IMPORT YOUR CUSTOM LOGGER FROM logger.py
from create_app.ui.logger import logger

class Spinner:
    def __init__(self, message="Processing"):
        self.message = message
        self.spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        self.running = False
        self.thread = None
        self.start_time = None

    def start(self):
        # 🪵 Log the start event to your .py-create.log
        logger.info(f"🌀 Spinner started: {self.message}")
        self.start_time = time.time()
        self.running = True
        self.thread = threading.Thread(target=self.animate, daemon=True)
        self.thread.start()

    def animate(self):
        while self.running:
            sys.stdout.write(
                f"\r{Fore.CYAN}{next(self.spinner)}{Style.RESET_ALL} "
                f"{Fore.WHITE}{Style.DIM}{self.message}...{Style.RESET_ALL}\033[K"
            )
            sys.stdout.flush()
            time.sleep(0.08)

    def stop(self, success=True):
        self.running = False
        if self.thread:
            self.thread.join()
        
        # ⏱️ Calculate how long the process took
        duration = time.time() - self.start_time if self.start_time else 0
        
        # 🪵 Log the completion and duration to the file
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"🌀 Spinner stopped: {self.message} | Status: {status} | Duration: {duration:.2f}s")
        
        icon = f"{Fore.GREEN}✔{Style.RESET_ALL}" if success else f"{Fore.RED}✘{Style.RESET_ALL}"
        sys.stdout.write(f"\r{icon} {self.message} Done!\n")
        sys.stdout.flush()

    def __enter__(self):
        """Allows usage with the 'with' statement"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically stops when the block ends"""
        if exc_type:
            # 🪵 Log the error if the spinner was interrupted by a crash
            logger.error(f"🌀 Spinner '{self.message}' interrupted by error: {exc_val}")
            
        self.stop(success=(exc_type is None))
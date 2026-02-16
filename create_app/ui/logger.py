import logging
import sys
from colorama import Fore, Style

def setup_logger():
    """🚀 Configures a silent logger that only speaks on failure."""
    root = logging.getLogger("py-create")
    
    if root.hasHandlers():
        root.handlers.clear()
        
    # 🤐 Set level to ERROR so INFO and DEBUG messages are ignored
    root.setLevel(logging.ERROR)

    handler = logging.StreamHandler(sys.stdout)
    
    # 🔴 Formatting specifically for failure traces
    formatter = logging.Formatter(
        f"\n{Fore.RED}{Style.BRIGHT}[SYSTEM_TRACE] %(asctime)s - %(name)s - %(levelname)s{Style.RESET_ALL}\n"
        f"{Fore.WHITE}%(message)s{Style.RESET_ALL}"
    )
    handler.setFormatter(formatter)
    
    root.addHandler(handler)
    return root

logger = setup_logger()

# --- UI LOGGING HELPERS ---

def log_info(message):
    """This will be SILENT during normal runs."""
    logger.info(message)

def log_error(message, error_details=None):
    """
    🔥 This triggers the output. 
    It prints your clean error message, then the technical trace.
    """
    print(f"\n{Fore.RED}{Style.BRIGHT}❌ ERROR: {message}{Style.RESET_ALL}")
    if error_details:
        # This only prints because we are logging at the ERROR level
        logger.error(f"TECHNICAL DETAILS:\n{error_details}", exc_info=True)

def log_warning(message):
    """Silently logs warnings to the background."""
    logger.warning(message)
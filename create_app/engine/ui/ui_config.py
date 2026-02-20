import sys
import os
from colorama import init

# 🚀 1. Initialize for Cross-Platform Performance
# autoreset=True prevents color bleeding; convert=True fixes Windows CMD
init(autoreset=True)

class UIConfig:
    """
    ULTRA-LIGHTWEIGHT UI PROCESSOR
    Optimized for cross-platform speed and Unicode safety.
    """
    C = {
        "primary": "\033[97m",         # Pure White
        "accent": "\033[38;5;214m",    # Pythonic Amber
        "success": "\033[38;5;82m",     # Electric Lime
        "white": "\033[97m",          # Pure White
        "muted": "\033[38;5;248m",     # Silver Grey
        "dim": "\033[38;5;239m",       # Deep Graphite
        "bold": "\033[1m",
        "bg_highlight": "\033[48;5;238m", # Subtle Steel
        "reset": "\033[0m"
    }
    
    # 🚀 2. Fast Encoding Check (Cross-Platform)
    _UTF = (getattr(sys.stdout, 'encoding', 'utf-8') or 'utf-8').lower() == 'utf-8'

    # Symbols with logic-based fallbacks
    SYMBOL_ACTIVE    = "█" if _UTF else ">"
    SYMBOL_CHECKED   = "⦿" if _UTF else "[x]"
    SYMBOL_UNCHECKED = "○" if _UTF else "[ ]"
    SYMBOL_INIT_ON   = "∬" if _UTF else "(i)"
    SYMBOL_INIT_OFF  = "∷" if _UTF else "( )"
    
    @classmethod
    def paint(cls, text, color_key="primary"):
        """Fastest way to colorize text for the CLI."""
        return f"{cls.C.get(color_key, cls.C['primary'])}{text}{cls.C['reset']}"

    @classmethod
    def write(cls, text, end="\n"):
        """High-performance direct-to-buffer write (Faster than print)."""
        sys.stdout.write(f"{text}{end}")
"""
utils.py - Shared utility helpers
==================================
Logging setup, text helpers, timing, and misc tools.
"""

import logging
import time
import unicodedata
from functools import wraps
from pathlib import Path
from typing import Callable, Any

from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL


# ─── Logging ──────────────────────────────────────────────────────────────────

def get_logger(name: str) -> logging.Logger:
    """Return a consistently-configured logger for *name*."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

        # File handler
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(fh)

        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(LOG_FORMAT))
        ch.setLevel(logging.WARNING)
        logger.addHandler(ch)

    return logger


# ─── Timing decorator ─────────────────────────────────────────────────────────

def timed(func: Callable) -> Callable:
    """Decorator – logs execution time of a function."""
    log = get_logger(func.__module__)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        log.debug("%s finished in %.4fs", func.__qualname__, elapsed)
        return result

    return wrapper


# ─── Text helpers ─────────────────────────────────────────────────────────────

def sanitize_input(text: str) -> str:
    """Strip whitespace and control characters from user input."""
    text = text.strip()
    # Remove non-printable characters (keep Unicode letters/numbers/symbols)
    text = "".join(
        ch for ch in text
        if unicodedata.category(ch)[0] not in ("C",) or ch in ("\n", "\t")
    )
    return text


def has_unicode(text: str) -> bool:
    """Return True if *text* contains non-ASCII characters."""
    return any(ord(ch) > 127 for ch in text)


def count_char_class(text: str, cls: str) -> int:
    """
    Count characters in *text* belonging to a Unicode category prefix.
    cls examples: 'Lu' (uppercase), 'Ll' (lowercase), 'Nd' (decimal digit),
                  'P'  (punctuation), 'S' (symbol).
    """
    return sum(1 for ch in text if unicodedata.category(ch).startswith(cls))


def human_readable_size(n_bytes: int) -> str:
    """Convert byte count to a human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes //= 1024
    return f"{n_bytes:.1f} TB"


def human_readable_time(seconds: float) -> str:
    """
    Convert seconds to a human-readable crack-time string.
    Mirrors zxcvbn display_time logic with extended ranges.
    """
    if seconds < 1:
        return "less than a second"
    if seconds < 60:
        return f"{int(seconds)} second{'s' if seconds != 1 else ''}"
    minutes = seconds / 60
    if minutes < 60:
        return f"{int(minutes)} minute{'s' if minutes != 1 else ''}"
    hours = minutes / 60
    if hours < 24:
        return f"{int(hours)} hour{'s' if hours != 1 else ''}"
    days = hours / 24
    if days < 365:
        return f"{int(days)} day{'s' if days != 1 else ''}"
    years = days / 365
    if years < 1_000:
        return f"{int(years)} year{'s' if years != 1 else ''}"
    if years < 1_000_000:
        return f"{years/1_000:.1f} thousand years"
    if years < 1_000_000_000:
        return f"{years/1_000_000:.1f} million years"
    return "centuries"


def ensure_dir(path: Path) -> Path:
    """Create *path* directory (and parents) if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(name: str) -> str:
    """Strip characters that are unsafe in file names."""
    keep = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.")
    return "".join(ch if ch in keep else "_" for ch in name)

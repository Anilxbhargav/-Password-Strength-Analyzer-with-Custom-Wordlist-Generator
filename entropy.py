"""
entropy.py - Shannon entropy and character-space calculations
==============================================================
Provides bit-entropy estimates independent of zxcvbn, plus
crack-time estimation based on configurable guess rates.
"""

import math
import string
from typing import NamedTuple

from utils import get_logger, human_readable_time

log = get_logger(__name__)

# ─── Guess rates (guesses / second) ───────────────────────────────────────────
# Source: Hashcat benchmarks on consumer GPU (RTX 4090 class)
GUESS_RATES: dict[str, int] = {
    "Online (throttled, 100/hr)":   100 // 3600 or 1,
    "Online (unthrottled, 10/s)":   10,
    "Offline (bcrypt, slow)":       10_000,
    "Offline (MD5, fast GPU)":      100_000_000_000,
}


class EntropyResult(NamedTuple):
    bits: float
    charset_size: int
    crack_times: dict[str, str]      # scenario → human-readable time


def _charset_size(password: str) -> int:
    """Estimate the pool size of the character classes present."""
    pool = 0
    if any(c in string.ascii_lowercase for c in password):
        pool += 26
    if any(c in string.ascii_uppercase for c in password):
        pool += 26
    if any(c in string.digits for c in password):
        pool += 10
    symbols = set(string.punctuation)
    if any(c in symbols for c in password):
        pool += 32
    # Non-ASCII Unicode
    if any(ord(c) > 127 for c in password):
        pool += 128           # conservative estimate
    return max(pool, 1)


def calculate_entropy(password: str) -> EntropyResult:
    """
    Calculate Shannon-style bit entropy:
        H = L × log2(N)
    where L = length, N = estimated character-pool size.

    This is the theoretical maximum entropy; real entropy (accounting
    for patterns) is provided by zxcvbn and used in analyzer.py.
    """
    if not password:
        return EntropyResult(bits=0.0, charset_size=0, crack_times={})

    n = _charset_size(password)
    bits = len(password) * math.log2(n)

    # Crack-time estimations
    combos = 2 ** bits
    crack_times: dict[str, str] = {}
    for scenario, rate in GUESS_RATES.items():
        seconds = combos / max(rate, 1)
        crack_times[scenario] = human_readable_time(seconds)

    log.debug("Entropy: %.2f bits (pool=%d, length=%d)", bits, n, len(password))
    return EntropyResult(bits=round(bits, 2), charset_size=n, crack_times=crack_times)

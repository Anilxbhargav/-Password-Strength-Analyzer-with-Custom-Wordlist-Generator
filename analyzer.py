"""
analyzer.py - Core password analysis engine
=============================================
Combines zxcvbn scoring with additional heuristic checks to produce
a rich AnalysisResult with feedback and actionable suggestions.
"""

import re
import string
import unicodedata
from dataclasses import dataclass, field
from typing import Optional

import zxcvbn as _zxcvbn

from config import (
    KEYBOARD_ROWS, LEET_MAP, MIN_LENGTH, RECOMMENDED_LENGTH,
    SCORE_LABELS, MIN_UPPERCASE, MIN_LOWERCASE, MIN_DIGITS, MIN_SYMBOLS,
    ENTROPY_VERY_WEAK, ENTROPY_WEAK, ENTROPY_FAIR, ENTROPY_STRONG,
)
from entropy import calculate_entropy, EntropyResult
from utils import get_logger, human_readable_time, has_unicode

log = get_logger(__name__)

# ─── Common patterns ──────────────────────────────────────────────────────────
_LEET_REVERSE: dict[str, str] = {v: k for k, v in LEET_MAP.items()}
_YEAR_RE   = re.compile(r"(19|20)\d{2}")
_REPEAT_RE = re.compile(r"(.)\1{2,}")         # 3+ same chars in a row
_SEQ_RE    = re.compile(                       # 3+ sequential chars
    r"(?:012|123|234|345|456|567|678|789|890"
    r"|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",
    re.IGNORECASE,
)
_KEYBOARD_PATTERNS = [
    "qwerty", "qwertz", "azerty", "asdf", "zxcv",
    "1qaz", "2wsx", "3edc", "4rfv", "5tgb",
]


@dataclass
class PasswordStats:
    """Raw character-class statistics for a password."""
    length:     int = 0
    uppercase:  int = 0
    lowercase:  int = 0
    digits:     int = 0
    symbols:    int = 0
    unicode_ch: int = 0
    spaces:     int = 0


@dataclass
class AnalysisResult:
    """Complete analysis result returned by analyze()."""
    password:           str                  = ""
    score:              int                  = 0         # 0-4  (zxcvbn)
    label:              str                  = "Very Weak"
    entropy:            EntropyResult        = field(default_factory=lambda: EntropyResult(0.0, 0, {}))
    stats:              PasswordStats        = field(default_factory=PasswordStats)
    crack_time_display: str                  = ""
    crack_time_seconds: float                = 0.0
    issues:             list[str]            = field(default_factory=list)
    suggestions:        list[str]            = field(default_factory=list)
    patterns_found:     list[str]            = field(default_factory=list)
    zxcvbn_feedback:    dict                 = field(default_factory=dict)
    has_unicode:        bool                 = False
    is_common:          bool                 = False
    has_leet:           bool                 = False
    has_repeated:       bool                 = False
    has_sequential:     bool                 = False
    has_keyboard_pattern: bool               = False
    has_year:           bool                 = False


# ─── Main entry point ─────────────────────────────────────────────────────────

def analyze(password: str, user_info: Optional[list[str]] = None) -> AnalysisResult:
    """
    Analyze *password* and return an AnalysisResult.

    Parameters
    ----------
    password  : The password string to evaluate.
    user_info : Optional list of personal tokens (name, dob, etc.) to
                check for personal information patterns.
    """
    result = AnalysisResult(password=password)

    if not password:
        result.issues.append("❌ Password is empty.")
        return result

    # ── 1. Character statistics ───────────────────────────────────────────────
    stats = _compute_stats(password)
    result.stats = stats

    # ── 2. Entropy ────────────────────────────────────────────────────────────
    result.entropy    = calculate_entropy(password)
    result.has_unicode = has_unicode(password)

    # ── 3. zxcvbn scoring ────────────────────────────────────────────────────
    zx = _zxcvbn.zxcvbn(password, user_inputs=user_info or [])
    result.score              = zx["score"]
    result.label              = SCORE_LABELS[zx["score"]]
    result.crack_time_seconds = float(
        zx["crack_times_seconds"].get("offline_fast_hashing_1e10_per_second", 0)
    )
    result.crack_time_display = human_readable_time(result.crack_time_seconds)
    result.zxcvbn_feedback    = zx.get("feedback", {})
    result.is_common          = zx["score"] == 0 and "password" in password.lower()

    # ── 4. Heuristic pattern checks ──────────────────────────────────────────
    _check_patterns(password, result, user_info or [])

    # ── 5. Build feedback ────────────────────────────────────────────────────
    _build_feedback(result)

    log.info(
        "Analysis: score=%d label=%s entropy=%.1fbits length=%d",
        result.score, result.label, result.entropy.bits, stats.length,
    )
    return result


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _compute_stats(password: str) -> PasswordStats:
    s = PasswordStats(length=len(password))
    for ch in password:
        cat = unicodedata.category(ch)
        if ch == " ":
            s.spaces += 1
        elif ch.isupper():
            s.uppercase += 1
        elif ch.islower():
            s.lowercase += 1
        elif ch.isdigit():
            s.digits += 1
        elif cat.startswith("P") or cat.startswith("S") or ch in string.punctuation:
            s.symbols += 1
        if ord(ch) > 127:
            s.unicode_ch += 1
    return s


def _check_patterns(
    password: str,
    result: AnalysisResult,
    user_info: list[str],
) -> None:
    p_lower = password.lower()

    # Repeated characters
    if _REPEAT_RE.search(password):
        result.has_repeated = True
        result.patterns_found.append("repeated characters")

    # Sequential characters / numbers
    if _SEQ_RE.search(p_lower):
        result.has_sequential = True
        result.patterns_found.append("sequential characters")

    # Keyboard patterns
    for kp in _KEYBOARD_PATTERNS:
        if kp in p_lower:
            result.has_keyboard_pattern = True
            result.patterns_found.append(f"keyboard pattern '{kp}'")
            break
    for row in KEYBOARD_ROWS:
        for size in range(4, len(row) + 1):
            for i in range(len(row) - size + 1):
                chunk = row[i:i + size]
                if chunk in p_lower and chunk not in result.patterns_found:
                    result.has_keyboard_pattern = True
                    if f"keyboard pattern '{chunk}'" not in result.patterns_found:
                        result.patterns_found.append(f"keyboard pattern '{chunk}'")
                    break

    # Year detection
    if _YEAR_RE.search(password):
        result.has_year = True
        result.patterns_found.append("year in password")

    # Leet-speak detection
    for sub in _LEET_REVERSE:
        if sub in password:
            result.has_leet = True
            result.patterns_found.append("leet-speak substitutions")
            break

    # Personal information
    for token in user_info:
        t = token.lower().strip()
        if t and len(t) >= 3 and t in p_lower:
            result.patterns_found.append(f"personal info '{token}'")


def _build_feedback(result: AnalysisResult) -> None:
    """Populate result.issues and result.suggestions."""
    s = result.stats
    issues: list[str]      = []
    suggestions: list[str] = []

    # Length checks
    if s.length < MIN_LENGTH:
        issues.append(f"❌ Too short (only {s.length} characters)")
        suggestions.append(f"✔ Use at least {MIN_LENGTH} characters")
    elif s.length < RECOMMENDED_LENGTH:
        issues.append(f"⚠ Short password ({s.length} characters)")
        suggestions.append(f"✔ Aim for {RECOMMENDED_LENGTH}+ characters for best security")

    # Character class checks
    if s.uppercase < MIN_UPPERCASE:
        issues.append("❌ Missing uppercase letters")
        suggestions.append("✔ Add at least one uppercase letter (A-Z)")

    if s.lowercase < MIN_LOWERCASE:
        issues.append("❌ Missing lowercase letters")
        suggestions.append("✔ Add at least one lowercase letter (a-z)")

    if s.digits < MIN_DIGITS:
        issues.append("❌ Missing numbers")
        suggestions.append("✔ Include at least one digit (0-9)")

    if s.symbols < MIN_SYMBOLS:
        issues.append("❌ Missing symbols")
        suggestions.append("✔ Add symbols like ! @ # $ % & *")

    # Pattern issues
    if result.has_repeated:
        issues.append("❌ Contains repeated characters (e.g. 'aaa')")
        suggestions.append("✔ Avoid repeating the same character 3+ times")

    if result.has_sequential:
        issues.append("❌ Contains sequential characters (e.g. '123', 'abc')")
        suggestions.append("✔ Avoid predictable sequences")

    if result.has_keyboard_pattern:
        issues.append("❌ Contains a keyboard pattern (e.g. 'qwerty')")
        suggestions.append("✔ Avoid rows of adjacent keyboard keys")

    if result.has_year:
        issues.append("⚠ Contains a year – potentially guessable")
        suggestions.append("✔ Avoid embedding years (birth year, current year)")

    if result.has_leet:
        issues.append("⚠ Leet-speak substitutions detected – not much extra security")
        suggestions.append("✔ Leet-speak (3→e, 0→o) is well-known to attackers")

    if any("personal info" in p for p in result.patterns_found):
        issues.append("❌ Contains personal information")
        suggestions.append("✔ Never use names, birthdays, or pet names in passwords")

    # zxcvbn extra feedback
    fb = result.zxcvbn_feedback
    for w in fb.get("warning", []) if isinstance(fb.get("warning"), list) else (
        [fb["warning"]] if fb.get("warning") else []
    ):
        if w and w not in issues:
            issues.append(f"⚠ {w}")

    for s_tip in fb.get("suggestions", []):
        if s_tip and s_tip not in suggestions:
            suggestions.append(f"✔ {s_tip}")

    # Entropy-based suggestion
    if result.entropy.bits < ENTROPY_FAIR:
        suggestions.append("✔ Consider using a passphrase of 4+ random words")

    # Generic strong-password suggestions (always shown)
    if result.score < 3:
        suggestions.append("✔ Use a password manager to generate and store complex passwords")
        suggestions.append("✔ Never reuse passwords across different accounts")

    result.issues      = issues
    result.suggestions = list(dict.fromkeys(suggestions))  # deduplicate, preserve order

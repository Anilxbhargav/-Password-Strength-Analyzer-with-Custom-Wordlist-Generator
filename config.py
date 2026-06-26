"""
config.py - Central configuration for Password Strength Analyzer
================================================================
All tuneable constants, thresholds, and settings live here.
"""

from pathlib import Path

# ─── Project paths ────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR    = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# ─── Application metadata ─────────────────────────────────────────────────────
APP_NAME    = "Password Strength Analyzer"
APP_VERSION = "1.0.0"
APP_AUTHOR  = "CyberSec Educational Project"
APP_LICENSE = "MIT"

# ─── Entropy thresholds (bits) ────────────────────────────────────────────────
ENTROPY_VERY_WEAK  = 28
ENTROPY_WEAK       = 36
ENTROPY_FAIR       = 60
ENTROPY_STRONG     = 128

# ─── Score mapping (zxcvbn 0-4) ───────────────────────────────────────────────
SCORE_LABELS = {
    0: "Very Weak",
    1: "Weak",
    2: "Fair",
    3: "Strong",
    4: "Very Strong",
}

SCORE_COLORS_GUI = {
    0: "#e74c3c",
    1: "#e67e22",
    2: "#f1c40f",
    3: "#2ecc71",
    4: "#27ae60",
}

# ─── Minimum password requirements ────────────────────────────────────────────
MIN_LENGTH          = 8
RECOMMENDED_LENGTH  = 16
MIN_UPPERCASE       = 1
MIN_LOWERCASE       = 1
MIN_DIGITS          = 1
MIN_SYMBOLS         = 1

# ─── Common keyboard patterns ─────────────────────────────────────────────────
KEYBOARD_ROWS = [
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
    "1234567890",
    "qwerty",
    "azerty",
]

# ─── Common suffixes / prefixes used in wordlist generation ───────────────────
COMMON_SUFFIXES = [
    "", "1", "12", "123", "1234", "12345", "123456",
    "!", "@", "#", "$", ".", "_", "-",
    "2020", "2021", "2022", "2023", "2024", "2025", "2026",
    "@123", "#123", "!123", "_123",
    "01", "007", "99", "00",
]

COMMON_PREFIXES = [
    "", "the", "my", "its", "mr", "ms", "dr",
]

# ─── Leet-speak substitution map ──────────────────────────────────────────────
LEET_MAP: dict[str, str] = {
    "a": "4", "e": "3", "i": "1",
    "o": "0", "s": "5", "t": "7",
    "g": "9", "l": "1", "b": "8",
}

# ─── Wordlist generation limits ───────────────────────────────────────────────
MAX_WORDLIST_SIZE   = 500_000   # hard cap to avoid runaway generation
DEDUP_CHUNK_SIZE    = 50_000    # process deduplication in chunks

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_FILE   = LOG_DIR / "psa.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_LEVEL  = "INFO"

# ─── GUI appearance ───────────────────────────────────────────────────────────
GUI_BG         = "#1e1e2e"
GUI_FG         = "#cdd6f4"
GUI_ACCENT     = "#89b4fa"
GUI_ENTRY_BG   = "#313244"
GUI_ENTRY_FG   = "#cdd6f4"
GUI_BUTTON_BG  = "#89b4fa"
GUI_BUTTON_FG  = "#1e1e2e"
GUI_TAB_BG     = "#181825"
GUI_FONT       = ("Consolas", 11)
GUI_FONT_BOLD  = ("Consolas", 11, "bold")
GUI_FONT_LARGE = ("Consolas", 14, "bold")
GUI_WIDTH      = 1100
GUI_HEIGHT     = 780

"""
export.py - Wordlist export utilities
=======================================
Writes generated wordlists to .txt files with metadata headers,
and provides export-result metadata.
"""

import time
from dataclasses import dataclass
from pathlib import Path

from config import OUTPUT_DIR
from utils import get_logger, human_readable_size, safe_filename, ensure_dir

log = get_logger(__name__)


@dataclass
class ExportResult:
    """Metadata returned after a successful export."""
    path:           Path
    word_count:     int
    file_size_bytes: int
    file_size_human: str
    elapsed_seconds: float
    encoding:       str


def export_wordlist(
    words:      list[str],
    filename:   str   = "wordlist",
    output_dir: Path  = OUTPUT_DIR,
    encoding:   str   = "utf-8",
) -> ExportResult:
    """
    Write *words* to a .txt file (one word per line).

    Parameters
    ----------
    words      : The list of candidate passwords to write.
    filename   : Base file name (without extension).
    output_dir : Directory where the file will be written.
    encoding   : Text encoding (default utf-8).

    Returns
    -------
    ExportResult with file metadata.

    Raises
    ------
    PermissionError  : If the directory or file is not writable.
    OSError          : On other filesystem errors.
    ValueError       : If the word list is empty.
    """
    if not words:
        raise ValueError("Word list is empty – nothing to export.")

    ensure_dir(output_dir)
    safe_name = safe_filename(filename) or "wordlist"
    out_path  = output_dir / f"{safe_name}.txt"

    # Avoid overwriting – append a counter if needed
    counter = 1
    while out_path.exists():
        out_path = output_dir / f"{safe_name}_{counter}.txt"
        counter += 1

    log.info("Exporting %d words → %s (encoding=%s)", len(words), out_path, encoding)

    t0 = time.perf_counter()
    try:
        with out_path.open("w", encoding=encoding, errors="replace") as fh:
            # Metadata header
            fh.write("# ─────────────────────────────────────────────────────\n")
            fh.write("# Password Strength Analyzer – Generated Wordlist\n")
            fh.write(f"# Total words : {len(words):,}\n")
            fh.write(f"# Encoding    : {encoding}\n")
            fh.write("# Disclaimer  : For authorised security testing ONLY.\n")
            fh.write("# ─────────────────────────────────────────────────────\n")
            for word in words:
                fh.write(word + "\n")
    except PermissionError as exc:
        log.error("Permission denied writing to %s: %s", out_path, exc)
        raise
    except OSError as exc:
        log.error("OS error while writing %s: %s", out_path, exc)
        raise

    elapsed   = time.perf_counter() - t0
    size      = out_path.stat().st_size
    size_str  = human_readable_size(size)

    log.info("Export complete: %s (%s) in %.2fs", out_path.name, size_str, elapsed)

    return ExportResult(
        path            = out_path,
        word_count      = len(words),
        file_size_bytes = size,
        file_size_human = size_str,
        elapsed_seconds = round(elapsed, 3),
        encoding        = encoding,
    )

"""
validators.py - Input validation helpers
=========================================
All validation logic for passwords and user-profile fields.
"""

import re
from typing import Optional

from utils import get_logger

log = get_logger(__name__)


# ─── Password validators ──────────────────────────────────────────────────────

def validate_password(password: str) -> tuple[bool, str]:
    """
    Light-touch validation – passwords can be almost anything;
    we just refuse completely empty or absurdly long strings.

    Returns (is_valid, error_message).
    """
    if not password:
        return False, "Password must not be empty."
    if len(password) > 1024:
        return False, "Password exceeds maximum allowed length (1024 characters)."
    return True, ""


# ─── Profile field validators ─────────────────────────────────────────────────

def validate_name(value: str, field: str = "Name") -> tuple[bool, str]:
    """Validate a name field – allow letters, hyphens, apostrophes, spaces."""
    if not value:
        return True, ""          # Optional fields are fine when blank
    if len(value) > 64:
        return False, f"{field} is too long (max 64 characters)."
    if re.search(r'[<>{}\[\]\\|^~`]', value):
        return False, f"{field} contains invalid characters."
    return True, ""


def validate_year(value: str) -> tuple[bool, str]:
    """Validate a 4-digit birth year."""
    if not value:
        return True, ""
    if not re.fullmatch(r"\d{4}", value):
        return False, "Year must be exactly 4 digits (e.g. 1995)."
    year = int(value)
    if not (1900 <= year <= 2025):
        return False, "Year must be between 1900 and 2025."
    return True, ""


def validate_date(value: str) -> tuple[bool, str]:
    """
    Validate a birthday in common formats:
    DD/MM/YYYY, MM/DD/YYYY, DDMMYYYY, YYYY-MM-DD.
    """
    if not value:
        return True, ""
    patterns = [
        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
        r"\d{4}-\d{2}-\d{2}",
        r"\d{8}",
    ]
    for p in patterns:
        if re.fullmatch(p, value):
            return True, ""
    return False, "Date format not recognised. Try DD/MM/YYYY or YYYY-MM-DD."


def validate_phone_prefix(value: str) -> tuple[bool, str]:
    """Validate a partial phone number / prefix (digits, optional + prefix)."""
    if not value:
        return True, ""
    if not re.fullmatch(r"\+?\d{3,6}", value):
        return False, "Phone prefix must be 3-6 digits (optionally starting with +)."
    return True, ""


def validate_keyword(value: str) -> tuple[bool, str]:
    """Validate a generic custom keyword."""
    if not value:
        return True, ""
    if len(value) > 128:
        return False, "Keyword is too long (max 128 characters)."
    return True, ""


def validate_profile(profile: dict) -> list[str]:
    """
    Validate a complete user-profile dict used by the wordlist generator.
    Returns a list of error strings (empty list = all OK).
    """
    errors: list[str] = []

    name_fields = [
        "first_name", "last_name", "nickname", "username",
        "pet_name", "partner_name", "company", "school",
        "college", "favourite_team", "favourite_movie",
        "favourite_game", "vehicle", "city", "state", "country",
    ]
    for field in name_fields:
        val = profile.get(field, "")
        ok, msg = validate_name(val, field.replace("_", " ").title())
        if not ok:
            errors.append(msg)

    # Parents names: can be comma-separated
    parents = profile.get("parents_names", "")
    if parents:
        for part in parents.split(","):
            ok, msg = validate_name(part.strip(), "Parent name")
            if not ok:
                errors.append(msg)

    # Year
    ok, msg = validate_year(profile.get("birth_year", ""))
    if not ok:
        errors.append(msg)

    # Birthday
    ok, msg = validate_date(profile.get("birthday", ""))
    if not ok:
        errors.append(msg)

    # Phone prefix
    ok, msg = validate_phone_prefix(profile.get("phone_prefix", ""))
    if not ok:
        errors.append(msg)

    # Custom keywords
    for kw in profile.get("custom_keywords", []):
        ok, msg = validate_keyword(kw)
        if not ok:
            errors.append(msg)

    return errors

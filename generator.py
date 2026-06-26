"""
generator.py - Custom wordlist generation engine
==================================================
Generates realistic password candidates from a user-profile dict,
applying capitalisation variants, leet-speak, suffixes, prefixes,
and common patterns. Deduplicates and caps the output.
"""

import itertools
import re
import secrets
import string
from dataclasses import dataclass, field
from typing import Iterator

from config import (
    COMMON_SUFFIXES, COMMON_PREFIXES, LEET_MAP, MAX_WORDLIST_SIZE,
)
from utils import get_logger, timed

log = get_logger(__name__)

# ─── Profile dataclass ────────────────────────────────────────────────────────

@dataclass
class UserProfile:
    """Holds all personal information supplied by the user."""
    first_name:      str = ""
    last_name:       str = ""
    nickname:        str = ""
    username:        str = ""
    birthday:        str = ""        # e.g. 15/06/1995 or 15061995
    birth_year:      str = ""
    pet_name:        str = ""
    partner_name:    str = ""
    parents_names:   str = ""        # comma-separated
    company:         str = ""
    school:          str = ""
    college:         str = ""
    phone_prefix:    str = ""
    favourite_team:  str = ""
    favourite_movie: str = ""
    favourite_game:  str = ""
    vehicle:         str = ""
    city:            str = ""
    state:           str = ""
    country:         str = ""
    custom_keywords: list[str] = field(default_factory=list)

    # ── Computed tokens ───────────────────────────────────────────────────────
    def base_tokens(self) -> list[str]:
        """Extract all non-empty single-word tokens from the profile."""
        tokens: list[str] = []

        # Simple fields
        for val in (
            self.first_name, self.last_name, self.nickname, self.username,
            self.pet_name, self.partner_name, self.company, self.school,
            self.college, self.favourite_team, self.favourite_movie,
            self.favourite_game, self.vehicle, self.city, self.state, self.country,
        ):
            for part in val.split():
                part = part.strip()
                if part:
                    tokens.append(part)

        # Parents names (comma-separated)
        for name in self.parents_names.split(","):
            for part in name.split():
                part = part.strip()
                if part:
                    tokens.append(part)

        # Date fragments
        if self.birthday:
            digits_only = re.sub(r"\D", "", self.birthday)
            if len(digits_only) >= 4:
                tokens.append(digits_only)
                tokens.append(digits_only[:4])  # DDMM or MMDD
                tokens.append(digits_only[-4:])  # year part

        if self.birth_year:
            tokens.append(self.birth_year)
            tokens.append(self.birth_year[2:])   # last 2 digits

        if self.phone_prefix:
            tokens.append(self.phone_prefix.lstrip("+"))

        # Custom keywords
        for kw in self.custom_keywords:
            kw = kw.strip()
            if kw:
                tokens.append(kw)

        # Deduplicate while preserving insertion order
        seen: set[str] = set()
        result: list[str] = []
        for t in tokens:
            if t.lower() not in seen:
                seen.add(t.lower())
                result.append(t)
        return result


# ─── Capitalisation helpers ───────────────────────────────────────────────────

def _capitalisation_variants(word: str) -> list[str]:
    """Return a set of capitalisation variants for *word*."""
    variants = {
        word.lower(),
        word.upper(),
        word.capitalize(),
        word.title(),
        # camelCase: lower first char, upper rest
        word[0].lower() + word[1:].capitalize() if len(word) > 1 else word.lower(),
        # snake_case (multi-word token is already split, so just lowercase)
        word.lower().replace(" ", "_"),
        # UPPER_SNAKE
        word.upper().replace(" ", "_"),
    }
    return list(variants)


def _leet_variant(word: str) -> str:
    """Apply full leet-speak substitution to *word*."""
    return "".join(LEET_MAP.get(ch.lower(), ch) for ch in word)


def _partial_leet_variant(word: str) -> str:
    """Apply leet-speak only to the first matching character."""
    result = list(word.lower())
    for i, ch in enumerate(result):
        if ch in LEET_MAP:
            result[i] = LEET_MAP[ch]
            break
    return "".join(result)


# ─── Core generation ─────────────────────────────────────────────────────────

def _generate_single_token_words(tokens: list[str]) -> Iterator[str]:
    """All capitalisation + leet variants of individual tokens."""
    for token in tokens:
        for cap in _capitalisation_variants(token):
            yield cap
        leet_full    = _leet_variant(token)
        leet_partial = _partial_leet_variant(token)
        yield leet_full
        yield leet_partial
        yield token.capitalize() + leet_full[-2:] if len(leet_full) > 2 else leet_full


def _apply_affixes(base: str) -> Iterator[str]:
    """Combine *base* with common prefixes and suffixes."""
    for prefix in COMMON_PREFIXES:
        for suffix in COMMON_SUFFIXES:
            if prefix or suffix:
                yield f"{prefix}{base}{suffix}"
            else:
                yield base


def _token_pair_combinations(tokens: list[str]) -> Iterator[str]:
    """
    Combine pairs of tokens (max 2) to form compound passwords.
    Limit to first 8 unique tokens to avoid combinatorial explosion.
    """
    limited = tokens[:8]
    for a, b in itertools.permutations(limited, 2):
        # e.g. RahulSharma, rahul_sharma, rahul123sharma
        yield a.lower() + b.lower()
        yield a.capitalize() + b.capitalize()
        yield a.lower() + "_" + b.lower()
        yield a.lower() + "." + b.lower()
        yield a.lower() + b.lower() + "123"
        yield a.capitalize() + b.capitalize() + "!"


def _popular_base_words() -> list[str]:
    """A small set of common base words to combine with personal tokens."""
    return [
        "password", "welcome", "letmein", "admin", "login",
        "hello", "secure", "dragon", "master", "football",
    ]


@timed
def generate_wordlist(profile: UserProfile, progress_cb=None) -> list[str]:
    """
    Generate a deduplicated wordlist from *profile*.

    Parameters
    ----------
    profile     : UserProfile instance populated from user input.
    progress_cb : Optional callback(current: int, total_estimate: int).

    Returns
    -------
    Sorted, deduplicated list of candidate passwords.
    """
    tokens = profile.base_tokens()
    if not tokens:
        log.warning("No tokens extracted from profile – wordlist will be empty.")
        return []

    log.info("Starting wordlist generation with %d base tokens.", len(tokens))

    seen: set[str] = set()
    result: list[str] = []

    def add(word: str) -> None:
        """Add *word* to the result if it is new and within size limits."""
        if word and word not in seen and len(result) < MAX_WORDLIST_SIZE:
            seen.add(word)
            result.append(word)

    total_estimate = MAX_WORDLIST_SIZE

    # Phase 1 – single-token variants with affixes
    for i, word in enumerate(_generate_single_token_words(tokens)):
        for candidate in _apply_affixes(word):
            add(candidate)
        if progress_cb and i % 50 == 0:
            progress_cb(len(result), total_estimate)
        if len(result) >= MAX_WORDLIST_SIZE:
            break

    # Phase 2 – pair combinations
    if len(result) < MAX_WORDLIST_SIZE:
        for candidate in _token_pair_combinations(tokens):
            add(candidate)
            if len(result) >= MAX_WORDLIST_SIZE:
                break

    # Phase 3 – popular base words + personal tokens
    if len(result) < MAX_WORDLIST_SIZE:
        for base in _popular_base_words():
            for token in tokens[:5]:
                add(base + token.lower())
                add(token.capitalize() + base.capitalize())
                add(base + token.lower() + "!")
            if len(result) >= MAX_WORDLIST_SIZE:
                break

    if progress_cb:
        progress_cb(len(result), len(result))

    log.info("Wordlist generation complete: %d words.", len(result))
    return result

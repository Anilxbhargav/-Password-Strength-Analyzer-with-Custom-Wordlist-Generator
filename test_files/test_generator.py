"""
tests/test_generator.py
========================
Unit tests for the wordlist generation engine.
"""

import pytest
from generator import UserProfile, generate_wordlist


def make_profile(**kwargs) -> UserProfile:
    return UserProfile(**kwargs)


class TestUserProfile:
    def test_base_tokens_empty(self):
        p = make_profile()
        assert p.base_tokens() == []

    def test_base_tokens_single_name(self):
        p = make_profile(first_name="Alice")
        tokens = p.base_tokens()
        assert "Alice" in tokens

    def test_base_tokens_multiple_fields(self):
        p = make_profile(first_name="Alice", pet_name="Rex", birth_year="1995")
        tokens = p.base_tokens()
        assert len(tokens) >= 3

    def test_base_tokens_deduplicated(self):
        p = make_profile(first_name="alice", nickname="alice")
        tokens = p.base_tokens()
        lowered = [t.lower() for t in tokens]
        assert lowered.count("alice") == 1

    def test_birthday_fragments(self):
        p = make_profile(birthday="15/06/1995")
        tokens = p.base_tokens()
        # Should contain some digit fragments
        digit_tokens = [t for t in tokens if t.isdigit()]
        assert len(digit_tokens) >= 1

    def test_custom_keywords(self):
        p = make_profile(custom_keywords=["dragon", "shadow"])
        tokens = p.base_tokens()
        assert "dragon" in tokens
        assert "shadow" in tokens


class TestGenerateWordlist:
    def test_returns_list(self):
        p = make_profile(first_name="Bob")
        wl = generate_wordlist(p)
        assert isinstance(wl, list)

    def test_not_empty(self):
        p = make_profile(first_name="Alice", birth_year="1990")
        wl = generate_wordlist(p)
        assert len(wl) > 0

    def test_contains_variants(self):
        p = make_profile(first_name="alice")
        wl = generate_wordlist(p)
        wl_lower = [w.lower() for w in wl]
        # Should contain alice and at least one variant
        assert any("alice" in w for w in wl_lower)

    def test_no_duplicates(self):
        p = make_profile(first_name="john", last_name="doe")
        wl = generate_wordlist(p)
        assert len(wl) == len(set(wl))

    def test_all_strings(self):
        p = make_profile(first_name="Test", birth_year="2000")
        wl = generate_wordlist(p)
        assert all(isinstance(w, str) for w in wl)

    def test_empty_profile_returns_empty(self):
        p = make_profile()
        wl = generate_wordlist(p)
        assert wl == []

    def test_progress_callback(self):
        p = make_profile(first_name="Callback")
        calls: list[tuple[int, int]] = []

        def cb(current: int, total: int) -> None:
            calls.append((current, total))

        generate_wordlist(p, progress_cb=cb)
        assert len(calls) > 0

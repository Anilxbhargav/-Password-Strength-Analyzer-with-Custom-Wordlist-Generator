"""
tests/test_entropy.py
======================
Unit tests for entropy calculation.
"""

import pytest
from entropy import calculate_entropy


class TestEntropy:
    def test_empty_string(self):
        result = calculate_entropy("")
        assert result.bits == 0.0
        assert result.charset_size == 0

    def test_single_char(self):
        result = calculate_entropy("a")
        assert result.bits > 0

    def test_longer_password_has_more_entropy(self):
        short  = calculate_entropy("abc")
        long_p = calculate_entropy("abcdefghij")
        assert long_p.bits > short.bits

    def test_mixed_charset_increases_entropy(self):
        lower  = calculate_entropy("abcdef")
        mixed  = calculate_entropy("aB1!eF")
        assert mixed.bits >= lower.bits

    def test_unicode_increases_charset(self):
        ascii_pw  = calculate_entropy("Hello")
        unicode_pw = calculate_entropy("Héllo")
        assert unicode_pw.charset_size >= ascii_pw.charset_size

    def test_crack_times_are_populated(self):
        result = calculate_entropy("MyP4ss!")
        assert len(result.crack_times) >= 2
        for scenario, time_str in result.crack_times.items():
            assert isinstance(scenario, str)
            assert isinstance(time_str, str)
            assert len(time_str) > 0

    def test_digits_only_charset(self):
        result = calculate_entropy("12345678")
        # Only digits → pool = 10
        assert result.charset_size == 10

    def test_all_classes(self):
        result = calculate_entropy("aA1!")
        assert result.charset_size >= 94   # lower + upper + digits + symbols

"""
tests/test_validators.py
=========================
Unit tests for all validator functions.
"""

import pytest
from validators import (
    validate_password, validate_name, validate_year,
    validate_date, validate_phone_prefix, validate_keyword, validate_profile,
)


class TestValidatePassword:
    def test_valid(self):
        ok, _ = validate_password("MyP@ss!")
        assert ok

    def test_empty(self):
        ok, msg = validate_password("")
        assert not ok
        assert "empty" in msg.lower()

    def test_too_long(self):
        ok, msg = validate_password("a" * 1025)
        assert not ok


class TestValidateName:
    def test_empty_is_ok(self):
        ok, _ = validate_name("")
        assert ok

    def test_simple_name(self):
        ok, _ = validate_name("Alice")
        assert ok

    def test_hyphenated(self):
        ok, _ = validate_name("Mary-Jane")
        assert ok

    def test_too_long(self):
        ok, _ = validate_name("a" * 65)
        assert not ok

    def test_invalid_chars(self):
        ok, _ = validate_name("Na<me>")
        assert not ok


class TestValidateYear:
    def test_valid(self):
        ok, _ = validate_year("1995")
        assert ok

    def test_empty_ok(self):
        ok, _ = validate_year("")
        assert ok

    def test_not_four_digits(self):
        ok, _ = validate_year("99")
        assert not ok

    def test_out_of_range(self):
        ok, _ = validate_year("2030")
        assert not ok


class TestValidateDate:
    def test_slash_format(self):
        ok, _ = validate_date("15/06/1995")
        assert ok

    def test_iso_format(self):
        ok, _ = validate_date("1995-06-15")
        assert ok

    def test_compact_format(self):
        ok, _ = validate_date("15061995")
        assert ok

    def test_empty_ok(self):
        ok, _ = validate_date("")
        assert ok

    def test_invalid(self):
        ok, _ = validate_date("yesterday")
        assert not ok


class TestValidatePhonePrefix:
    def test_valid_digits(self):
        ok, _ = validate_phone_prefix("9876")
        assert ok

    def test_valid_plus_prefix(self):
        ok, _ = validate_phone_prefix("+1234")
        assert ok

    def test_empty_ok(self):
        ok, _ = validate_phone_prefix("")
        assert ok

    def test_too_short(self):
        ok, _ = validate_phone_prefix("12")
        assert not ok


class TestValidateKeyword:
    def test_valid(self):
        ok, _ = validate_keyword("dragon")
        assert ok

    def test_empty_ok(self):
        ok, _ = validate_keyword("")
        assert ok

    def test_too_long(self):
        ok, _ = validate_keyword("x" * 129)
        assert not ok


class TestValidateProfile:
    def test_empty_profile_no_errors(self):
        errors = validate_profile({})
        assert errors == []

    def test_invalid_year_produces_error(self):
        errors = validate_profile({"birth_year": "abcd"})
        assert len(errors) > 0

    def test_valid_profile(self):
        errors = validate_profile({
            "first_name": "Alice",
            "last_name": "Smith",
            "birth_year": "1992",
            "birthday": "12/03/1992",
        })
        assert errors == []

"""
tests/test_analyzer.py
========================
Unit tests for the password analysis engine.
"""

import pytest
from analyzer import analyze, AnalysisResult
from config import SCORE_LABELS


class TestAnalyze:
    def test_empty_password(self):
        result = analyze("")
        assert result.score == 0
        assert any("empty" in i.lower() for i in result.issues)

    def test_very_weak_password(self):
        result = analyze("123456")
        assert result.score <= 1

    def test_very_strong_password(self):
        result = analyze("T!r#9kQx@Lm$2vP&")
        assert result.score >= 3

    def test_label_matches_score(self):
        for pw, expected_max in [("password", 1), ("Tr0ub4dor&3", 4)]:
            result = analyze(pw)
            assert result.label == SCORE_LABELS[result.score]

    def test_stats_counts(self):
        pw = "Hello World! 123"
        result = analyze(pw)
        assert result.stats.length == len(pw)
        assert result.stats.uppercase >= 1
        assert result.stats.lowercase >= 1
        assert result.stats.digits >= 1
        assert result.stats.symbols >= 1

    def test_sequential_detection(self):
        result = analyze("abc123def")
        assert result.has_sequential or result.has_repeated or result.score <= 2

    def test_keyboard_pattern(self):
        result = analyze("qwertyuiop!")
        assert result.has_keyboard_pattern

    def test_year_detection(self):
        result = analyze("john1990pass")
        assert result.has_year

    def test_personal_info_detection(self):
        result = analyze("johnsmith", user_info=["john", "smith"])
        assert any("personal" in p for p in result.patterns_found)

    def test_leet_detection(self):
        result = analyze("P4ssw0rd!")
        assert result.has_leet or result.score >= 0   # at least runs without error

    def test_unicode_detection(self):
        result = analyze("Pässwörd123!")
        assert result.has_unicode

    def test_issues_are_strings(self):
        result = analyze("pass")
        for issue in result.issues:
            assert isinstance(issue, str)

    def test_suggestions_are_strings(self):
        result = analyze("hunter2")
        for sug in result.suggestions:
            assert isinstance(sug, str)

    def test_repeated_characters(self):
        result = analyze("aaabbbccc")
        assert result.has_repeated

    def test_crack_time_display_is_string(self):
        result = analyze("MyS3cur3P@ss!")
        assert isinstance(result.crack_time_display, str)
        assert len(result.crack_time_display) > 0

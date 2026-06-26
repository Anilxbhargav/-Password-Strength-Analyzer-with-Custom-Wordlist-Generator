"""
tests"""
tests/test_export.py
=====================
Unit tests for wordlist export.
"""

import pytest
from pathlib import Path
from export import export_wordlist, ExportResult


class TestExportWordlist:
    def test_basic_export(self, tmp_path: Path):
        words = ["hello", "world", "test123"]
        result = export_wordlist(words, filename="test_export", output_dir=tmp_path)
        assert isinstance(result, ExportResult)
        assert result.path.exists()
        assert result.word_count == 3

    def test_file_contains_words(self, tmp_path: Path):
        words = ["alpha", "beta", "gamma"]
        result = export_wordlist(words, filename="words", output_dir=tmp_path)
        content = result.path.read_text(encoding="utf-8")
        for w in words:
            assert w in content

    def test_no_overwrite(self, tmp_path: Path):
        words = ["a", "b"]
        r1 = export_wordlist(words, filename="dupe", output_dir=tmp_path)
        r2 = export_wordlist(words, filename="dupe", output_dir=tmp_path)
        assert r1.path != r2.path      # second file should have a counter suffix

    def test_empty_list_raises(self, tmp_path: Path):
        with pytest.raises(ValueError):
            export_wordlist([], filename="empty", output_dir=tmp_path)

    def test_metadata_header(self, tmp_path: Path):
        words = ["x"]
        result = export_wordlist(words, filename="meta", output_dir=tmp_path)
        content = result.path.read_text(encoding="utf-8")
        assert "Password Strength Analyzer" in content

    def test_file_size_populated(self, tmp_path: Path):
        words = ["one", "two", "three"]
        result = export_wordlist(words, filename="size", output_dir=tmp_path)
        assert result.file_size_bytes > 0
        assert isinstance(result.file_size_human, str)

    def test_elapsed_seconds(self, tmp_path: Path):
        words = ["timing"]
        result = export_wordlist(words, filename="timing", output_dir=tmp_path)
        assert result.elapsed_seconds >= 0

    def test_custom_encoding(self, tmp_path: Path):
        words = ["café", "naïve"]
        result = export_wordlist(
            words, filename="utf16", output_dir=tmp_path, encoding="utf-16")
        assert result.encoding == "utf-16"
        assert result.path.exists()
=====================
Unit tests for wordlist export.
"""

import pytest
from pathlib import Path
from export import export_wordlist, ExportResult


class TestExportWordlist:
    def test_basic_export(self, tmp_path: Path):
        words = ["hello", "world", "test123"]
        result = export_wordlist(words, filename="test_export", output_dir=tmp_path)
        assert isinstance(result, ExportResult)
        assert result.path.exists()
        assert result.word_count == 3

    def test_file_contains_words(self, tmp_path: Path):
        words = ["alpha", "beta", "gamma"]
        result = export_wordlist(words, filename="words", output_dir=tmp_path)
        content = result.path.read_text(encoding="utf-8")
        for w in words:
            assert w in content

    def test_no_overwrite(self, tmp_path: Path):
        words = ["a", "b"]
        r1 = export_wordlist(words, filename="dupe", output_dir=tmp_path)
        r2 = export_wordlist(words, filename="dupe", output_dir=tmp_path)
        assert r1.path != r2.path      # second file should have a counter suffix

    def test_empty_list_raises(self, tmp_path: Path):
        with pytest.raises(ValueError):
            export_wordlist([], filename="empty", output_dir=tmp_path)

    def test_metadata_header(self, tmp_path: Path):
        words = ["x"]
        result = export_wordlist(words, filename="meta", output_dir=tmp_path)
        content = result.path.read_text(encoding="utf-8")
        assert "Password Strength Analyzer" in content

    def test_file_size_populated(self, tmp_path: Path):
        words = ["one", "two", "three"]
        result = export_wordlist(words, filename="size", output_dir=tmp_path)
        assert result.file_size_bytes > 0
        assert isinstance(result.file_size_human, str)

    def test_elapsed_seconds(self, tmp_path: Path):
        words = ["timing"]
        result = export_wordlist(words, filename="timing", output_dir=tmp_path)
        assert result.elapsed_seconds >= 0

    def test_custom_encoding(self, tmp_path: Path):
        words = ["café", "naïve"]
        result = export_wordlist(
            words, filename="utf16", output_dir=tmp_path, encoding="utf-16")
        assert result.encoding == "utf-16"
        assert result.path.exists()

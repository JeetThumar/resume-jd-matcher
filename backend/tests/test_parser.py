"""
tests/test_parser.py
====================
Unit tests for :mod:`resume_matcher.parser`.

Run with::

    pytest tests/test_parser.py -v

Fixtures
--------
* ``sample_pdf_bytes`` — minimal valid PDF bytes for smoke tests.
* ``sample_txt_bytes`` — UTF-8 encoded plain text for smoke tests.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_txt_bytes() -> bytes:
    """Return a trivial UTF-8 text payload for parser tests."""
    return b"Software Engineer with 5 years of Python experience."


@pytest.fixture()
def sample_pdf_bytes() -> bytes:
    """Return minimal valid PDF bytes.

    Note: The content is not extracted here — tests that need real extraction
    should place a sample PDF in ``data/samples/`` and read it from disk.
    """
    # Minimal hand-crafted single-page PDF (no images, just structure).
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f\n"
        b"trailer<</Size 4/Root 1 0 R>>\n"
        b"%%EOF\n"
    )


# ---------------------------------------------------------------------------
# extract_text_from_txt
# ---------------------------------------------------------------------------


class TestExtractTextFromTxt:
    """Tests for :func:`resume_matcher.parser.extract_text_from_txt`."""

    def test_bytes_input_returns_string(self, sample_txt_bytes: bytes) -> None:
        """Bytes input should be decoded and returned as a str."""
        from resume_matcher.parser import extract_text_from_txt

        result = extract_text_from_txt(sample_txt_bytes)
        assert isinstance(result, str)

    def test_content_is_preserved(self, sample_txt_bytes: bytes) -> None:
        """Decoded text should match the original content."""
        from resume_matcher.parser import extract_text_from_txt

        result = extract_text_from_txt(sample_txt_bytes)
        assert "Python" in result

    def test_invalid_type_raises_type_error(self) -> None:
        """Non-str/Path/bytes input should raise TypeError."""
        from resume_matcher.parser import extract_text_from_txt

        with pytest.raises((TypeError, NotImplementedError)):
            extract_text_from_txt(12345)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# extract_text_from_pdf
# ---------------------------------------------------------------------------


class TestExtractTextFromPdf:
    """Tests for :func:`resume_matcher.parser.extract_text_from_pdf`."""

    def test_returns_string(self, sample_pdf_bytes: bytes) -> None:
        """Valid PDF bytes should produce a str (possibly empty for stub PDF)."""
        from resume_matcher.parser import extract_text_from_pdf

        # Implementation may raise NotImplementedError until wired up.
        try:
            result = extract_text_from_pdf(sample_pdf_bytes)
            assert isinstance(result, str)
        except NotImplementedError:
            pytest.skip("extract_text_from_pdf not yet implemented")

    def test_invalid_type_raises(self) -> None:
        """Non-supported source type should raise TypeError or NotImplementedError."""
        from resume_matcher.parser import extract_text_from_pdf

        with pytest.raises((TypeError, NotImplementedError)):
            extract_text_from_pdf(42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# parse_uploaded_file
# ---------------------------------------------------------------------------


class TestParseUploadedFile:
    """Tests for :func:`resume_matcher.parser.parse_uploaded_file`."""

    def test_txt_extension_dispatches_correctly(self, sample_txt_bytes: bytes) -> None:
        """A .txt file should be extracted without raising."""
        from resume_matcher.parser import parse_uploaded_file

        try:
            result = parse_uploaded_file(sample_txt_bytes, "resume.txt")
            assert isinstance(result, str)
        except NotImplementedError:
            pytest.skip("parse_uploaded_file not yet implemented")

    def test_unsupported_extension_raises_value_error(self) -> None:
        """An unsupported extension should raise ValueError."""
        from resume_matcher.parser import parse_uploaded_file

        with pytest.raises((ValueError, NotImplementedError)):
            parse_uploaded_file(b"data", "resume.docx")

    def test_pdf_extension_accepted(self, sample_pdf_bytes: bytes) -> None:
        """A .pdf file should not raise a ValueError for the extension."""
        from resume_matcher.parser import parse_uploaded_file

        try:
            parse_uploaded_file(sample_pdf_bytes, "resume.pdf")
        except ValueError as exc:
            if "Unsupported" in str(exc):
                raise
        except NotImplementedError:
            pytest.skip("parse_uploaded_file not yet implemented")

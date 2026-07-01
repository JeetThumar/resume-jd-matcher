"""
parser.py
=========
Text extraction from resume and job-description documents.

Supported input formats
-----------------------
* PDF  — extracted with ``pdfplumber`` (text-based PDFs only).
* TXT  — plain UTF-8 text files or raw bytes.
* str  — passthrough for already-decoded strings.

All public functions return plain ``str`` so the rest of the application
never needs to know which format was originally supplied.
"""

from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Union

import pdfplumber


# ---------------------------------------------------------------------------
# Type alias for the various ways a caller can supply document bytes
# ---------------------------------------------------------------------------
FileSource = Union[str, Path, bytes, io.BytesIO]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _clean_whitespace(text: str) -> str:
    """Normalise whitespace in extracted text.

    - Collapses runs of spaces / tabs on a single line to one space.
    - Preserves paragraph breaks (up to 2 newlines) while collapsing
      triple-or-more newlines down to exactly two.
    - Strips trailing spaces from every line and leading/trailing
      whitespace from the whole document.

    Args:
        text: Raw text as returned by pdfplumber or a file read.

    Returns:
        Cleaned plain-text string.
    """
    # Collapse horizontal whitespace (tabs → space, multi-space → space)
    text = re.sub(r"[ \t]+", " ", text)
    # Strip trailing spaces from each line
    text = "\n".join(line.rstrip() for line in text.splitlines())
    # Collapse 3+ consecutive newlines to 2 (preserve paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_text_from_pdf(source: FileSource) -> str:
    """Extract all readable text from a PDF document.

    Reads each page with ``pdfplumber`` and concatenates the results.
    Pages are separated by a double newline so paragraph structure is
    preserved across page boundaries.

    Args:
        source: The PDF to parse.  Accepted forms:

                - ``str`` or ``pathlib.Path`` — path to a file on disk.
                - ``bytes``                   — raw binary content.
                - ``io.BytesIO``              — already-opened binary stream.

    Returns:
        Concatenated plain-text from all pages, pages separated by
        double newlines.  Excess whitespace is stripped.

    Raises:
        TypeError:         If *source* is not one of the supported types.
        ValueError:        If no text could be extracted (e.g. image-only PDF).
        FileNotFoundError: If a path is given but the file does not exist.
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")
        pdf_stream: io.IOBase = open(path, "rb")  # type: ignore[assignment]
        close_after = True
    elif isinstance(source, bytes):
        pdf_stream = io.BytesIO(source)
        close_after = False
    elif isinstance(source, io.BytesIO):
        pdf_stream = source
        close_after = False
    else:
        raise TypeError(
            f"extract_text_from_pdf: unsupported source type {type(source).__name__!r}. "
            "Expected str, Path, bytes, or io.BytesIO."
        )

    try:
        with pdfplumber.open(pdf_stream) as pdf:
            page_texts: list[str] = []
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                page_texts.append(page_text)

        combined = "\n\n".join(page_texts)
        cleaned = _clean_whitespace(combined)

        if not cleaned:
            raise ValueError(
                "No text could be extracted from the PDF. "
                "The file may be image-based or password-protected."
            )

        return cleaned
    finally:
        if close_after:
            pdf_stream.close()  # type: ignore[union-attr]


def extract_text_from_txt(source: Union[str, Path, bytes]) -> str:
    """Extract text from a plain-text file or raw bytes.

    Args:
        source: The text to parse.  Accepted forms:

                - ``str`` or ``pathlib.Path`` — path to a UTF-8 file on disk.
                - ``bytes``                   — UTF-8 encoded binary content.

    Returns:
        Decoded and whitespace-normalised string content.

    Raises:
        TypeError:         If *source* is not one of the supported types.
        FileNotFoundError: If a path is given but the file does not exist.
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Text file not found: {path}")
        raw = path.read_text(encoding="utf-8", errors="replace")
    elif isinstance(source, bytes):
        raw = source.decode("utf-8", errors="replace")
    else:
        raise TypeError(
            f"extract_text_from_txt: unsupported source type {type(source).__name__!r}. "
            "Expected str, Path, or bytes."
        )

    return _clean_whitespace(raw)


def extract_text_from_input(text_or_path: Union[str, Path]) -> str:
    """Accept either a raw text string or a path to a PDF / TXT file.

    This is the convenience entry-point for callers that don't know ahead of
    time whether the user supplied a file path or pasted plain text (e.g. a
    job description typed into a text area).

    Detection logic
    ~~~~~~~~~~~~~~~
    1. If *text_or_path* is an existing path ending in ``.pdf``  →
       :func:`extract_text_from_pdf`.
    2. If *text_or_path* is an existing path ending in ``.txt``  →
       :func:`extract_text_from_txt`.
    3. Otherwise treat the value as a raw plain-text string and return it
       after whitespace normalisation.

    Strings that look like paths but do not exist on disk (or have an
    unrecognised extension) are treated as literal text, so a pasted job
    description that happens to contain slashes won't trigger an error.
    A bare ``pathlib.Path`` object that doesn't match any supported extension
    will raise ``ValueError`` instead, since the caller clearly intended a
    file.

    Args:
        text_or_path: A pasted text string **or** a ``str`` / ``Path``
                      pointing to a ``.pdf`` or ``.txt`` file on disk.

    Returns:
        Extracted or normalised plain-text string.

    Raises:
        ValueError:        If a ``Path`` object is given whose extension is
                           not supported or whose file does not exist.
        FileNotFoundError: Propagated from the underlying extractor when an
                           explicitly existing path cannot be opened.
    """
    candidate = Path(text_or_path)

    if candidate.suffix.lower() == ".pdf" and candidate.exists():
        return extract_text_from_pdf(candidate)

    if candidate.suffix.lower() == ".txt" and candidate.exists():
        return extract_text_from_txt(candidate)

    # A bare Path object that didn't match → surface a helpful error.
    if isinstance(text_or_path, Path):
        raise ValueError(
            f"Unsupported file type or file not found: {text_or_path}. "
            "Supported extensions are .pdf and .txt."
        )

    # Fall through: treat as raw text (pasted string input).
    return _clean_whitespace(str(text_or_path))


def parse_uploaded_file(file_bytes: bytes, filename: str) -> str:
    """Dispatch to the correct extractor based on the file extension.

    This is the single entry-point used by the Streamlit UI.

    Args:
        file_bytes: Raw binary content of the uploaded file.
        filename:   Original filename, e.g. ``"resume.pdf"`` or
                    ``"job_description.txt"``.  Used **only** to detect
                    the file type — the bytes are the actual data.

    Returns:
        Extracted plain-text string ready for downstream processing.

    Raises:
        ValueError: If the file extension is not ``.pdf`` or ``.txt``.
    """
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)

    if ext == ".txt":
        return extract_text_from_txt(file_bytes)

    raise ValueError(
        f"Unsupported file type: {ext!r}. "
        "Please upload a .pdf or .txt file."
    )

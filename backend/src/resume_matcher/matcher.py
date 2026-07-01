"""
matcher.py
==========
LLM-powered resume ↔ job-description comparison via the Google Gemini API.

Design
------
* A single public function :func:`match_resume_to_jd` sends both documents
  to a Gemini model and parses a structured JSON response.
* :func:`compare_resume_to_jd` is a convenience alias with the exact
  signature requested by the application layer.
* The result type :class:`MatchResult` is a ``TypedDict`` so callers get
  IDE auto-complete without a heavy dependency on a dataclass library.
* All configuration (model name, token limits, API key) is sourced from
  :mod:`resume_matcher.config` — never hard-coded here.

Example
-------
>>> from resume_matcher.matcher import compare_resume_to_jd
>>> result = compare_resume_to_jd(resume_text="...", jd_text="...")
>>> print(result["match_score"])  # e.g. 72
"""

from __future__ import annotations

import json
import re
from typing import Any, TypedDict

from google import genai
from google.genai import types

from resume_matcher.config import settings, _load_settings


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

_MODEL = "gemini-2.5-flash"


class MatchResult(TypedDict):
    """Structured output returned by :func:`match_resume_to_jd`.

    Attributes:
        match_score:              Overall fit percentage, 0–100.
        matched_skills:           Keywords / skills present in *both* the
                                  resume and the job description.
        missing_skills:           Keywords in the JD absent from the resume.
        suggested_resume_tweaks:  Specific, actionable suggestions to improve
                                  the resume for this role.
    """

    match_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    suggested_resume_tweaks: list[str]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are an expert technical recruiter and resume coach. "
    "Your task is to compare a candidate's resume against a job description "
    "and return a structured evaluation. "
    "You MUST respond with ONLY a single valid JSON object — "
    "no markdown, no code fences, no preamble, no trailing text. "
    "The JSON must have exactly these four keys:\n"
    '  "match_score"             : integer 0-100\n'
    '  "matched_skills"          : array of strings\n'
    '  "missing_skills"          : array of strings\n'
    '  "suggested_resume_tweaks" : array of specific, actionable suggestion strings\n'
    "Do not include any other keys or commentary."
)


def _build_prompt(resume_text: str, jd_text: str) -> str:
    """Construct the user-turn prompt for the LLM.

    Args:
        resume_text: Plain-text resume.
        jd_text:     Plain-text job description.

    Returns:
        Formatted prompt string ready to be sent as the ``user`` message.
    """
    return (
        "## RESUME\n"
        f"{resume_text.strip()}\n\n"
        "## JOB DESCRIPTION\n"
        f"{jd_text.strip()}\n\n"
        "Evaluate the resume against the job description and return the JSON object."
    )


def _strip_markdown_fences(text: str) -> str:
    """Remove accidental markdown code fences the model might emit.

    Handles both ``` and ```json variants.
    """
    # Match an optional ```[lang] … ``` wrapper
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text.strip()


def _parse_llm_response(raw_text: str) -> MatchResult:
    """Parse and validate a raw LLM response string into a :class:`MatchResult`.

    Strips any accidental markdown code fences, then JSON-decodes and
    coerces each field to its expected type.

    Args:
        raw_text: The raw text from the Gemini response.

    Returns:
        A validated :class:`MatchResult`.

    Raises:
        ValueError: If *raw_text* is not valid JSON or is missing required keys.
    """
    cleaned = _strip_markdown_fences(raw_text)

    try:
        data: dict[str, Any] = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned non-JSON content.\n"
            f"JSON error: {exc}\n"
            f"Raw response (first 500 chars):\n{raw_text[:500]}"
        ) from exc

    required_keys = {"match_score", "matched_skills", "missing_skills", "suggested_resume_tweaks"}
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(
            f"LLM response JSON is missing required keys: {missing}.\n"
            f"Received keys: {set(data.keys())}"
        )

    # Coerce types to guard against model returning strings instead of ints
    try:
        return MatchResult(
            match_score=int(data["match_score"]),
            matched_skills=[str(s) for s in data["matched_skills"]],
            missing_skills=[str(s) for s in data["missing_skills"]],
            suggested_resume_tweaks=[str(s) for s in data["suggested_resume_tweaks"]],
        )
    except (TypeError, KeyError) as exc:
        raise ValueError(f"LLM response has unexpected field types: {exc}") from exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def match_resume_to_jd(
    resume_text: str,
    jd_text: str,
    *,
    model: str | None = None,
    max_tokens: int | None = None,
    api_key: str | None = None,
) -> MatchResult:
    """Compare a resume to a job description using a Gemini LLM.

    Sends both documents to the Gemini API and parses the structured
    JSON response into a :class:`MatchResult`.

    Args:
        resume_text: Plain-text content of the candidate's resume.
        jd_text:     Plain-text content of the job description.
        model:       Gemini model identifier to use.  Defaults to
                     ``gemini-2.5-flash``.
        max_tokens:  Maximum response tokens.  Defaults to
                     ``settings.max_tokens``.
        api_key:     Gemini API key.  Defaults to
                     ``settings.gemini_api_key``.

    Returns:
        A :class:`MatchResult` dict with ``match_score``, ``matched_skills``,
        ``missing_skills``, and ``suggested_resume_tweaks``.

    Raises:
        EnvironmentError:   If no API key is available.
        ValueError:         If the LLM response cannot be decoded as JSON or
                            is missing required fields.
        genai.errors.APIError: On Gemini API-level errors.
    """
    # Resolve configuration, preferring explicit arguments over settings.
    resolved_api_key = api_key
    resolved_model = model or _MODEL
    resolved_max_tokens = max_tokens

    # Only attempt to load environment settings if we are missing the key or max_tokens
    if not resolved_api_key or not resolved_max_tokens:
        try:
            _settings = settings if settings is not None else _load_settings()
            resolved_api_key = resolved_api_key or _settings.gemini_api_key
            resolved_max_tokens = resolved_max_tokens or _settings.max_tokens
        except EnvironmentError:
            # If _load_settings fails (e.g. empty .env file) but we have an explicit key from the UI,
            # we can safely proceed using a default max_tokens.
            if resolved_api_key:
                resolved_max_tokens = resolved_max_tokens or 4096
            else:
                raise

    if not resolved_api_key:
        raise EnvironmentError("No Gemini API key provided via arguments or environment.")

    client = genai.Client(api_key=resolved_api_key)
    prompt = _build_prompt(resume_text, jd_text)

    try:
        response = client.models.generate_content(
            model=resolved_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                max_output_tokens=resolved_max_tokens,
                temperature=0.0,
                # Optionally use response_mime_type="application/json"
                response_mime_type="application/json",
            )
        )
    except genai.errors.APIError as exc:
        err_msg = str(exc).lower()
        if exc.code in (401, 403) or (exc.code == 400 and "api key not valid" in err_msg):
            raise EnvironmentError(
                "Gemini authentication failed. "
                "Check that GEMINI_API_KEY is set correctly."
            ) from exc
        raise RuntimeError(
            f"Gemini API error ({exc.code}): {exc.message}"
        ) from exc

    raw_text: str = response.text
    return _parse_llm_response(raw_text)


# ---------------------------------------------------------------------------
# Convenience alias (matches the function name requested by the application)
# ---------------------------------------------------------------------------


def compare_resume_to_jd(resume_text: str, jd_text: str) -> MatchResult:
    """Thin wrapper around :func:`match_resume_to_jd` with a simpler signature.

    Accepts only the two required text arguments; all other parameters use
    their defaults (model = ``gemini-2.5-flash``, credentials from env).

    Args:
        resume_text: Plain-text content of the candidate's resume.
        jd_text:     Plain-text content of the job description.

    Returns:
        A :class:`MatchResult` dict with ``match_score``, ``matched_skills``,
        ``missing_skills``, and ``suggested_resume_tweaks``.
    """
    return match_resume_to_jd(resume_text=resume_text, jd_text=jd_text)

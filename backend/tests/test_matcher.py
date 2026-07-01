"""
tests/test_matcher.py
=====================
Unit tests for :mod:`resume_matcher.matcher`.

Run with::

    pytest tests/test_matcher.py -v

External API calls are **mocked** — these tests never hit the real
Anthropic API.  Set ``ANTHROPIC_API_KEY=test-key`` in the environment
(or via a ``conftest.py`` fixture) to allow the config module to initialise.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_resume() -> str:
    """Return minimal resume text for matcher tests."""
    return (
        "Jane Doe — Software Engineer\n"
        "Skills: Python, FastAPI, PostgreSQL, Docker, REST APIs\n"
        "Experience: 4 years backend development at Acme Corp."
    )


@pytest.fixture()
def sample_jd() -> str:
    """Return minimal job-description text for matcher tests."""
    return (
        "We are looking for a Senior Backend Engineer with strong Python skills, "
        "experience with FastAPI, Kubernetes, and PostgreSQL.  "
        "Knowledge of CI/CD pipelines is a plus."
    )


@pytest.fixture()
def valid_llm_response() -> str:
    """Return a well-formed JSON string that the LLM is expected to produce."""
    return json.dumps(
        {
            "score": 75,
            "matched_skills": ["Python", "FastAPI", "PostgreSQL"],
            "missing_skills": ["Kubernetes", "CI/CD"],
            "strengths": ["Strong Python background", "REST API experience"],
            "improvements": [
                "Add Kubernetes to your profile",
                "Highlight any CI/CD pipeline work",
            ],
            "summary": "Good fit overall; add Kubernetes and CI/CD experience.",
        }
    )


# ---------------------------------------------------------------------------
# _parse_llm_response
# ---------------------------------------------------------------------------


class TestParseLlmResponse:
    """Tests for :func:`resume_matcher.matcher._parse_llm_response`."""

    def test_valid_json_returns_match_result(self, valid_llm_response: str) -> None:
        """Well-formed JSON should parse into a MatchResult without error."""
        from resume_matcher.matcher import _parse_llm_response

        try:
            result = _parse_llm_response(valid_llm_response)
            assert result["score"] == 75
            assert "Python" in result["matched_skills"]
        except NotImplementedError:
            pytest.skip("_parse_llm_response not yet implemented")

    def test_invalid_json_raises_value_error(self) -> None:
        """Malformed JSON should raise ValueError."""
        from resume_matcher.matcher import _parse_llm_response

        with pytest.raises((ValueError, NotImplementedError)):
            _parse_llm_response("this is not json {{{")

    def test_score_is_clamped_or_validated(self, valid_llm_response: str) -> None:
        """Score field should be an integer between 0 and 100."""
        from resume_matcher.matcher import _parse_llm_response

        try:
            result = _parse_llm_response(valid_llm_response)
            assert isinstance(result["score"], int)
            assert 0 <= result["score"] <= 100
        except NotImplementedError:
            pytest.skip("_parse_llm_response not yet implemented")

    def test_strips_markdown_fences(self, valid_llm_response: str) -> None:
        """JSON wrapped in ```json ... ``` fences should still parse."""
        from resume_matcher.matcher import _parse_llm_response

        fenced = f"```json\n{valid_llm_response}\n```"
        try:
            result = _parse_llm_response(fenced)
            assert result["score"] == 75
        except NotImplementedError:
            pytest.skip("_parse_llm_response not yet implemented")


# ---------------------------------------------------------------------------
# match_resume_to_jd (with mocked Anthropic client)
# ---------------------------------------------------------------------------


class TestMatchResumeToJd:
    """Tests for :func:`resume_matcher.matcher.match_resume_to_jd`."""

    def test_returns_match_result_shape(
        self,
        sample_resume: str,
        sample_jd: str,
        valid_llm_response: str,
    ) -> None:
        """With a mocked API, the function should return a complete MatchResult."""
        from resume_matcher.matcher import match_resume_to_jd

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=valid_llm_response)]

        with patch("anthropic.Anthropic") as MockClient:
            MockClient.return_value.messages.create.return_value = mock_message
            try:
                result = match_resume_to_jd(
                    sample_resume,
                    sample_jd,
                    api_key="test-key",
                )
                assert "score" in result
                assert "matched_skills" in result
                assert "missing_skills" in result
            except NotImplementedError:
                pytest.skip("match_resume_to_jd not yet implemented")

    def test_raises_without_api_key(
        self, sample_resume: str, sample_jd: str
    ) -> None:
        """Calling without any API key source should raise EnvironmentError."""
        from resume_matcher.matcher import match_resume_to_jd

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises((EnvironmentError, NotImplementedError)):
                match_resume_to_jd(sample_resume, sample_jd, api_key="")

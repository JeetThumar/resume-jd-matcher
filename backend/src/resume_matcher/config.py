"""
config.py
=========
Centralised environment variable loading and application settings.

All other modules should import their configuration from here rather than
calling ``os.getenv`` directly.  This ensures:
  - ``.env`` is loaded exactly once.
  - Missing required variables raise an early, descriptive error.
  - Settings are typed and documented in one place.

Usage
-----
>>> from resume_matcher.config import settings
>>> print(settings.anthropic_api_key)
>>> print(settings.default_model)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from pathlib import Path

# Load .env explicitly from the backend directory
_backend_dir = Path(__file__).resolve().parent.parent.parent
_env_path = _backend_dir / ".env"
load_dotenv(_env_path)


def _require_env(name: str) -> str:
    """Read *name* from the environment, raising a descriptive error if absent.

    Args:
        name: The environment variable name to look up.

    Returns:
        The string value of the environment variable.

    Raises:
        EnvironmentError: If the variable is not set or is empty.
    """
    value = os.getenv(name, "").strip()
    if not value:
        raise EnvironmentError(
            f"\n\n[resume_matcher] Required environment variable '{name}' is not set.\n"
            f"  1. Copy .env.example → .env\n"
            f"  2. Fill in your Gemini API key.\n"
            f"  Get a key at: https://aistudio.google.com/\n"
        )
    return value


@dataclass(frozen=True)
class Settings:
    """Immutable application settings resolved from the environment.

    Attributes:
        gemini_api_key: Gemini API key (required).
        default_model:  Gemini model identifier used by default.
        max_tokens:     Maximum tokens for LLM responses.
    """

    gemini_api_key: str
    default_model: str = "gemini-2.5-flash"
    max_tokens: int = 4096


def _load_settings() -> Settings:
    """Build a :class:`Settings` instance from the current environment.

    Returns:
        A fully-populated, immutable :class:`Settings` object.

    Raises:
        EnvironmentError: If any required variable is missing.
    """
    return Settings(
        gemini_api_key=_require_env("GEMINI_API_KEY"),
        default_model=os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
        max_tokens=int(os.getenv("MAX_TOKENS", "4096")),
    )


# Module-level singleton — imported by other modules.
# Validation is deferred: this raises only when first accessed, not at import time,
# so tests can monkey-patch the env before the config is consumed.
settings: Settings  # populated below


def _get_settings() -> Settings:
    """Return the cached :class:`Settings` singleton, building it on first call."""
    global settings
    if "settings" not in globals() or globals()["settings"] is None:  # type: ignore[misc]
        globals()["settings"] = _load_settings()
    return globals()["settings"]  # type: ignore[return-value]


# Eager initialisation for normal runtime; tests may re-call _load_settings().
try:
    settings = _load_settings()
except EnvironmentError:
    # Allow the module to be imported even without the key (e.g. during testing).
    # Accessing `settings` directly will raise later in that case.
    settings = None  # type: ignore[assignment]

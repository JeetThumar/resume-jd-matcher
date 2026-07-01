"""
resume_matcher
==============
AI-powered resume ↔ job-description matching, powered by Claude (Anthropic).

Public API
----------
>>> from resume_matcher.config  import settings
>>> from resume_matcher.parser  import parse_uploaded_file
>>> from resume_matcher.matcher import match_resume_to_jd
"""

__version__ = "0.1.0"
__all__ = ["__version__"]

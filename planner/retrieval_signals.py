from __future__ import annotations

import re


_CURRENT_INFORMATION_PATTERNS = (
    r"\blatest\b",
    r"\brecent\b",
    r"\bcurrently\b",
    r"\bcurrent\b",
    r"\btoday\b",
    r"\bthis year\b",
    r"\bthis month\b",
    r"\bup[- ]to[- ]date\b",
)

_EXPLICIT_SEARCH_PATTERNS = (
    r"\bsearch the web\b",
    r"\bsearch online\b",
    r"\bsearch the internet\b",
    r"\blook (?:it )?up online\b",
    r"\blook (?:it )?up on the web\b",
)


def _matches_any(
    text: str,
    patterns: tuple[str, ...],
) -> bool:
    normalized = text.lower().strip()

    return any(
        re.search(pattern, normalized)
        for pattern in patterns
    )


def requires_current_information(user_input: str) -> bool:
    """
    Determine whether the request explicitly requires current information.

    This function detects temporal/currentness signals only.
    Words such as "explain" or "describe" do not imply current information.
    """
    return _matches_any(
        user_input,
        _CURRENT_INFORMATION_PATTERNS,
    )


def has_explicit_search_request(user_input: str) -> bool:
    """
    Determine whether the user explicitly requested online/web search.
    """
    return _matches_any(
        user_input,
        _EXPLICIT_SEARCH_PATTERNS,
    )

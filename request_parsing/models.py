from dataclasses import dataclass


@dataclass(frozen=True)
class RequestSegment:
    """One independently actionable segment of a user request."""

    text: str
    start: int
    end: int


@dataclass(frozen=True)
class RequestParseResult:
    """The result of parsing a complete user input."""

    original_text: str
    segments: tuple[RequestSegment, ...]
from dataclasses import dataclass
from enum import Enum
from typing import Tuple

@dataclass(frozen=True)
class Token:
    """A single token in a user request."""

    text: str
    start: int
    end: int
class ProtectedSpanKind(Enum):
    QUOTED_TEXT = "quoted_text"
    URL = "url"
    CODE = "code"
    FILE_PATH = "file_path"
    PARENTHETICAL = "parenthetical"
    BRACKETED = "bracketed"

@dataclass(frozen=True)
class ProtectedSpan:
    """A span of text that should be treated as a single unit during parsing."""
    start: int
    end: int
    kind: ProtectedSpanKind

class BoundarySignalType(Enum):
    """Types of signals that indicate boundaries in the input text."""

    PUNCTUATION = "punctuation"
    SEMICOLON = "semicolon"
    COORDINATOR = "coordinator"
    SEQUENCE_MARKER = "sequence_marker"
    COMMA = "comma"

@dataclass(frozen=True)
class CandidateBoundary:
    """A potential boundary in the input text."""

    left_end: int
    right_start: int
    trigger_start: int
    trigger_end: int
    signal_type: BoundarySignalType

class BoundaryLabel(Enum):
    ''' Labels for candidate boundaries in the input text.'''
    BOUNDARY = "boundary"
    CONTINUATION = "continuation"
    UNCERTAIN = "uncertain"

@dataclass(frozen=True)
class BoundaryPrediction:
    """A prediction about a candidate boundary in the input text."""

    candidate: CandidateBoundary
    label: BoundaryLabel
    boundary_probability: float | None = None
    evidence: Tuple[str, ...] = ()
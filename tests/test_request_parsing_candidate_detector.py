import pytest

from request_parsing.candidate_detector import CandidateDetector
from request_parsing.internal_models import (
    BoundarySignalType,
    CandidateBoundary,
    ProtectedSpan,
    ProtectedSpanKind,
    StructuralSignal,
)


@pytest.fixture
def detector():
    return CandidateDetector()


def make_signal(text, phrase, signal_type, occurrence=0):
    """Create a signal at a chosen occurrence of a phrase."""
    search_from = 0

    for _ in range(occurrence + 1):
        start = text.index(phrase, search_from)
        search_from = start + len(phrase)

    return StructuralSignal(
        start=start,
        end=start + len(phrase),
        signal_type=signal_type,
    )


def make_span(text, phrase, kind):
    """Create a protected span covering a phrase in the input."""
    start = text.index(phrase)

    return ProtectedSpan(
        start=start,
        end=start + len(phrase),
        kind=kind,
    )


# ---------------------------------------------------------
# Basic contract
# ---------------------------------------------------------

def test_no_signals_returns_empty_tuple(detector):
    text = "Open GitHub and explain Git"

    assert detector.detect(text, (), ()) == ()


def test_detector_returns_tuple_of_candidate_boundaries(detector):
    text = "Open GitHub and explain Git"
    signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR
    )

    result = detector.detect(text, (signal,), ())

    assert isinstance(result, tuple)
    assert all(isinstance(item, CandidateBoundary) for item in result)


def test_single_coordinator_generates_candidate(detector):
    text = "Open GitHub and explain Git"
    signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR
    )

    result = detector.detect(text, (signal,), ())

    assert len(result) == 1

    candidate = result[0]

    assert candidate.left_end == 11
    assert candidate.right_start == 16
    assert candidate.trigger_start == 12
    assert candidate.trigger_end == 15
    assert candidate.signal_type is BoundarySignalType.COORDINATOR


def test_candidate_offsets_reference_original_text(detector):
    text = "Open GitHub and explain Git"
    signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR
    )

    candidate = detector.detect(text, (signal,), ())[0]

    assert text[candidate.trigger_start:candidate.trigger_end] == "and"
    assert text[:candidate.left_end] == "Open GitHub"
    assert text[candidate.right_start:] == "explain Git"


# ---------------------------------------------------------
# Protected-span filtering
# ---------------------------------------------------------

def test_signal_inside_quoted_span_is_ignored(detector):
    text = 'Search for "AI and ML" papers.'

    signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR
    )
    protected = make_span(
        text, "AI and ML", ProtectedSpanKind.QUOTED_TEXT
    )

    assert detector.detect(text, (signal,), (protected,)) == ()


def test_signal_inside_parenthetical_span_is_ignored(detector):
    text = "Compare (Python and C++) carefully."

    signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR
    )
    protected = make_span(
        text, "Python and C++", ProtectedSpanKind.PARENTHETICAL
    )

    assert detector.detect(text, (signal,), (protected,)) == ()


def test_signal_outside_protected_span_remains_eligible(detector):
    text = 'Search "AI and ML" and explain Git.'

    inner_signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR, occurrence=0
    )
    outer_signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR, occurrence=1
    )
    protected = make_span(
        text, "AI and ML", ProtectedSpanKind.QUOTED_TEXT
    )

    result = detector.detect(
        text,
        (inner_signal, outer_signal),
        (protected,),
    )

    assert len(result) == 1
    assert result[0].trigger_start == outer_signal.start


def test_any_partial_overlap_with_protected_span_rejects_candidate(detector):
    text = "Open GitHub and explain Git"
    signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR
    )

    # Only part of the signal range overlaps the protected span.
    protected = ProtectedSpan(
        start=signal.start + 1,
        end=signal.end + 2,
        kind=ProtectedSpanKind.CODE,
    )

    assert detector.detect(text, (signal,), (protected,)) == ()


def test_unrelated_protected_span_does_not_suppress_candidate(detector):
    text = 'Search "AI and ML" and explain Git.'

    signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR, occurrence=1
    )
    protected = make_span(
        text, "AI and ML", ProtectedSpanKind.QUOTED_TEXT
    )

    result = detector.detect(text, (signal,), (protected,))

    assert len(result) == 1
    assert result[0].trigger_start == signal.start


# ---------------------------------------------------------
# Missing text on either side
# ---------------------------------------------------------

@pytest.mark.parametrize(
    ("text", "phrase"),
    [
        ("and explain Git", "and"),
        ("Open GitHub and", "and"),
        ("   then explain Git", "then"),
        ("Open GitHub then   ", "then"),
    ],
)
def test_signal_without_text_on_both_sides_is_ignored(
    detector, text, phrase
):
    signal_type = (
        BoundarySignalType.SEQUENCE_MARKER
        if phrase == "then"
        else BoundarySignalType.COORDINATOR
    )

    signal = make_signal(text, phrase, signal_type)

    assert detector.detect(text, (signal,), ()) == ()


# ---------------------------------------------------------
# Whitespace and exact offsets
# ---------------------------------------------------------

def test_multiple_spaces_are_excluded_from_fragments(detector):
    text = "  Open GitHub   and   explain Git  "
    signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR
    )

    result = detector.detect(text, (signal,), ())

    assert len(result) == 1
    candidate = result[0]

    assert text[:candidate.left_end].strip() == "Open GitHub"
    assert text[candidate.trigger_start:candidate.trigger_end] == "and"
    assert text[candidate.right_start:].strip() == "explain Git"

    assert not text[candidate.left_end:candidate.trigger_start].strip()
    assert not text[candidate.trigger_end:candidate.right_start].strip()


# ---------------------------------------------------------
# Multiple candidates and ordering
# ---------------------------------------------------------

def test_repeated_signals_generate_distinct_candidates(detector):
    text = "Open GitHub and then explain Git"

    coordinator = make_signal(
        text, "and", BoundarySignalType.COORDINATOR
    )
    sequence = make_signal(
        text, "then", BoundarySignalType.SEQUENCE_MARKER
    )

    result = detector.detect(
        text,
        (coordinator, sequence),
        (),
    )

    assert len(result) == 2
    assert result[0].trigger_start == coordinator.start
    assert result[1].trigger_start == sequence.start


def test_candidates_are_sorted_by_trigger_position(detector):
    text = "Open GitHub; then explain Git"

    sequence = make_signal(
        text, "then", BoundarySignalType.SEQUENCE_MARKER
    )
    semicolon = make_signal(
        text, ";", BoundarySignalType.SEMICOLON
    )

    # Pass signals in reverse order deliberately.
    result = detector.detect(
        text,
        (sequence, semicolon),
        (),
    )

    assert tuple(candidate.trigger_start for candidate in result) == tuple(
        sorted(candidate.trigger_start for candidate in result)
    )


def test_candidates_preserve_signal_types(detector):
    text = "Open GitHub; then explain Git"

    semicolon = make_signal(
        text, ";", BoundarySignalType.SEMICOLON
    )
    sequence = make_signal(
        text, "then", BoundarySignalType.SEQUENCE_MARKER
    )

    result = detector.detect(text, (semicolon, sequence), ())

    assert result[0].signal_type is BoundarySignalType.SEMICOLON
    assert result[1].signal_type is BoundarySignalType.SEQUENCE_MARKER


# ---------------------------------------------------------
# Classification remains out of scope
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "text",
    [
        "Open GitHub and explain Git",
        "Explain Python and C++",
    ],
)
def test_coordinator_generates_candidate_without_classifying(
    detector, text
):
    signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR
    )

    result = detector.detect(text, (signal,), ())

    assert len(result) == 1
    assert isinstance(result[0], CandidateBoundary)
    assert result[0].signal_type is BoundarySignalType.COORDINATOR


# ---------------------------------------------------------
# Determinism
# ---------------------------------------------------------

def test_candidate_generation_is_deterministic(detector):
    text = "Open GitHub and explain Git"
    signal = make_signal(
        text, "and", BoundarySignalType.COORDINATOR
    )

    first = detector.detect(text, (signal,), ())
    second = detector.detect(text, (signal,), ())

    assert first == second

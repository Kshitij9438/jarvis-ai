from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from request_parsing.internal_models import (
    Token,
    ProtectedSpan,
    ProtectedSpanKind,
    BoundarySignalType,
    CandidateBoundary,
    BoundaryLabel,
    BoundaryPrediction,
)


# ---------------------------------------------------------
# Token
# ---------------------------------------------------------

def test_token_is_frozen_dataclass():
    token = Token(text="GitHub", start=5, end=11)

    assert is_dataclass(Token)
    assert Token.__dataclass_params__.frozen
    assert token.text == "GitHub"
    assert token.start == 5
    assert token.end == 11


def test_token_equality_uses_field_values():
    first = Token(text="GitHub", start=5, end=11)
    second = Token(text="GitHub", start=5, end=11)

    assert first == second


def test_token_is_immutable():
    token = Token(text="GitHub", start=5, end=11)

    with pytest.raises(FrozenInstanceError):
        token.text = "Git"


def test_token_offsets_reference_original_text():
    original = "Open GitHub and explain Git"
    token = Token(text="GitHub", start=5, end=11)

    assert original[token.start:token.end] == token.text
    assert token.end - token.start == len(token.text)


# ---------------------------------------------------------
# ProtectedSpan
# ---------------------------------------------------------

def test_protected_span_is_frozen_dataclass():
    span = ProtectedSpan(
        start=11,
        end=36,
        kind=ProtectedSpanKind.QUOTED_TEXT,
    )

    assert is_dataclass(ProtectedSpan)
    assert ProtectedSpan.__dataclass_params__.frozen
    assert span.start == 11
    assert span.end == 36
    assert span.kind is ProtectedSpanKind.QUOTED_TEXT


def test_protected_span_equality_uses_field_values():
    first = ProtectedSpan(11, 36, ProtectedSpanKind.QUOTED_TEXT)
    second = ProtectedSpan(11, 36, ProtectedSpanKind.QUOTED_TEXT)

    assert first == second


def test_protected_span_is_immutable():
    span = ProtectedSpan(11, 36, ProtectedSpanKind.QUOTED_TEXT)

    with pytest.raises(FrozenInstanceError):
        span.start = 10


def test_protected_span_kind_enum_values():
    assert ProtectedSpanKind.QUOTED_TEXT.value == "quoted_text"
    assert ProtectedSpanKind.URL.value == "url"
    assert ProtectedSpanKind.CODE.value == "code"
    assert ProtectedSpanKind.FILE_PATH.value == "file_path"
    assert ProtectedSpanKind.PARENTHETICAL.value == "parenthetical"
    assert ProtectedSpanKind.BRACKETED.value == "bracketed"


# ---------------------------------------------------------
# CandidateBoundary
# ---------------------------------------------------------

def test_candidate_boundary_is_frozen_dataclass():
    candidate = CandidateBoundary(
        left_end=11,
        right_start=16,
        trigger_start=12,
        trigger_end=15,
        signal_type=BoundarySignalType.COORDINATOR,
    )

    assert is_dataclass(CandidateBoundary)
    assert CandidateBoundary.__dataclass_params__.frozen
    assert candidate.left_end == 11
    assert candidate.right_start == 16
    assert candidate.trigger_start == 12
    assert candidate.trigger_end == 15
    assert candidate.signal_type is BoundarySignalType.COORDINATOR


def test_candidate_boundary_keeps_split_and_trigger_positions_separate():
    candidate = CandidateBoundary(
        left_end=11,
        right_start=16,
        trigger_start=12,
        trigger_end=15,
        signal_type=BoundarySignalType.COORDINATOR,
    )

    assert candidate.left_end < candidate.trigger_start
    assert candidate.trigger_start < candidate.trigger_end
    assert candidate.trigger_end < candidate.right_start


def test_candidate_boundary_trigger_references_original_text():
    original = "Open GitHub and explain Git"

    candidate = CandidateBoundary(
        left_end=11,
        right_start=16,
        trigger_start=12,
        trigger_end=15,
        signal_type=BoundarySignalType.COORDINATOR,
    )

    assert original[candidate.left_end:candidate.trigger_start] == " "
    assert original[candidate.trigger_start:candidate.trigger_end] == "and"
    assert original[candidate.trigger_end:candidate.right_start] == " "


def test_candidate_boundary_is_immutable():
    candidate = CandidateBoundary(
        left_end=11,
        right_start=16,
        trigger_start=12,
        trigger_end=15,
        signal_type=BoundarySignalType.COORDINATOR,
    )

    with pytest.raises(FrozenInstanceError):
        candidate.left_end = 10


def test_boundary_signal_type_enum_values():
    assert BoundarySignalType.PUNCTUATION.value == "punctuation"
    assert BoundarySignalType.SEMICOLON.value == "semicolon"
    assert BoundarySignalType.COORDINATOR.value == "coordinator"
    assert BoundarySignalType.SEQUENCE_MARKER.value == "sequence_marker"
    assert BoundarySignalType.COMMA.value == "comma"


# ---------------------------------------------------------
# BoundaryPrediction
# ---------------------------------------------------------

@pytest.fixture
def sample_candidate():
    return CandidateBoundary(
        left_end=11,
        right_start=16,
        trigger_start=12,
        trigger_end=15,
        signal_type=BoundarySignalType.COORDINATOR,
    )


def test_boundary_prediction_is_frozen_dataclass(sample_candidate):
    prediction = BoundaryPrediction(
        candidate=sample_candidate,
        label=BoundaryLabel.BOUNDARY,
        boundary_probability=0.93,
        evidence=("two action-like clauses",),
    )

    assert is_dataclass(BoundaryPrediction)
    assert BoundaryPrediction.__dataclass_params__.frozen
    assert prediction.candidate == sample_candidate
    assert prediction.label is BoundaryLabel.BOUNDARY
    assert prediction.boundary_probability == 0.93
    assert prediction.evidence == ("two action-like clauses",)


def test_boundary_prediction_references_assessed_candidate(sample_candidate):
    prediction = BoundaryPrediction(
        candidate=sample_candidate,
        label=BoundaryLabel.CONTINUATION,
        boundary_probability=0.08,
        evidence=("single action with coordinated objects",),
    )

    assert prediction.candidate is sample_candidate


def test_boundary_prediction_evidence_defaults_to_empty_tuple(
    sample_candidate,
):
    prediction = BoundaryPrediction(
        candidate=sample_candidate,
        label=BoundaryLabel.UNCERTAIN,
        boundary_probability=0.5,
    )

    assert prediction.evidence == ()
    assert isinstance(prediction.evidence, tuple)


def test_boundary_prediction_evidence_is_immutable(sample_candidate):
    prediction = BoundaryPrediction(
        candidate=sample_candidate,
        label=BoundaryLabel.BOUNDARY,
        boundary_probability=0.93,
        evidence=("structural signal",),
    )

    with pytest.raises(FrozenInstanceError):
        prediction.label = BoundaryLabel.CONTINUATION


def test_boundary_prediction_equality_uses_field_values(sample_candidate):
    first = BoundaryPrediction(
        candidate=sample_candidate,
        label=BoundaryLabel.BOUNDARY,
        boundary_probability=0.93,
        evidence=("structural signal",),
    )

    second = BoundaryPrediction(
        candidate=sample_candidate,
        label=BoundaryLabel.BOUNDARY,
        boundary_probability=0.93,
        evidence=("structural signal",),
    )

    assert first == second


def test_boundary_label_enum_values():
    assert BoundaryLabel.BOUNDARY.value == "boundary"
    assert BoundaryLabel.CONTINUATION.value == "continuation"
    assert BoundaryLabel.UNCERTAIN.value == "uncertain"

def test_boundary_probability_can_be_absent(sample_candidate):
    prediction = BoundaryPrediction(
        candidate=sample_candidate,
        label=BoundaryLabel.UNCERTAIN,
    )

    assert prediction.boundary_probability is None

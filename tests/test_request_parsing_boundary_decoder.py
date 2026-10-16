import pytest

from request_parsing.boundary_decoder import BoundaryDecoder
from request_parsing.internal_models import (
    BoundaryLabel,
    BoundaryPrediction,
    BoundarySignalType,
    CandidateBoundary,
)


def make_candidate(
    trigger_start: int,
    trigger_text_length: int = 3,
    signal_type: BoundarySignalType = BoundarySignalType.COORDINATOR,
) -> CandidateBoundary:
    """Build a candidate with one whitespace character on either side."""
    trigger_end = trigger_start + trigger_text_length
    return CandidateBoundary(
        left_end=trigger_start - 1,
        right_start=trigger_end + 1,
        trigger_start=trigger_start,
        trigger_end=trigger_end,
        signal_type=signal_type,
    )


def make_prediction(
    candidate: CandidateBoundary,
    label: BoundaryLabel,
    evidence: tuple[str, ...] = ("test_evidence",),
) -> BoundaryPrediction:
    return BoundaryPrediction(
        candidate=candidate,
        label=label,
        boundary_probability=None,
        evidence=evidence,
    )


def test_empty_predictions_returns_empty_tuple() -> None:
    decoder = BoundaryDecoder()

    result = decoder.decode(())

    assert result == ()
    assert isinstance(result, tuple)


def test_boundary_prediction_is_accepted() -> None:
    decoder = BoundaryDecoder()
    prediction = make_prediction(
        make_candidate(10),
        BoundaryLabel.BOUNDARY,
    )

    result = decoder.decode((prediction,))

    assert result == (prediction,)
    assert result[0] is prediction


def test_continuation_prediction_is_rejected() -> None:
    decoder = BoundaryDecoder()
    prediction = make_prediction(
        make_candidate(10),
        BoundaryLabel.CONTINUATION,
    )

    result = decoder.decode((prediction,))

    assert result == ()


def test_uncertain_prediction_is_rejected_conservatively() -> None:
    decoder = BoundaryDecoder()
    prediction = make_prediction(
        make_candidate(10),
        BoundaryLabel.UNCERTAIN,
    )

    result = decoder.decode((prediction,))

    assert result == ()


def test_mixed_predictions_keep_only_boundaries() -> None:
    decoder = BoundaryDecoder()
    accepted = make_prediction(
        make_candidate(20),
        BoundaryLabel.BOUNDARY,
    )
    continuation = make_prediction(
        make_candidate(10),
        BoundaryLabel.CONTINUATION,
    )
    uncertain = make_prediction(
        make_candidate(30),
        BoundaryLabel.UNCERTAIN,
    )

    result = decoder.decode((continuation, accepted, uncertain))

    assert result == (accepted,)
    assert result[0] is accepted


def test_accepted_predictions_are_returned_in_text_order() -> None:
    decoder = BoundaryDecoder()
    later = make_prediction(
        make_candidate(30),
        BoundaryLabel.BOUNDARY,
    )
    earlier = make_prediction(
        make_candidate(10),
        BoundaryLabel.BOUNDARY,
    )
    middle = make_prediction(
        make_candidate(20),
        BoundaryLabel.BOUNDARY,
    )

    result = decoder.decode((later, earlier, middle))

    assert result == (earlier, middle, later)
    assert result[0] is earlier
    assert result[1] is middle
    assert result[2] is later


def test_duplicate_accepted_candidate_is_returned_only_once() -> None:
    decoder = BoundaryDecoder()
    candidate = make_candidate(10)
    first = make_prediction(
        candidate,
        BoundaryLabel.BOUNDARY,
        evidence=("first_prediction",),
    )
    duplicate = make_prediction(
        candidate,
        BoundaryLabel.BOUNDARY,
        evidence=("duplicate_prediction",),
    )

    result = decoder.decode((first, duplicate))

    assert result == (first,)
    assert len(result) == 1
    assert result[0] is first


def test_prediction_objects_and_evidence_are_preserved() -> None:
    decoder = BoundaryDecoder()
    prediction = make_prediction(
        make_candidate(10),
        BoundaryLabel.BOUNDARY,
        evidence=("explicit_sequence_marker", "strong_signal"),
    )

    result = decoder.decode((prediction,))

    assert result[0] is prediction
    assert result[0].candidate is prediction.candidate
    assert result[0].evidence == (
        "explicit_sequence_marker",
        "strong_signal",
    )
    assert result[0].boundary_probability is None


def test_input_tuple_is_not_modified() -> None:
    decoder = BoundaryDecoder()
    first = make_prediction(
        make_candidate(20),
        BoundaryLabel.BOUNDARY,
    )
    second = make_prediction(
        make_candidate(10),
        BoundaryLabel.CONTINUATION,
    )
    predictions = (first, second)
    original_predictions = predictions

    decoder.decode(predictions)

    assert predictions is original_predictions
    assert predictions == (first, second)
    assert predictions[0] is first
    assert predictions[1] is second


def test_repeated_calls_are_deterministic() -> None:
    decoder = BoundaryDecoder()
    predictions = (
        make_prediction(make_candidate(20), BoundaryLabel.BOUNDARY),
        make_prediction(make_candidate(10), BoundaryLabel.BOUNDARY),
        make_prediction(make_candidate(30), BoundaryLabel.UNCERTAIN),
    )

    first_result = decoder.decode(predictions)
    second_result = decoder.decode(predictions)

    assert first_result == second_result


def test_decoder_returns_a_tuple() -> None:
    decoder = BoundaryDecoder()
    prediction = make_prediction(
        make_candidate(10),
        BoundaryLabel.BOUNDARY,
    )

    result = decoder.decode((prediction,))

    assert isinstance(result, tuple)


@pytest.mark.parametrize(
    ("label", "expected_count"),
    [
        (BoundaryLabel.BOUNDARY, 1),
        (BoundaryLabel.CONTINUATION, 0),
        (BoundaryLabel.UNCERTAIN, 0),
    ],
)
def test_acceptance_policy_for_each_label(
    label: BoundaryLabel,
    expected_count: int,
) -> None:
    decoder = BoundaryDecoder()
    prediction = make_prediction(make_candidate(10), label)

    result = decoder.decode((prediction,))

    assert len(result) == expected_count

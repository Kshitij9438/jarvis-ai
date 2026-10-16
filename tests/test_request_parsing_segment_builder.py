from request_parsing.internal_models import (
    BoundaryLabel,
    BoundaryPrediction,
    BoundarySignalType,
    CandidateBoundary,
)
from request_parsing.models import RequestParseResult, RequestSegment
from request_parsing.segment_builder import SegmentBuilder


def make_prediction(
    left_end: int,
    right_start: int,
    trigger_start: int,
    trigger_end: int,
    signal_type: BoundarySignalType = BoundarySignalType.COORDINATOR,
) -> BoundaryPrediction:
    candidate = CandidateBoundary(
        left_end=left_end,
        right_start=right_start,
        trigger_start=trigger_start,
        trigger_end=trigger_end,
        signal_type=signal_type,
    )

    return BoundaryPrediction(
        candidate=candidate,
        label=BoundaryLabel.BOUNDARY,
        evidence=("test_boundary",),
    )


def test_empty_input_returns_empty_result() -> None:
    builder = SegmentBuilder()

    result = builder.build("", ())

    assert result == RequestParseResult(
        original_text="",
        segments=(),
    )


def test_whitespace_only_input_returns_empty_segments() -> None:
    builder = SegmentBuilder()

    result = builder.build("   \t\n  ", ())

    assert result.original_text == "   \t\n  "
    assert result.segments == ()


def test_single_request_without_boundaries() -> None:
    builder = SegmentBuilder()
    text = "Open GitHub"

    result = builder.build(text, ())

    assert result == RequestParseResult(
        original_text=text,
        segments=(
            RequestSegment(text="Open GitHub", start=0, end=11),
        ),
    )


def test_outer_whitespace_is_trimmed_without_losing_offsets() -> None:
    builder = SegmentBuilder()
    text = "  Open GitHub  "

    result = builder.build(text, ())

    assert result.segments == (
        RequestSegment(text="Open GitHub", start=2, end=13),
    )
    segment = result.segments[0]
    assert text[segment.start:segment.end] == segment.text


def test_one_boundary_creates_two_segments() -> None:
    builder = SegmentBuilder()
    text = "Open GitHub and explain Git."

    prediction = make_prediction(
        left_end=11,
        right_start=16,
        trigger_start=12,
        trigger_end=15,
    )

    result = builder.build(text, (prediction,))

    assert result.segments == (
        RequestSegment(text="Open GitHub", start=0, end=11),
        RequestSegment(text="explain Git.", start=16, end=28),
    )


def test_multiple_boundaries_create_ordered_segments() -> None:
    builder = SegmentBuilder()
    text = "Open GitHub and explain Git then summarize Git."

    first = make_prediction(
        left_end=11,
        right_start=16,
        trigger_start=12,
        trigger_end=15,
    )
    second = make_prediction(
        left_end=27,
        right_start=33,
        trigger_start=28,
        trigger_end=32,
        signal_type=BoundarySignalType.SEQUENCE_MARKER,
    )

    result = builder.build(text, (first, second))

    assert result.segments == (
        RequestSegment(text="Open GitHub", start=0, end=11),
        RequestSegment(text="explain Git", start=16, end=27),
        RequestSegment(text="summarize Git.", start=33, end=47),
    )


def test_unsorted_predictions_still_produce_text_order() -> None:
    builder = SegmentBuilder()
    text = "Open GitHub and explain Git then summarize Git."

    first = make_prediction(11, 16, 12, 15)
    second = make_prediction(
        27,
        33,
        28,
        32,
        BoundarySignalType.SEQUENCE_MARKER,
    )

    result = builder.build(text, (second, first))

    assert [segment.text for segment in result.segments] == [
        "Open GitHub",
        "explain Git",
        "summarize Git.",
    ]


def test_all_segment_offsets_reference_original_text() -> None:
    builder = SegmentBuilder()
    text = "Open GitHub and explain Git then summarize Git."

    predictions = (
        make_prediction(11, 16, 12, 15),
        make_prediction(
            27,
            33,
            28,
            32,
            BoundarySignalType.SEQUENCE_MARKER,
        ),
    )

    result = builder.build(text, predictions)

    assert result.original_text == text

    for segment in result.segments:
        assert text[segment.start:segment.end] == segment.text
        assert 0 <= segment.start < segment.end <= len(text)


def test_input_predictions_are_not_modified() -> None:
    builder = SegmentBuilder()
    text = "Open GitHub and explain Git."
    prediction = make_prediction(11, 16, 12, 15)
    predictions = (prediction,)

    builder.build(text, predictions)

    assert predictions == (prediction,)


def test_repeated_calls_are_deterministic() -> None:
    builder = SegmentBuilder()
    text = "Open GitHub and explain Git."
    predictions = (make_prediction(11, 16, 12, 15),)

    first_result = builder.build(text, predictions)
    second_result = builder.build(text, predictions)

    assert first_result == second_result
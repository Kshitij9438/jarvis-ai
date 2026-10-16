
from request_parsing.models import RequestParseResult, RequestSegment
from request_parsing.parser import RequestParser


def test_empty_input_returns_empty_result() -> None:
    result = RequestParser().parse("")

    assert result == RequestParseResult(
        original_text="",
        segments=(),
    )


def test_whitespace_only_input_returns_empty_segments() -> None:
    text = "   \t\n  "

    result = RequestParser().parse(text)

    assert result.original_text == text
    assert result.segments == ()


def test_single_request_without_boundary() -> None:
    text = "Open GitHub"

    result = RequestParser().parse(text)

    assert result.segments == (
        RequestSegment(text=text, start=0, end=len(text)),
    )


def test_and_between_two_actions_creates_two_segments() -> None:
    text = "Open GitHub and explain Git."

    result = RequestParser().parse(text)

    assert result.segments == (
        RequestSegment(text="Open GitHub", start=0, end=11),
        RequestSegment(text="explain Git.", start=16, end=28),
    )


def test_and_between_objects_does_not_split_request() -> None:
    text = "Explain Python and C++"

    result = RequestParser().parse(text)

    assert result.segments == (
        RequestSegment(text=text, start=0, end=len(text)),
    )


def test_sequence_marker_creates_two_segments() -> None:
    text = "Open GitHub then explain Git."

    result = RequestParser().parse(text)

    assert result.segments == (
        RequestSegment(text="Open GitHub", start=0, end=11),
        RequestSegment(text="explain Git.", start=17, end=29),
    )


def test_coordinator_inside_quoted_text_does_not_split() -> None:
    text = 'Open the page named "rock and roll"'

    result = RequestParser().parse(text)

    assert result.segments == (
        RequestSegment(text=text, start=0, end=len(text)),
    )


def test_sentence_punctuation_separates_requests() -> None:
    text = "Open GitHub. Explain Git"

    result = RequestParser().parse(text)

    assert result.segments == (
        RequestSegment(text="Open GitHub", start=0, end=11),
        RequestSegment(text="Explain Git", start=13, end=24),
    )


def test_multiple_boundaries_create_three_segments() -> None:
    text = "Open GitHub and explain Git then summarize Git."

    result = RequestParser().parse(text)

    assert result.segments == (
        RequestSegment(text="Open GitHub", start=0, end=11),
        RequestSegment(text="explain Git", start=16, end=27),
        RequestSegment(text="summarize Git.", start=33, end=47),
    )


def test_segment_offsets_reference_original_input() -> None:
    text = "Open GitHub and explain Git then summarize Git."

    result = RequestParser().parse(text)

    assert result.original_text == text

    for segment in result.segments:
        assert text[segment.start:segment.end] == segment.text


def test_parser_is_deterministic() -> None:
    parser = RequestParser()
    text = "Open GitHub and explain Git."

    assert parser.parse(text) == parser.parse(text)

def test_and_then_splits_before_and_and_after_then():
    cases = (
        (
            "Open GitHub and then explain Git",
            ("Open GitHub", "explain Git"),
        ),
        (
            "Explain the code and then run the tests",
            ("Explain the code", "run the tests"),
        ),
        (
            "Download the dataset and then clean it.",
            ("Download the dataset", "clean it."),
        ),
    )

    parser = RequestParser()

    for text, expected_segments in cases:
        result = parser.parse(text)

        assert tuple(
            segment.text for segment in result.segments
        ) == expected_segments
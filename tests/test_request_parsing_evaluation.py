
import pytest

from request_parsing.parser import RequestParser


@pytest.mark.parametrize(
    ("text", "expected_segments"),
    [
        pytest.param(
            "Open GitHub",
            ("Open GitHub",),
            id="single-request",
        ),
        pytest.param(
            "Open GitHub and explain Git.",
            ("Open GitHub", "explain Git."),
            id="two-independent-actions",
        ),
        pytest.param(
            "Explain Python and C++",
            ("Explain Python and C++",),
            id="coordinated-objects-do-not-split",
        ),
        pytest.param(
            "Open GitHub or open GitLab",
            ("Open GitHub or open GitLab",),
            id="alternatives-do-not-split",
        ),
        pytest.param(
            'Search for "rock and roll"',
            ('Search for "rock and roll"',),
            id="quoted-coordinator-is-protected",
        ),
        pytest.param(
            "Open https://example.com and summarize it",
            ("Open https://example.com", "summarize it"),
            id="url-is-preserved-and-request-splits-after-it",
        ),
        pytest.param(
            "Open GitHub, then explain Git, then summarize it",
            ("Open GitHub,", "explain Git,", "summarize it"),
            id="multiple-sequence-markers",
        ),
        pytest.param(
            "Open GitHub. Explain Git",
            ("Open GitHub", "Explain Git"),
            id="sentence-punctuation",
        ),
        pytest.param(
            "Open the planner and documentation",
            ("Open the planner and documentation",),
            id="ambiguous-coordinated-nouns",
        ),
        pytest.param(
            "Open GitHub; explain Git",
            ("Open GitHub", "explain Git"),
            id="semicolon-separates-actions",
        ),
        pytest.param(
            "Explain (Python and C++) and compare with Java",
            ("Explain (Python and C++)", "compare with Java"),
            id="coordinator-inside-parentheses-is-protected",
        ),
        pytest.param(
            "Explain `x and y` and compare with Java.",
            ("Explain `x and y`", "compare with Java."),
            id="coordinator-inside-inline-code-is-protected",
        ),
        pytest.param(
            "  Open GitHub.  Explain Git! ",
            ("Open GitHub", "Explain Git!"),
            id="leading-trailing-and-repeated-whitespace",
        ),
        pytest.param(
            "Open GitHub but explain Git",
            ("Open GitHub but explain Git",),
            id="contrast-is-not-automatically-split",
        ),
        pytest.param(
            "Open GitHub then explain Git then summarize Git.",
            ("Open GitHub", "explain Git", "summarize Git."),
            id="multiple-sequential-actions",
        ),
    ],
)
def test_realistic_request_segmentation(
    text: str,
    expected_segments: tuple[str, ...],
) -> None:
    """Check segmentation outcomes against a realistic evaluation set."""
    result = RequestParser().parse(text)

    assert result.original_text == text
    assert tuple(segment.text for segment in result.segments) == (
        expected_segments
    )

    previous_end = 0

    for segment in result.segments:
        # Segments must have valid, non-empty ranges in the original text.
        assert 0 <= segment.start < segment.end <= len(text)

        # Each segment must reference the exact original substring.
        assert text[segment.start:segment.end] == segment.text

        # Segments must be ordered and must not overlap.
        assert segment.start >= previous_end

        # Empty or whitespace-only segments are not permitted.
        assert segment.text.strip()

        previous_end = segment.end


def test_empty_request_produces_no_segments() -> None:
    result = RequestParser().parse("")

    assert result.original_text == ""
    assert result.segments == ()


@pytest.mark.parametrize(
    "text",
    [
        " ",
        "   ",
        "\t",
        "\n",
        " \t\n  ",
    ],
)
def test_whitespace_only_requests_produce_no_segments(
    text: str,
) -> None:
    result = RequestParser().parse(text)

    assert result.original_text == text
    assert result.segments == ()


def test_original_input_is_preserved_exactly() -> None:
    text = "  Open GitHub and explain Git.  "

    result = RequestParser().parse(text)

    assert result.original_text == text


def test_repeated_parsing_is_deterministic() -> None:
    parser = RequestParser()
    text = "Open GitHub, then explain Git, then summarize it"

    first_result = parser.parse(text)
    second_result = parser.parse(text)

    assert first_result == second_result


def test_segments_are_returned_in_original_text_order() -> None:
    text = "Open GitHub then explain Git then summarize Git."

    result = RequestParser().parse(text)

    starts = [segment.start for segment in result.segments]

    assert starts == sorted(starts)


def test_segments_do_not_include_sequence_markers() -> None:
    text = "Open GitHub then explain Git."

    result = RequestParser().parse(text)

    assert tuple(segment.text for segment in result.segments) == (
        "Open GitHub",
        "explain Git.",
    )

    assert all(
        "then" not in segment.text.casefold()
        for segment in result.segments
    )


def test_parser_does_not_create_empty_segments_between_boundaries() -> None:
    text = "Open GitHub then explain Git then summarize it"

    result = RequestParser().parse(text)

    assert result.segments
    assert all(segment.text.strip() for segment in result.segments)


def test_every_segment_offset_reconstructs_its_text() -> None:
    text = (
        'Open https://example.com and search for "rock and roll" '
        "then summarize it."
    )

    result = RequestParser().parse(text)

    for segment in result.segments:
        assert text[segment.start:segment.end] == segment.text


def test_and_also_separates_following_action():
    text = (
        "open github and github, then explain git and explain git again, "
        "and also open youtube"
    )

    result = RequestParser().parse(text)

    assert tuple(segment.text for segment in result.segments) == (
        "open github and github,",
        "explain git",
        "explain git again,",
        "open youtube",
    )

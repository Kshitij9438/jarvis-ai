import pytest

from request_parsing.internal_models import ProtectedSpan, ProtectedSpanKind
from request_parsing.protected_spans import ProtectedSpanDetector


@pytest.fixture
def detector():
    return ProtectedSpanDetector()


def spans_of_kind(spans, kind):
    return tuple(span for span in spans if span.kind is kind)


def test_empty_input_returns_empty_tuple(detector):
    assert detector.detect("") == ()
    assert detector.detect("   \t\n") == ()


def test_detector_returns_tuple(detector):
    spans = detector.detect('Search for "AI and ML".')

    assert isinstance(spans, tuple)
    assert all(isinstance(span, ProtectedSpan) for span in spans)


def test_quoted_text_excludes_quote_delimiters(detector):
    text = 'Search for "AI and ML" papers.'

    spans = detector.detect(text)
    quoted = spans_of_kind(spans, ProtectedSpanKind.QUOTED_TEXT)

    assert len(quoted) == 1
    assert text[quoted[0].start:quoted[0].end] == "AI and ML"


def test_parenthetical_and_bracketed_spans_exclude_delimiters(detector):
    text = "Compare (Python and C++) [for beginners]."

    spans = detector.detect(text)

    parentheses = spans_of_kind(spans, ProtectedSpanKind.PARENTHETICAL)
    brackets = spans_of_kind(spans, ProtectedSpanKind.BRACKETED)

    assert len(parentheses) == 1
    assert text[parentheses[0].start:parentheses[0].end] == "Python and C++"

    assert len(brackets) == 1
    assert text[brackets[0].start:brackets[0].end] == "for beginners"


def test_url_span_preserves_exact_offsets(detector):
    text = "Open https://example.com/docs now."

    spans = detector.detect(text)
    urls = spans_of_kind(spans, ProtectedSpanKind.URL)

    assert len(urls) == 1
    assert text[urls[0].start:urls[0].end] == "https://example.com/docs"


def test_code_span_excludes_backticks(detector):
    text = "Run `df -h` now."

    spans = detector.detect(text)
    code_spans = spans_of_kind(spans, ProtectedSpanKind.CODE)

    assert len(code_spans) == 1
    assert text[code_spans[0].start:code_spans[0].end] == "df -h"


def test_file_path_span_preserves_exact_offsets(detector):
    text = "Open /home/kshitij/project/main.py now."

    spans = detector.detect(text)
    paths = spans_of_kind(spans, ProtectedSpanKind.FILE_PATH)

    assert len(paths) == 1
    assert text[paths[0].start:paths[0].end] == (
        "/home/kshitij/project/main.py"
    )


def test_nested_spans_are_preserved(detector):
    text = 'Search for "machine learning (and deep learning)" in my notes.'

    spans = detector.detect(text)

    quoted = spans_of_kind(spans, ProtectedSpanKind.QUOTED_TEXT)
    parentheses = spans_of_kind(spans, ProtectedSpanKind.PARENTHETICAL)

    assert len(quoted) == 1
    assert len(parentheses) == 1

    quoted_text = text[quoted[0].start:quoted[0].end]
    parenthetical_text = text[parentheses[0].start:parentheses[0].end]

    assert quoted_text == "machine learning (and deep learning)"
    assert parenthetical_text == "and deep learning"

    # The parenthetical content is nested inside the quoted content.
    assert quoted[0].start <= parentheses[0].start
    assert parentheses[0].end <= quoted[0].end


def test_identical_ranges_with_different_kinds_are_preserved(detector):
    text = 'Open "https://example.com/docs" now.'

    spans = detector.detect(text)

    quoted = spans_of_kind(spans, ProtectedSpanKind.QUOTED_TEXT)
    urls = spans_of_kind(spans, ProtectedSpanKind.URL)

    assert len(quoted) == 1
    assert len(urls) == 1

    # Both detectors identify the same text for different reasons.
    assert (quoted[0].start, quoted[0].end) == (
        urls[0].start,
        urls[0].end,
    )


def test_repeated_identical_text_has_distinct_offsets(detector):
    text = 'Find "AI and ML", then search for "AI and ML".'

    spans = detector.detect(text)
    quoted = spans_of_kind(spans, ProtectedSpanKind.QUOTED_TEXT)

    assert len(quoted) == 2

    assert text[quoted[0].start:quoted[0].end] == "AI and ML"
    assert text[quoted[1].start:quoted[1].end] == "AI and ML"

    assert quoted[0].start < quoted[1].start
    assert quoted[0].start != quoted[1].start


def test_spans_are_sorted_deterministically(detector):
    text = 'Check [notes] and "AI and ML" at https://example.com/docs.'

    first = detector.detect(text)
    second = detector.detect(text)

    assert first == second

    expected = tuple(
        sorted(
            first,
            key=lambda span: (
                span.start,
                -(span.end - span.start),
                span.kind.value,
            ),
        )
    )

    assert first == expected


def test_all_span_offsets_reference_original_text(detector):
    text = (
        'Search "AI and ML", compare (Python and C++), '
        "and open https://example.com/docs."
    )

    for span in detector.detect(text):
        assert 0 <= span.start < span.end <= len(text)
        assert text[span.start:span.end]


def test_unmatched_opening_quote_is_tolerated(detector):
    text = 'Search for "AI and ML then explain Git.'

    spans = detector.detect(text)
    quoted = spans_of_kind(spans, ProtectedSpanKind.QUOTED_TEXT)

    assert len(quoted) == 1
    assert text[quoted[0].start:quoted[0].end] == (
        "AI and ML then explain Git."
    )


def test_unmatched_closing_quote_is_tolerated(detector):
    text = 'Search for AI and ML" then explain Git.'

    spans = detector.detect(text)

    # An unmatched closing quote does not start a new quoted span.
    assert spans_of_kind(spans, ProtectedSpanKind.QUOTED_TEXT) == ()


def test_unmatched_opening_parenthesis_is_tolerated(detector):
    text = "Compare Python (and C++ then explain Git."

    spans = detector.detect(text)
    parentheses = spans_of_kind(spans, ProtectedSpanKind.PARENTHETICAL)

    assert len(parentheses) == 1
    assert text[parentheses[0].start:parentheses[0].end] == (
        "and C++ then explain Git."
    )


def test_unmatched_closing_parenthesis_is_tolerated(detector):
    text = "Compare Python and C++) then explain Git."

    spans = detector.detect(text)

    assert spans_of_kind(spans, ProtectedSpanKind.PARENTHETICAL) == ()

import pytest

from request_parsing.internal_models import (
    BoundarySignalType,
    StructuralSignal,
)
from request_parsing.structural_scanner import StructuralScanner
from request_parsing.tokenizer import Tokenizer


@pytest.fixture
def scanner():
    return StructuralScanner(Tokenizer())


def test_scan_empty_input(scanner):
    assert scanner.scan("") == ()


@pytest.mark.parametrize(
    ("text", "signal_text", "expected_type"),
    [
        ("Open GitHub.", ".", BoundarySignalType.PUNCTUATION),
        ("Continue?", "?", BoundarySignalType.PUNCTUATION),
        ("Stop!", "!", BoundarySignalType.PUNCTUATION),
        ("First; second", ";", BoundarySignalType.SEMICOLON),
        ("Open GitHub, then explain Git", ",", BoundarySignalType.COMMA),
        ("Open GitHub and explain Git", "and", BoundarySignalType.COORDINATOR),
        ("Open GitHub or explain Git", "or", BoundarySignalType.COORDINATOR),
        ("Open GitHub but explain Git", "but", BoundarySignalType.COORDINATOR),
        ("Open GitHub then explain Git", "then", BoundarySignalType.SEQUENCE_MARKER),
        ("Open GitHub next explain Git", "next", BoundarySignalType.SEQUENCE_MARKER),
        ("Open GitHub after that explain Git", "after that", BoundarySignalType.SEQUENCE_MARKER),
    ],
)
def test_detect_signal_type(scanner, text, signal_text, expected_type):
    signals = scanner.scan(text)

    matching = [
        signal
        for signal in signals
        if text[signal.start:signal.end] == signal_text
    ]

    assert len(matching) == 1
    assert matching[0].signal_type is expected_type


def test_after_that_is_one_signal(scanner):
    text = "Open GitHub after that explain Git"

    signals = scanner.scan(text)
    sequence_signals = [
        signal
        for signal in signals
        if signal.signal_type is BoundarySignalType.SEQUENCE_MARKER
    ]

    assert len(sequence_signals) == 1

    signal = sequence_signals[0]
    assert text[signal.start:signal.end] == "after that"


def test_signal_offsets_reference_original_text(scanner):
    text = "  Open GitHub, then explain Git.  "

    for signal in scanner.scan(text):
        assert text[signal.start:signal.end]
        assert signal.start < signal.end


def test_signals_are_ordered_by_position(scanner):
    text = "Open GitHub, then explain Git."

    signals = scanner.scan(text)

    assert tuple(signal.start for signal in signals) == tuple(
        sorted(signal.start for signal in signals)
    )


def test_scanner_returns_tuple(scanner):
    assert isinstance(scanner.scan("Open GitHub, then explain Git"), tuple)


def test_scanner_is_deterministic(scanner):
    text = "Open GitHub, then explain Git."

    assert scanner.scan(text) == scanner.scan(text)


def test_scanner_detects_signals_without_deciding_boundaries(scanner):
    # Both uses of "and" are detected. Deciding whether they are
    # actual request boundaries belongs to a later component.
    text = "Open GitHub and explain Git. Explain Python and C++."

    signals = scanner.scan(text)

    coordinators = [
        signal
        for signal in signals
        if signal.signal_type is BoundarySignalType.COORDINATOR
    ]

    assert len(coordinators) == 2

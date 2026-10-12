from dataclasses import FrozenInstanceError, is_dataclass

import pytest

import request_parsing
from request_parsing.models import RequestParseResult, RequestSegment


@pytest.fixture
def sample_result():
    original = "Open GitHub and explain Git"

    first = RequestSegment("Open GitHub", 0, 11)
    second = RequestSegment("explain Git", 16, 27)

    return RequestParseResult(
        original_text=original,
        segments=(first, second),
    )


def test_request_parsing_package_imports():
    assert request_parsing is not None


def test_models_are_frozen_dataclasses():
    assert is_dataclass(RequestSegment)
    assert is_dataclass(RequestParseResult)

    assert RequestSegment.__dataclass_params__.frozen
    assert RequestParseResult.__dataclass_params__.frozen


def test_segment_offsets_reference_original_text(sample_result):
    original = sample_result.original_text

    for segment in sample_result.segments:
        assert original[segment.start:segment.end] == segment.text


def test_segment_equality_uses_field_values():
    first = RequestSegment("Open GitHub", 0, 11)
    equivalent = RequestSegment("Open GitHub", 0, 11)

    assert first == equivalent


def test_request_segment_is_immutable():
    segment = RequestSegment("Open GitHub", 0, 11)

    with pytest.raises(FrozenInstanceError):
        segment.text = "Changed"


def test_request_parse_result_is_immutable(sample_result):
    with pytest.raises(FrozenInstanceError):
        sample_result.original_text = "Changed"


def test_parse_result_stores_ordered_tuple(sample_result):
    assert isinstance(sample_result.segments, tuple)
    assert len(sample_result.segments) == 2

    assert sample_result.segments[0].text == "Open GitHub"
    assert sample_result.segments[1].text == "explain Git"
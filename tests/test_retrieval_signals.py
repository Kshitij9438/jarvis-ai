from planner.retrieval_signals import (
    has_explicit_search_request,
    requires_current_information,
)


def test_latest_requires_current_information():
    assert requires_current_information(
        "explain the latest transformer architectures"
    )


def test_recent_requires_current_information():
    assert requires_current_information(
        "describe recent transformer architectures"
    )


def test_explain_does_not_require_current_information():
    assert not requires_current_information(
        "explain transformers"
    )


def test_describe_does_not_require_current_information():
    assert not requires_current_information(
        "describe transformers"
    )


def test_explicit_web_search_is_detected():
    assert has_explicit_search_request(
        "search the web for transformer applications"
    )


def test_explicit_online_search_is_detected():
    assert has_explicit_search_request(
        "search online for transformer applications"
    )


def test_explain_is_not_an_explicit_search_request():
    assert not has_explicit_search_request(
        "explain transformers"
    )


def test_describe_is_not_an_explicit_search_request():
    assert not has_explicit_search_request(
        "describe transformers"
    )
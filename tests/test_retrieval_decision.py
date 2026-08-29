from planner.retrieval_decision import (
    RetrievalDecision,
    should_use_retrieval,
)


def test_explain_and_describe_have_same_retrieval_decision():
    explain = should_use_retrieval(
        requires_current_information=False,
        explicit_search_request=False,
        context_available=False,
    )

    describe = should_use_retrieval(

        requires_current_information=False,
        explicit_search_request=False,
        context_available=False,
    )

    assert explain == describe


def test_latest_information_requires_retrieval():
    decision = should_use_retrieval(
        requires_current_information=True,
        explicit_search_request=False,
        context_available=False,
    )

    assert decision == RetrievalDecision.USE


def test_explicit_search_request_requires_retrieval():
    decision = should_use_retrieval(

        requires_current_information=False,
        explicit_search_request=True,
        context_available=False,
    )

    assert decision == RetrievalDecision.USE


def test_existing_context_can_avoid_retrieval():
    decision = should_use_retrieval(

        requires_current_information=False,
        explicit_search_request=False,
        context_available=True,
    )

    assert decision == RetrievalDecision.SKIP

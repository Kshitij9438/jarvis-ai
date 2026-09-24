from planner.request_understanding_adapter import RequestUnderstandingAdapter
from planner.decision import DecisionType, PlannerDecision


class FakeEntityExtractor:
    def extract(self, text):
        return {}


def test_request_understanding_populates_canonical_query():
    adapter = RequestUnderstandingAdapter(
        entity_extractor=FakeEntityExtractor()
    )

    results = adapter.understand(
        "Please explain artificial intelligence",
        PlannerDecision(type=DecisionType.EXECUTE),
    )

    assert len(results) == 1
    assert results[0].original_query == "Please explain artificial intelligence"
    assert results[0].canonical_query == "ai"
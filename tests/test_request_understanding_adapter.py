from unittest.mock import Mock

from planner.decision import DecisionType, PlannerDecision
from planner.request_understanding import RequestUnderstanding
from planner.request_understanding_adapter import RequestUnderstandingAdapter


def test_adapter_preserves_request_segmentation():
    entity_extractor = Mock()
    entity_extractor.extract.side_effect = [
        {"topics": ["BFS"]},
        {"websites": ["github"]},
    ]

    adapter = RequestUnderstandingAdapter(entity_extractor)

    decision = PlannerDecision(type=DecisionType.EXECUTE)

    result = adapter.understand(
        "Explain BFS and open GitHub",
        decision,
    )

    assert [item.original_query for item in result] == [
        "Explain BFS",
        "open GitHub",
    ]


def test_adapter_extracts_entities_for_each_segment():
    entity_extractor = Mock()
    entity_extractor.extract.side_effect = [
        {"topics": ["BFS"]},
        {"websites": ["github"]},
    ]

    adapter = RequestUnderstandingAdapter(entity_extractor)

    decision = PlannerDecision(type=DecisionType.EXECUTE)

    result = adapter.understand(
        "Explain BFS and open GitHub",
        decision,
    )

    assert result[0].entities == {"topics": ["BFS"]}
    assert result[1].entities == {"websites": ["github"]}

    assert entity_extractor.extract.call_count == 2


def test_adapter_preserves_decision():
    entity_extractor = Mock()
    entity_extractor.extract.return_value = {}

    adapter = RequestUnderstandingAdapter(entity_extractor)

    decision = PlannerDecision(type=DecisionType.EXECUTE)

    result = adapter.understand(
        "Calculate 2 + 2",
        decision,
    )

    assert len(result) == 1
    assert result[0].decision == decision
    assert result[0].decision.type == DecisionType.EXECUTE


def test_adapter_returns_request_understanding_models():
    entity_extractor = Mock()
    entity_extractor.extract.return_value = {
        "topics": ["graph traversal"],
    }

    adapter = RequestUnderstandingAdapter(entity_extractor)

    decision = PlannerDecision(type=DecisionType.EXECUTE)

    result = adapter.understand(
        "Explain graph traversal",
        decision,
    )

    assert len(result) == 1
    assert isinstance(result[0], RequestUnderstanding)
    assert result[0].original_query == "Explain graph traversal"
    assert result[0].entities == {
        "topics": ["graph traversal"],
    }


def test_adapter_ignores_empty_segments():
    entity_extractor = Mock()
    entity_extractor.extract.return_value = {}

    adapter = RequestUnderstandingAdapter(entity_extractor)

    decision = PlannerDecision(type=DecisionType.EXECUTE)

    result = adapter.understand(
        "Explain BFS and then",
        decision,
    )

    assert [item.original_query for item in result] == [
        "Explain BFS",
    ]

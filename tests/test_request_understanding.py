import pytest
from pydantic import ValidationError

from planner.decision import DecisionType, PlannerDecision
from planner.request_understanding import RequestUnderstanding


def test_request_understanding_requires_original_query():
    with pytest.raises(ValidationError):
        RequestUnderstanding(
            decision=PlannerDecision(type=DecisionType.EXECUTE)
        )


def test_request_understanding_requires_decision():
    with pytest.raises(ValidationError):
        RequestUnderstanding(
            original_query="Explain graph traversal"
        )


def test_request_understanding_stores_original_query():
    result = RequestUnderstanding(
        original_query="Explain graph traversal",
        decision=PlannerDecision(type=DecisionType.EXECUTE),
    )

    assert result.original_query == "Explain graph traversal"


def test_request_understanding_defaults_optional_fields():
    result = RequestUnderstanding(
        original_query="Explain graph traversal",
        decision=PlannerDecision(type=DecisionType.EXECUTE),
    )

    assert result.canonical_query is None
    assert result.intent is None
    assert result.entities == {}
    assert result.resolved_references == []
    assert result.clarification_reason is None


def test_request_understanding_accepts_canonical_query():
    result = RequestUnderstanding(
        original_query="Please explain graph traversal",
        canonical_query="graph traversal",
        decision=PlannerDecision(type=DecisionType.EXECUTE),
    )

    assert result.canonical_query == "graph traversal"


def test_request_understanding_accepts_intent():
    result = RequestUnderstanding(
        original_query="Open GitHub",
        intent="open_website",
        decision=PlannerDecision(type=DecisionType.EXECUTE),
    )

    assert result.intent == "open_website"


def test_request_understanding_accepts_entities():
    result = RequestUnderstanding(
        original_query="Open GitHub and explain BFS",
        entities={
            "websites": ["github"],
            "topics": ["BFS"],
        },
        decision=PlannerDecision(type=DecisionType.EXECUTE),
    )

    assert result.entities == {
        "websites": ["github"],
        "topics": ["BFS"],
    }


def test_request_understanding_accepts_resolved_references():
    result = RequestUnderstanding(
        original_query="Explain it",
        resolved_references=["it -> BFS"],
        decision=PlannerDecision(type=DecisionType.EXECUTE),
    )

    assert result.resolved_references == ["it -> BFS"]


def test_request_understanding_accepts_clarification_reason():
    result = RequestUnderstanding(
        original_query="Explain it",
        decision=PlannerDecision(type=DecisionType.CLARIFY),
        clarification_reason="The referenced topic is ambiguous.",
    )

    assert result.clarification_reason == (
        "The referenced topic is ambiguous."
    )


@pytest.mark.parametrize(
    "decision_type",
    [
        DecisionType.EXECUTE,
        DecisionType.CLARIFY,
        DecisionType.RESPOND,
        DecisionType.REJECT,
    ],
)
def test_request_understanding_accepts_all_planner_decisions(
    decision_type,
):
    result = RequestUnderstanding(
        original_query="test request",
        decision=PlannerDecision(type=decision_type),
    )

    assert result.decision.type == decision_type


def test_request_understanding_is_pydantic_model():
    result = RequestUnderstanding(
        original_query="Explain BFS",
        decision=PlannerDecision(type=DecisionType.EXECUTE),
    )

    dumped = result.model_dump()

    assert dumped["original_query"] == "Explain BFS"
    assert dumped["decision"]["type"] == DecisionType.EXECUTE


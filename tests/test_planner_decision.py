import pytest
from pydantic import ValidationError

from planner.decision import DecisionType, PlannerDecision


def test_execute_decision():
    decision = PlannerDecision(type=DecisionType.EXECUTE)

    assert decision.type == DecisionType.EXECUTE


def test_clarify_decision():
    decision = PlannerDecision(type=DecisionType.CLARIFY)

    assert decision.type == DecisionType.CLARIFY


def test_respond_decision():
    decision = PlannerDecision(type=DecisionType.RESPOND)

    assert decision.type == DecisionType.RESPOND


def test_reject_decision():
    decision = PlannerDecision(type=DecisionType.REJECT)

    assert decision.type == DecisionType.REJECT


def test_decision_type_is_string_compatible():
    assert DecisionType.EXECUTE == "execute"
    assert DecisionType.CLARIFY == "clarify"
    assert DecisionType.RESPOND == "respond"
    assert DecisionType.REJECT == "reject"


def test_planner_decision_requires_a_valid_decision_type():
    with pytest.raises(ValidationError):
        PlannerDecision(type="unknown")
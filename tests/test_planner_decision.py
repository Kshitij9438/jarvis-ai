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
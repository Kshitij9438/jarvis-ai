from app.runtime import JarvisRuntime
from planner.decision import DecisionType


def test_explain_something_clarifies_without_execution():
    runtime = JarvisRuntime()

    def planner_should_not_be_called(*args, **kwargs):
        raise AssertionError("Planner must not run for CLARIFY")

    runtime.planner.plan = planner_should_not_be_called

    response = runtime.run("explain something")

    assert response["decision"].type == DecisionType.CLARIFY
    assert response["plan"] is None
    assert response["results"] == []


def test_hi_returns_respond_without_execution():
    runtime = JarvisRuntime()

    def planner_should_not_be_called(*args, **kwargs):
        raise AssertionError("Planner must not run for RESPOND")

    runtime.planner.plan = planner_should_not_be_called

    response = runtime.run("hi")

    assert response["decision"].type == DecisionType.RESPOND
    assert response["plan"] is None
    assert response["results"] == []
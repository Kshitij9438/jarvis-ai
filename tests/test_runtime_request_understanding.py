from types import SimpleNamespace

from app.runtime import JarvisRuntime
from planner.decision import DecisionType


def test_execute_request_passes_through_request_understanding():
    runtime = JarvisRuntime()

    captured = {}

    original = runtime.request_understanding_adapter.understand

    def wrapped(user_input, decision):
        captured["user_input"] = user_input
        captured["decision"] = decision

        return original(user_input, decision)

    runtime.request_understanding_adapter.understand = wrapped

    runtime.planner.plan = lambda user_input, context: None

    response = runtime.run("calculate 2 + 2")

    assert captured["user_input"] == "calculate 2 + 2"
    assert captured["decision"].type == DecisionType.EXECUTE
    assert response["decision"].type == DecisionType.EXECUTE


def test_clarify_does_not_enter_request_understanding(monkeypatch):
    runtime = JarvisRuntime()

    def should_not_run(*args, **kwargs):
        raise AssertionError(
            "RequestUnderstanding must not run after CLARIFY"
        )

    runtime.request_understanding_adapter.understand = should_not_run
    runtime.planner.plan = should_not_run

    monkeypatch.setattr(
        "app.runtime.clarify_question",
        lambda *args, **kwargs: SimpleNamespace(
            question="What specific topic do you need explained?"
        ),
    )

    response = runtime.run("explain something")

    assert response["decision"].type == DecisionType.CLARIFY
    assert response["plan"] is None


def test_respond_does_not_enter_request_understanding():
    runtime = JarvisRuntime()

    def should_not_run(*args, **kwargs):
        raise AssertionError(
            "RequestUnderstanding must not run after RESPOND"
        )

    runtime.request_understanding_adapter.understand = should_not_run
    runtime.planner.plan = should_not_run

    response = runtime.run("hi")

    assert response["decision"].type == DecisionType.RESPOND
    assert response["plan"] is None


def test_request_understanding_topics_update_active_topic():
    runtime = JarvisRuntime()

    runtime.request_understanding_adapter.understand = (
        lambda user_input, decision: [
            SimpleNamespace(
                entities={
                    "topics": ["BFS"],
                }
            )
        ]
    )

    runtime.planner.plan = lambda user_input, context: None

    response = runtime.run("explain BFS")

    conversation = runtime.conversation_manager.get_or_create_conversation(
        response["conversation_id"]
    )

    assert [topic.entity for topic in conversation.active_topic] == ["BFS"]

from types import SimpleNamespace

from app.runtime import JarvisRuntime
from planner.decision import DecisionType
from conversation.context import IntentModel
from conversation.manager import ConversationManager


def test_execute_request_passes_through_request_understanding():
    runtime = JarvisRuntime()

    captured = {}

    original = runtime.request_understanding_adapter.understand

    def wrapped(user_input, decision):
        captured["user_input"] = user_input
        captured["decision"] = decision

        return original(user_input, decision)

    runtime.request_understanding_adapter.understand = wrapped

    runtime.planner.plan = lambda user_input, context, request_understanding=None: None

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

    runtime.planner.plan = lambda user_input, context, request_understanding=None: None

    response = runtime.run("explain BFS")

    conversation = runtime.conversation_manager.get_or_create_conversation(
        response["conversation_id"]
    )

    assert [topic.entity for topic in conversation.active_topic] == ["BFS"]

def test_clarification_answer_resumes_pending_request(monkeypatch):
    runtime = JarvisRuntime.__new__(JarvisRuntime)
    runtime.conversation_manager = ConversationManager()

    runtime.planner = SimpleNamespace(
        llm=SimpleNamespace(
            generate_structured=lambda **_: IntentModel(
                name="explain",
                description="Explain a concept",
            )
        )
    )

    captured = {
        "understanding_queries": [],
        "planned_queries": [],
    }

    def fake_understand(user_input, decision):
        captured["understanding_queries"].append(user_input)
        return [SimpleNamespace(entities={"topics": []})]

    def fake_plan(
        user_input,
        context,
        request_understanding=None,
    ):
        captured["planned_queries"].append(user_input)
        return None

    runtime.request_understanding_adapter = SimpleNamespace(
        understand=fake_understand,
    )
    runtime.planner.plan = fake_plan

    monkeypatch.setattr(
        "app.runtime.clarify_question",
        lambda *args, **kwargs: SimpleNamespace(
            question="What would you like me to explain?"
        ),
    )

    # Turn 1: an incomplete request must result in clarification.
    first_response = runtime.run("explain something")
    conversation_id = first_response["conversation_id"]

    conversation = runtime.conversation_manager.get_conversation(
        conversation_id
    )

    assert first_response["decision"].type == DecisionType.CLARIFY
    assert first_response["plan"] is None
    assert captured["planned_queries"] == []

    assert conversation.pending_request is not None
    assert conversation.pending_request.original_query == "explain something"

    # Turn 2: the answer must complete the existing request.
    second_response = runtime.run(
        "transformers",
        conversation_id=conversation_id,
    )

    assert second_response["decision"].type == DecisionType.EXECUTE
    assert captured["understanding_queries"] == ["explain transformers"]
    assert captured["planned_queries"] == ["explain transformers"]

    # The clarification must be consumed, not reused on another turn.
    assert conversation.pending_request is None
    assert conversation.pending_clarification is None

    # History must preserve the user's actual messages.
    assert [
        entry.user_input
        for entry in conversation.conversation_history
    ] == [
        "explain something",
        "transformers",
    ]
    # Turn 3: a new request must not inherit the previous clarification.
    captured["understanding_queries"].clear()
    captured["planned_queries"].clear()

    third_response = runtime.run(
        "calculate 5 + 6",
        conversation_id=conversation_id,
    )

    assert third_response["decision"].type == DecisionType.EXECUTE

    # The new request must remain unchanged.
    assert captured["understanding_queries"] == ["calculate 5 + 6"]
    assert captured["planned_queries"] == ["calculate 5 + 6"]

    # The consumed clarification must not reappear.
    assert conversation.pending_request is None
    assert conversation.pending_clarification is None

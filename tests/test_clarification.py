from app.runtime import JarvisRuntime
from control.clarification import ClarificationRequest, clarify_question
from planner.decision import DecisionType


def test_clarification_response_is_generated():
    runtime = JarvisRuntime()

    response = runtime.run("explain something")

    assert response["decision"].type == DecisionType.CLARIFY
    assert response["plan"] is None
    assert response["results"]

    clarification = response["results"][0]

    assert clarification.question
    assert isinstance(clarification.question, str)


def test_clarification_stores_pending_request():
    runtime = JarvisRuntime()

    response = runtime.run("explain something")

    conversation_id = response["conversation_id"]

    conversation = runtime.conversation_manager.get_conversation(
        conversation_id
    )

    assert conversation.pending_clarification is not None
    assert conversation.pending_clarification.clarification_question

    assert conversation.pending_request is not None
    assert conversation.pending_request.intent is not None
    assert conversation.pending_request.intent.name
    assert conversation.pending_request.missing_information == ["topic"]
    assert conversation.pending_request.clarification_answer is None


def test_clarification_does_not_execute_tools():
    runtime = JarvisRuntime()

    response = runtime.run("explain something")

    assert response["decision"].type == DecisionType.CLARIFY
    assert response["plan"] is None
    assert response["results"]

    # A clarification must terminate the current execution attempt.
    # Therefore no execution plan should have been produced.


def test_clarification_returns_fallback_when_structured_generation_fails():
    class FailingLLM:
        def generate_structured(self, **kwargs):
            return None

    llm = FailingLLM()

    clarification = clarify_question(
        llm,
        "explain something",
    )

    assert isinstance(clarification, ClarificationRequest)
    assert clarification.question.strip()


def test_clarification_preserves_successful_generated_question():
    expected = ClarificationRequest(
        question="Which topic would you like me to explain?"
    )

    class SuccessfulLLM:
        def generate_structured(self, **kwargs):
            return expected

    clarification = clarify_question(
        SuccessfulLLM(),
        "explain something",
    )

    assert clarification is expected
    assert clarification.question == (
        "Which topic would you like me to explain?"
    )

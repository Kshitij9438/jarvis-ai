
from conversation.manager import ConversationManager

from conversation.context import ConversationEntry
from conversation.context import (
    ConversationContext,
    IntentModel,
    PendingRequest,
)
from conversation.manager import ConversationManager

from app.runtime import JarvisRuntime

def test_conversation_persists_across_lookup():
    manager = ConversationManager()

    context = manager.create_conversation()
    conversation_id = context.conversation_id

    context.conversation_history.append(
        ConversationEntry(
            user_input="hello",
        )
    )

    retrieved = manager.get_conversation(conversation_id)

    assert retrieved is context
    assert len(retrieved.conversation_history) == 1
    assert retrieved.conversation_history[0].user_input == "hello"

from conversation.manager import ConversationManager
from conversation.context import ConversationEntry


def test_add_conversation_entry_updates_conversation_state():
    manager = ConversationManager()

    context = manager.create_conversation()
    conversation_id = context.conversation_id

    entry = ConversationEntry(
        user_input="Explain transformers",
        assistant_response="Transformers are neural network architectures...",
    )

    result = manager.add_conversation_entry(
        conversation_id,
        entry,
    )

    assert result is True

    retrieved = manager.get_conversation(conversation_id)

    assert retrieved is context
    assert len(retrieved.conversation_history) == 1
    assert retrieved.conversation_history[0] == entry
    assert retrieved.last_assistant_response == (
        "Transformers are neural network architectures..."
    )

def test_add_conversation_entry_returns_false_for_unknown_conversation():
    manager = ConversationManager()

    context = manager.create_conversation()

    entry = ConversationEntry(
        user_input="Hello",
        assistant_response="Hello!",
    )

    unknown_id = context.conversation_id

    manager.delete_conversation(unknown_id)

    result = manager.add_conversation_entry(
        unknown_id,
        entry,
    )

    assert result is False



def test_runtime_persists_conversation_across_requests():
    runtime = JarvisRuntime()

    first_response = runtime.run("hello")

    conversation_id = first_response["conversation_id"]

    assert conversation_id is not None
    assert runtime.conversation_manager.count() == 1

    second_response = runtime.run(
        "second message",
        conversation_id=conversation_id,
    )

    assert second_response["conversation_id"] == conversation_id
    assert runtime.conversation_manager.count() == 1

    conversation = runtime.conversation_manager.get_conversation(
        conversation_id
    )

    assert conversation is not None
    assert len(conversation.conversation_history) == 2

    assert (
        conversation.conversation_history[0].user_input
        == "hello"
    )

    assert (
        conversation.conversation_history[1].user_input
        == "second message"
    )



def test_pending_request_persists_and_updates():
    manager = ConversationManager()

    conversation = manager.create_conversation()
    conversation_id = conversation.conversation_id

    assert conversation.pending_request is None

    conversation.pending_request = PendingRequest(
        intent=IntentModel(
            name="explain",
            description="Explain a concept",
        ),
        missing_information=["topic"],
        clarification_answer=None,
    )

    stored = manager.get_conversation(conversation_id)

    assert stored is conversation
    assert stored.pending_request is not None
    assert stored.pending_request.intent.name == "explain"
    assert stored.pending_request.missing_information == ["topic"]
    assert stored.pending_request.clarification_answer is None

    stored.pending_request.clarification_answer = "Quantum Physics"

    retrieved = manager.get_conversation(conversation_id)

    assert retrieved is conversation
    assert retrieved.pending_request is not None
    assert retrieved.pending_request == PendingRequest(
        intent=IntentModel(
            name="explain",
            description="Explain a concept",
        ),
        missing_information=["topic"],
        clarification_answer="Quantum Physics",
    )

def test_pending_request_persists_across_conversation_lookup():
    manager = ConversationManager()

    context = manager.create_conversation()
    conversation_id = context.conversation_id

    pending_request = PendingRequest(
        intent=IntentModel(
            name="explain",
            description="Explain a concept",
        ),
        missing_information=["topic"],
    )

    context.pending_request = pending_request

    retrieved = manager.get_conversation(conversation_id)

    assert retrieved is context
    assert retrieved.pending_request is not None
    assert retrieved.pending_request.intent.name == "explain"
    assert retrieved.pending_request.missing_information == ["topic"]
    assert retrieved.pending_request.clarification_answer is None

def test_pending_request_is_isolated_between_conversations():
    manager = ConversationManager()

    conversation_a = manager.create_conversation()
    conversation_b = manager.create_conversation()

    conversation_a.pending_request = PendingRequest(
        intent=IntentModel(
            name="explain",
            description="Explain a concept",
        ),
        missing_information=["topic"],
    )

    assert conversation_a.pending_request is not None
    assert conversation_b.pending_request is None

    conversation_a.pending_request.clarification_answer = "Transformers"

    assert (
        conversation_a.pending_request.clarification_answer
        == "Transformers"
    )
    assert conversation_b.pending_request is None
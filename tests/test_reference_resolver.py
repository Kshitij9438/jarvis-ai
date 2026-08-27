from conversation.context import ActiveTopic, ConversationContext
from conversation.reference_resolver import (
    ReferenceResolutionDecision,
    ReferenceResolver,
)


def test_resolve_reference_with_no_active_topic():
    context = ConversationContext(active_topic=None)
    resolver = ReferenceResolver(context)

    resolved_entity, decision = resolver.resolve_reference("it")

    assert resolved_entity is None
    assert decision == ReferenceResolutionDecision.UNRESOLVED


def test_resolve_reference_with_multiple_active_topics():
    context = ConversationContext(
        active_topic=[
            ActiveTopic(entity="transformers"),
            ActiveTopic(entity="neural networks"),
        ]
    )
    resolver = ReferenceResolver(context)

    resolved_entity, decision = resolver.resolve_reference("it")

    assert resolved_entity is None
    assert decision == ReferenceResolutionDecision.AMBIGUOUS


def test_resolve_reference_with_single_active_topic():
    context = ConversationContext(
        active_topic=[
            ActiveTopic(entity="transformers")
        ]
    )
    resolver = ReferenceResolver(context)

    resolved_entity, decision = resolver.resolve_reference("it")

    assert resolved_entity == "transformers"
    assert decision == ReferenceResolutionDecision.RESOLVED

def test_update_context_with_resolved_reference():
    context = ConversationContext(
        active_topic=[
            ActiveTopic(entity="transformers")
        ]
    )
    resolver = ReferenceResolver(context)

    resolver.update_context_with_resolution(
        reference="it",
        resolved_entity="transformers",
        decision=ReferenceResolutionDecision.RESOLVED,
    )

    assert "it -> transformers" in context.resolved_references

from app.runtime import JarvisRuntime
from conversation.context import ActiveTopic


def test_conversation_active_topic_persists_across_turns():
    runtime = JarvisRuntime()

    first_response = runtime.run("explain transformers")

    conversation_id = first_response["conversation_id"]

    conversation = runtime.conversation_manager.get_conversation(
        conversation_id
    )

    assert conversation.active_topic == [
        ActiveTopic(entity="transformers")
    ]

    second_conversation = (
        runtime.conversation_manager.get_conversation(
            conversation_id
        )
    )

    assert second_conversation.active_topic == [
        ActiveTopic(entity="transformers")
    ]

def test_resolves_reference_against_persisted_active_topic():
    runtime = JarvisRuntime()

    first_response = runtime.run("explain transformers")
    conversation_id = first_response["conversation_id"]

    conversation = runtime.conversation_manager.get_conversation(
        conversation_id
    )

    resolver = ReferenceResolver(conversation)

    resolved_entity, decision = resolver.resolve_reference("it")

    assert resolved_entity == "transformers"
    assert decision == ReferenceResolutionDecision.RESOLVED

def test_runtime_resolves_reference_against_active_topic():
    runtime = JarvisRuntime()

    first_response = runtime.run("explain transformers")
    conversation_id = first_response["conversation_id"]

    second_response = runtime.run(
        "what are its applications?",
        conversation_id=conversation_id,
    )

    conversation = runtime.conversation_manager.get_conversation(
        conversation_id
    )

    assert second_response["conversation_id"] == conversation_id

    assert any(
        "its -> transformers" == reference
        for reference in conversation.resolved_references
    )

from app.runtime import JarvisRuntime
from planner.decision import DecisionType
from conversation.context import ActiveTopic


def test_ambiguous_reference_clarifies_without_execution():
    runtime = JarvisRuntime()

    first_response = runtime.run(
        "compare transformers and neural networks"
    )

    conversation_id = first_response["conversation_id"]

    conversation = runtime.conversation_manager.get_conversation(
        conversation_id
    )

    assert conversation.active_topic == [
        ActiveTopic(entity="transformers"),
        ActiveTopic(entity="neural networks"),
    ]

    def planner_should_not_be_called(*args, **kwargs):
        raise AssertionError(
            "Planner must not run for an ambiguous reference"
        )

    runtime.planner.plan = planner_should_not_be_called

    second_response = runtime.run(
        "what are its applications?",
        conversation_id=conversation_id,
    )

    assert second_response["decision"].type == DecisionType.CLARIFY
    assert second_response["plan"] is None
    assert len(second_response["results"]) == 1
    assert second_response["results"][0].question

def test_resolved_reference_reaches_planner():
    runtime = JarvisRuntime()

    first_response = runtime.run("explain transformers")
    conversation_id = first_response["conversation_id"]

    second_response = runtime.run(
        "what are its applications?",
        conversation_id=conversation_id,
    )

    assert second_response["decision"].type == DecisionType.EXECUTE
    assert second_response["plan"] is not None

    plan_text = str(second_response["plan"]).lower()

    assert "transformers" in plan_text
    assert "its applications" not in plan_text

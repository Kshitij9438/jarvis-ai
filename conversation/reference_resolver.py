from enum import Enum

from conversation.context import ConversationContext


class ReferenceResolutionDecision(str, Enum):
    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"


class ReferenceResolver:
    def __init__(self, context: ConversationContext):
        self.context = context

    def resolve_reference(
        self,
        reference: str,
    ) -> tuple[str | None, ReferenceResolutionDecision]:
        """
        Resolve a reference using the current conversation context.

        Returns the resolved entity together with the resolution decision.
        Resolution is deterministic and does not use an LLM.
        """
        active_topics = self.context.active_topic

        if not active_topics:
            return None, ReferenceResolutionDecision.UNRESOLVED

        if len(active_topics) > 1:
            return None, ReferenceResolutionDecision.AMBIGUOUS

        return (
            active_topics[0].entity,
            ReferenceResolutionDecision.RESOLVED,
        )

    def update_context_with_resolution(
        self,
        reference: str,
        resolved_entity: str | None,
        decision: ReferenceResolutionDecision,
    ) -> None:
        """
        Record a successfully resolved reference in conversation state.
        """
        if (
            decision == ReferenceResolutionDecision.RESOLVED
            and resolved_entity is not None
        ):
            self.context.resolved_references.append(
                f"{reference} -> {resolved_entity}"
            )
from uuid import UUID

from conversation.context import ConversationContext, ConversationEntry


class ConversationManager:
    """
    Owns the lifecycle and mutation of conversation contexts.

    ConversationManager manages which conversations exist and exposes
    operations for updating their state.

    ConversationContext owns the state of an individual conversation.
    """

    def __init__(self):
        self.conversations: dict[UUID, ConversationContext] = {}

    # =========================
    # CONVERSATION LIFECYCLE
    # =========================

    def create_conversation(
        self,
        conversation_id: UUID | None = None,
    ) -> ConversationContext:
        """
        Create and store a new conversation.
        """
        if conversation_id is None:
            context = ConversationContext()
        else:
            context = ConversationContext(
                conversation_id=conversation_id,
            )

        self.conversations[context.conversation_id] = context

        return context

    def get_conversation(
        self,
        conversation_id: UUID,
    ) -> ConversationContext | None:
        """
        Retrieve an existing conversation.

        Returns None when the conversation does not exist.
        """
        return self.conversations.get(conversation_id)

    def get_or_create_conversation(
        self,
        conversation_id: UUID | None = None,
    ) -> ConversationContext:
        """
        Retrieve an existing conversation or create a new one.
        """
        if conversation_id is not None:
            context = self.get_conversation(conversation_id)

            if context is not None:
                return context

        return self.create_conversation(conversation_id)

    def delete_conversation(self, conversation_id: UUID) -> bool:
        """
        Delete a conversation.

        Returns True if the conversation existed and was deleted.
        """
        if conversation_id not in self.conversations:
            return False

        del self.conversations[conversation_id]
        return True

    # =========================
    # CONVERSATION STATE
    # =========================

    def add_conversation_entry(
        self,
        conversation_id: UUID,
        entry: ConversationEntry,
    ) -> bool:
        """
        Add a completed conversation entry to an existing conversation.

        Returns False if the conversation does not exist.
        """
        context = self.get_conversation(conversation_id)

        if context is None:
            return False

        context.conversation_history.append(entry)
        context.last_assistant_response = entry.assistant_response

        return True

    # =========================
    # INSPECTION
    # =========================

    def conversation_exists(self, conversation_id: UUID) -> bool:
        """Check whether a conversation exists."""
        return conversation_id in self.conversations

    def count(self) -> int:
        """Return the number of managed conversations."""
        return len(self.conversations)

    # =========================
    # RESET
    # =========================

    def clear(self) -> None:
        """Remove all managed conversations."""
        self.conversations.clear()
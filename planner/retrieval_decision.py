from enum import Enum


class RetrievalDecision(str, Enum):
    USE = "use"
    SKIP = "skip"


def should_use_retrieval(
    requires_current_information: bool,
    explicit_search_request: bool,
    context_available: bool,
) -> RetrievalDecision:
    """
    Determine whether external retrieval should be used.

    Retrieval is required when:
    - current information is explicitly required, or
    - the user explicitly requests online/web search.

    Retrieval can be skipped when:
    - suitable context is already available, or
    - neither retrieval trigger is present.

    Lexical intent words such as "explain" or "describe" do not
    independently determine retrieval.
    """
    if requires_current_information:
        return RetrievalDecision.USE

    if explicit_search_request:
        return RetrievalDecision.USE

    if context_available:
        return RetrievalDecision.SKIP

    return RetrievalDecision.SKIP
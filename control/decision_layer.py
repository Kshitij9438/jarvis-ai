import re

from planner.decision import DecisionType, PlannerDecision


# =========================
# DETERMINISTIC DECISION RULES
# =========================

_GREETING_INPUTS = {
    "hi",
    "hello",
    "hey",
    "yo",
    "sup",
    "good morning",
    "good afternoon",
    "good evening",
}

_CLARIFICATION_PATTERNS = (
    r"^\s*explain\s+(something|anything|it)\s*$",
    r"^\s*explain\s*$",
    r"^\s*describe\s+(something|anything|it)\s*$",
    r"^\s*tell\s+me\s+about\s+(something|anything|it)\s*$",
)


def _is_greeting(user_input: str) -> bool:
    """Return True when the input is a simple conversational greeting."""
    return user_input.lower().strip() in _GREETING_INPUTS


def _requires_clarification(user_input: str) -> bool:
    """
    Return True when the request clearly expresses an intent
    but does not provide the information required to execute it.

    M4 intentionally handles only the first clarification class.
    General request understanding belongs to later milestones.
    """
    normalized = user_input.lower().strip()

    return any(
        re.fullmatch(pattern, normalized)
        for pattern in _CLARIFICATION_PATTERNS
    )


def decision_type_from_user_input(
    user_input: str,
) -> PlannerDecision:
    """
    Determine the execution boundary for a user request.

    M4 uses deterministic logic only.

    The decision layer answers one question:

        Should this request proceed to planning?

    It does not perform:
        - intent resolution
        - reference resolution
        - capability selection
        - tool selection
        - planning
        - execution

    Those responsibilities belong to later stages of the architecture.
    """
    normalized = user_input.strip()

    if not normalized:
        return PlannerDecision(
            type=DecisionType.REJECT,
        )

    if _is_greeting(normalized):
        return PlannerDecision(
            type=DecisionType.RESPOND,
        )

    if _requires_clarification(normalized):
        return PlannerDecision(
            type=DecisionType.CLARIFY,
        )

    return PlannerDecision(
        type=DecisionType.EXECUTE,
    )
from __future__ import annotations

from enum import Enum


class Capability(str, Enum):
    NAVIGATION = "navigation"
    CALCULATION = "calculation"
    DOCUMENT = "document"
    KNOWLEDGE = "knowledge"


class CapabilitySelector:
    """
    M7.4 capability boundary.

    Determines the high-level capability required by a request.

    This component does NOT select concrete tools.
    Concrete tool selection remains owned by ToolSelector.

    M7.4 intentionally uses the existing deterministic intent
    signatures as the first implementation so the migration
    changes ownership without changing behavior.
    """

    NAVIGATION_TERMS = (
        "open",
        "visit",
        "go to",
        "launch",
    )

    CALCULATION_TERMS = (
        "+",
        "-",
        "*",
        "/",
        "calculate",
        "compute",
        "evaluate",
        "sqrt",
        "square",
        "cube",
        "power",
        "percent",
        "%",
    )

    DOCUMENT_TERMS = (
        "file",
        "pdf",
        "document",
        "summarize",
    )

    KNOWLEDGE_TERMS = (
        "explain",
        "what is",
        "who is",
        "how",
        "guide",
        "learn",
        "teach",
    )

    def select(self, query: str) -> Capability | None:
        """
        Determine the high-level capability required by a query.

        Returns None when no deterministic capability can be
        identified.
        """
        q = query.lower()

        if any(term in q for term in self.NAVIGATION_TERMS):
            return Capability.NAVIGATION

        if any(term in q for term in self.CALCULATION_TERMS):
            return Capability.CALCULATION

        if any(term in q for term in self.DOCUMENT_TERMS):
            return Capability.DOCUMENT

        if any(term in q for term in self.KNOWLEDGE_TERMS):
            return Capability.KNOWLEDGE

        return None

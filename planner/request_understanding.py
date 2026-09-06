from typing import Any

from pydantic import BaseModel, Field

from planner.decision import PlannerDecision


class RequestUnderstanding(BaseModel):
    """
    Structured result produced by the Request Understanding phase.

    M7.1 defines the contract only. It does not perform parsing,
    intent resolution, reference resolution, or planning itself.

    The purpose of this model is to provide a stable boundary between
    request understanding and the existing planner.
    """

    original_query: str = Field(
        ...,
        min_length=1,
        description="The original user request before interpretation.",
    )

    canonical_query: str | None = Field(
        None,
        description=(
            "The normalized query representation used downstream. "
            "M7.1 does not define the normalization algorithm yet."
        ),
    )

    intent: str | None = Field(
        None,
        description="Resolved intent name when available.",
    )

    entities: dict[str, Any] = Field(
        default_factory=dict,
        description="Entities extracted from the request.",
    )

    resolved_references: list[str] = Field(
        default_factory=list,
        description="References resolved during request understanding.",
    )

    decision: PlannerDecision = Field(
        ...,
        description=(
            "Terminal decision produced by request understanding "
            "before planning may begin."
        ),
    )

    clarification_reason: str | None = Field(
        None,
        description="Reason clarification is required, when applicable.",
    )

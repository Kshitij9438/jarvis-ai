from pydantic import BaseModel, Field

from brain.llm import LLM


class ClarificationRequest(BaseModel):
    """
    Structured clarification question generated for an incomplete request.
    """

    question: str = Field(
        ...,
        description="The question for which clarification is requested.",
    )


def clarify_question(
    llm: LLM,
    user_query: str,
) -> ClarificationRequest:
    """
    Generate a concise clarification question for an incomplete request.

    The function only generates the clarification.
    It does not modify conversation state or decide whether clarification
    is required.
    """
    return llm.generate_structured(
        prompt=user_query,
        schema=ClarificationRequest,
        system_prompt=(
            "You are an assistant that receives a user query which is "
            "missing some information. Generate a clear and concise "
            "question asking the user for the missing information. "
            "Do not provide an answer or additional context. "
            "Return only a relevant clarification question in English."
        ),
    )
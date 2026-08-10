from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    message: str
    plan: Any | None = None
    results: list[dict] = Field(default_factory=list)
    context: dict[str, Any] | None = None
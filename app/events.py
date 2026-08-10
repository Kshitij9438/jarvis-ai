from typing import Any
from pydantic import BaseModel, Field

class JarvisEvent(BaseModel):
    type: str
    data: dict[str,Any] = Field(default_factory=dict)
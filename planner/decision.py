from enum import Enum

from pydantic import BaseModel


class DecisionType(str, Enum):
    EXECUTE = "execute"
    CLARIFY = "clarify"
    RESPOND = "respond"
    REJECT = "reject"


class PlannerDecision(BaseModel):
    type: DecisionType
from pydantic import BaseModel
from typing import List, Dict

class Action(BaseModel):
    action: str
    args: Dict

class Plan(BaseModel):
    steps: List[Action]
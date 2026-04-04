from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    type: str
    target: Optional[str] = None
    file_path: Optional[str] = None
    query: Optional[str] = None
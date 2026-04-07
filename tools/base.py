from pydantic import BaseModel
from typing import Type, List


class BaseTool:
    name: str
    description: str
    args_schema: Type[BaseModel]

    # 🧠 NEW — tool self-description (core of new architecture)
    intents: List[str] = []       # e.g. ["open", "visit", "launch"]
    entities: List[str] = []      # e.g. ["url", "website", "file_path"]

    # 🔗 NEW — dependencies
    requires: List[str] = []      # e.g. ["load_document"]

    # ⚡ NEW — execution priority (lower = earlier)
    priority: int = 5

    def run(self, **kwargs):
        raise NotImplementedError
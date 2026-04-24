from pydantic import BaseModel
from typing import Type, List


class BaseTool:
    """
    Base class for all tools in the system.

    Defines:
    - identity (name, description)
    - argument schema
    - matching signals (intents, entities)
    - execution behavior

    NEW ARCHITECTURE:
    - requires_context → what data this tool NEEDS
    - produces_context → what data this tool GENERATES
    """

    # =========================
    # 🧩 CORE IDENTITY
    # =========================
    name: str
    description: str
    args_schema: Type[BaseModel]

    # =========================
    # 🧠 MATCHING SIGNALS
    # =========================
    intents: List[str] = []
    entities: List[str] = []

    # =========================
    # 🔗 LEGACY DEPENDENCIES (KEEP FOR NOW)
    # =========================
    requires: List[str] = []   # 🔁 old system (do not remove yet)

    # =========================
    # ⚡ EXECUTION PRIORITY
    # =========================
    priority: int = 5

    # =========================
    # 🧠 CONTEXT CONTRACTS (NEW — CRITICAL)
    # =========================

    # What context this tool NEEDS
    # Example: ["web"], ["document"]
    requires_context: List[str] = []

    # What context this tool PRODUCES
    # Example: ["web"], ["document"]
    produces_context: List[str] = []

    # =========================
    # 🚀 EXECUTION
    # =========================
    def run(self, **kwargs):
        raise NotImplementedError("Tool must implement run()")
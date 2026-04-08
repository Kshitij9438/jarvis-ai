# tools/explain_tool.py

from tools.base import BaseTool
from brain.llm import LLM
from pydantic import BaseModel


# ✅ REQUIRED for executor
class ExplainArgs(BaseModel):
    query: str


class ExplainTool(BaseTool):
    name = "explain"
    description = "Explain concepts, teach topics, and answer conceptual questions using LLM"

    # 🧠 CRITICAL — matching signals
    intents = [
        "explain",
        "teach",
        "learn",
        "understand",
        "what is",
        "how does",
        "guide",
        "help me understand"
        "walk me through",
        "break down",
        "guide me through",
        "give me an overview",
        "help me understand"
    ]

    entities = [
        "topic",
        "concept",
        "idea",
        "query",
        "subject"
    ]

    # ⚡ moderate priority (after open/load)
    priority = 3

    args_schema = ExplainArgs  # 🔥 REQUIRED

    def __init__(self):
        self.llm = LLM()

    def run(self, query: str):
        prompt = f"Explain clearly and concisely: {query}"
        return self.llm.generate_text(prompt)
# tools/explain_tool.py

from tools.base import BaseTool
from brain.llm import LLM
from pydantic import BaseModel


# =========================
# 📦 ARG SCHEMA (UPDATED)
# =========================
class ExplainArgs(BaseModel):
    query: str
    context: str | None = None  # 🔥 NEW


class ExplainTool(BaseTool):
    name = "explain"
    description = "Explain concepts using LLM, optionally grounded with retrieved context"

    intents = [
        "explain",
        "teach",
        "learn",
        "understand",
        "what is",
        "how does",
        "guide",
        "help me understand",
        "walk me through",
        "break down",
        "guide me through",
        "give me an overview"
    ]

    entities = [
        "topic",
        "concept",
        "idea",
        "query",
        "subject"
    ]

    priority = 1
    args_schema = ExplainArgs

    def __init__(self):
        self.llm = LLM()

    # =========================
    # 🚀 RUN (CONTEXT-AWARE)
    # =========================
    def run(self, query: str, context: str = None):

        # 🔥 CASE 1: WITH CONTEXT (RAG MODE)
        if context:
            prompt = f"""
Use the following context to explain the concept.

Question: {query}

Context:
{context}

Give a clear, accurate, and concise explanation.
"""
        else:
            # 🔁 FALLBACK
            prompt = f"""
Explain clearly and concisely:

{query}
"""

        return self.llm.generate_text(prompt)
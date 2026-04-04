# tools/explain_tool.py

from tools.base import BaseTool
from brain.llm import LLM
from pydantic import BaseModel


# ✅ REQUIRED for executor
class ExplainArgs(BaseModel):
    query: str


class ExplainTool(BaseTool):
    name = "explain"
    description = "Explain general concepts using LLM"
    args_schema = ExplainArgs  # 🔥 REQUIRED

    def __init__(self):
        self.llm = LLM()

    def run(self, query: str):
        prompt = f"Explain clearly and concisely: {query}"
        return self.llm.generate_text(prompt)
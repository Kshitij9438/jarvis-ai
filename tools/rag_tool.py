from tools.base import BaseTool
from pydantic import BaseModel


class RAGArgs(BaseModel):
    query: str


class RAGTool(BaseTool):
    name = "rag_search"
    description = "Search and answer questions from internal documents"
    args_schema = RAGArgs

    def __init__(self, rag):
        self.rag = rag

    def run(self, **kwargs):
        query = kwargs["query"]
        return self.rag.answer(query)
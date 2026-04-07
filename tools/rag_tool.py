from tools.base import BaseTool
from pydantic import BaseModel


class RAGArgs(BaseModel):
    query: str


class RAGTool(BaseTool):
    name = "rag_search"
    description = "Search, summarize, and answer questions from loaded documents"

    # 🧠 matching signals
    intents = [
        "summarize",
        "summary",
        "brief",
        "analyze",
        "search",
        "find in document",
        "what does document say"
    ]

    entities = [
        "document",
        "file",
        "pdf",
        "text",
        "content"
    ]

    # 🔗 dependency
    requires = ["load_document"]

    # ⚡ execution priority
    priority = 2

    args_schema = RAGArgs

    def __init__(self, rag):
        self.rag = rag

    def run(self, **kwargs):
        query = kwargs.get("query", "")

        # =========================
        # 🚨 SAFETY CHECK (CRITICAL)
        # =========================
        if not hasattr(self.rag, "has_documents") or not self.rag.has_documents():
            return "⚠️ No document loaded. Please load a file before querying."

        # =========================
        # 🧠 DEFAULT QUERY FIX
        # =========================
        if not query or len(query.strip()) < 3:
            query = "summarize the document"

        try:
            result = self.rag.answer(query)

            # =========================
            # 🚨 EMPTY RESULT GUARD
            # =========================
            if not result or len(result.strip()) < 5:
                return "⚠️ Could not find relevant information in the document."

            return result

        except Exception as e:
            return f"⚠️ RAG error: {str(e)}"
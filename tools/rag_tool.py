from tools.base import BaseTool
from pydantic import BaseModel
import re


class RAGArgs(BaseModel):
    query: str


class RAGTool(BaseTool):
    name = "rag_search"
    description = "Search, summarize, and answer questions from loaded documents"

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

    requires = ["load_document"]
    priority = 2

    args_schema = RAGArgs

    def __init__(self, rag):
        self.rag = rag

    def run(self, **kwargs):
        query = kwargs.get("query", "")

        # =========================
        # 🚨 SAFETY: document check
        # =========================
        if not hasattr(self.rag, "has_documents") or not self.rag.has_documents():
            return "⚠️ No document loaded. Please load a file before querying."

        # =========================
        # 🧠 CLEAN QUERY (CRITICAL FIX)
        # =========================
        if query:
            # remove file paths
            query = re.sub(r"[A-Za-z]:\\\\[^\s]+", "", query)

            # remove quotes
            query = query.replace('"', "").replace("'", "")

            query = query.strip()

        # =========================
        # 🧠 DEFAULT QUERY
        # =========================
        if not query or len(query) < 3:
            query = "summarize the document"

        # normalize summarize intent
        if "summarize" in query.lower():
            query = "summarize the document"

        try:
            result = self.rag.answer(query)

            # =========================
            # 🚨 BLOCK STRUCTURED / JSON LEAKS
            # =========================
            if isinstance(result, dict):
                return "⚠️ Invalid RAG output. Try again."

            if isinstance(result, str):
                stripped = result.strip()

                # block JSON-like output
                if stripped.startswith("{") or stripped.startswith("["):
                    return "⚠️ Invalid structured output from RAG."

                if len(stripped) < 5:
                    return "⚠️ Could not find relevant information in the document."

            return result

        except Exception as e:
            return f"⚠️ RAG error: {str(e)}"
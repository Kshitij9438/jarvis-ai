from tools.base import BaseTool
from pydantic import BaseModel


class LoadDocArgs(BaseModel):
    file_path: str


class LoadDocTool(BaseTool):
    name = "load_document"
    description = "Load a file (pdf, txt, md) into memory for later querying"

    # 🧠 matching signals
    intents = [
        "load",
        "read",
        "open file",
        "import",
        "upload",
        "process file"
    ]

    entities = [
        "file",
        "document",
        "pdf",
        "txt",
        "md",
        "path"
    ]

    # ⚡ should run BEFORE rag_search
    priority = 1

    args_schema = LoadDocArgs

    def __init__(self, rag):
        self.rag = rag  # ✅ shared system

    def run(self, **kwargs):
        file_path = kwargs["file_path"]

        # 🔥 delegate to RAG system
        return self.rag.load_file(file_path)
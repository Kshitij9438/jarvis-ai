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

    priority = 1
    args_schema = LoadDocArgs

    # =========================
    # 🧠 CONTEXT CONTRACT
    # =========================
    requires_context = []
    produces_context = ["document"]

    def __init__(self, rag):
        self.rag = rag

    def run(self, **kwargs):
        file_path = kwargs["file_path"]
        return self.rag.load_file(file_path)
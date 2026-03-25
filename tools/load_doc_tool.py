from tools.base import BaseTool
from pydantic import BaseModel


class LoadDocArgs(BaseModel):
    file_path: str


class LoadDocTool(BaseTool):
    name = "load_document"
    description = "Load a file (pdf, txt, md) into memory"
    args_schema = LoadDocArgs

    def __init__(self, ingestor):
        self.ingestor = ingestor

    def run(self, **kwargs):
        return self.ingestor.load_file(kwargs["file_path"])
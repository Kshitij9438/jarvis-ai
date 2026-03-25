from tools.base import BaseTool
from pydantic import BaseModel
import webbrowser


class OpenWebsiteArgs(BaseModel):
    url: str


class OpenWebsiteTool(BaseTool):
    name = "open_website"
    description = "Open a website in browser"
    args_schema = OpenWebsiteArgs

    def run(self, **kwargs):
        webbrowser.open(kwargs["url"])
        return f"Opened {kwargs['url']}"


class EchoArgs(BaseModel):
    text: str


class EchoTool(BaseTool):
    name = "echo"
    description = "Echo text"
    args_schema = EchoArgs

    def run(self, **kwargs):
        return kwargs["text"]
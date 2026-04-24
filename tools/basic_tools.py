from tools.base import BaseTool
from pydantic import BaseModel
import webbrowser


# =========================
# 🌐 OPEN WEBSITE TOOL
# =========================
class OpenWebsiteArgs(BaseModel):
    url: str


class OpenWebsiteTool(BaseTool):
    name = "open_website"
    description = "Open a website in browser"

    # 🧠 NEW — self-describing metadata
    intents = ["open", "visit", "go to", "launch", "browse"]
    entities = ["url", "website", "site", "link"]

    # ⚡ execution priority (run early)
    priority = 1

    args_schema = OpenWebsiteArgs
    requires_context = []
    produces_context = ["web"]

    def run(self, **kwargs):
        webbrowser.open(kwargs["url"])
        return f"Opened {kwargs['url']}"


# =========================
# 🔁 ECHO TOOL (fallback)
# =========================
class EchoArgs(BaseModel):
    text: str


class EchoTool(BaseTool):
    name = "echo"
    description = "Echo text"

    # 🧠 minimal metadata (fallback tool)
    intents = []
    entities = ["text"]

    # ⚡ lowest priority
    priority = 10

    args_schema = EchoArgs
    requires_context = []
    produces_context = []

    def run(self, **kwargs):
        return kwargs["text"]
"""
tests/test_tool_selector.py

Regression tests for planner.tool_selector.ToolSelector.

These tests intentionally exercise the REAL tool selector against a
minimal registry instead of mocking internal methods. They protect the
selection contract while allowing the scoring implementation to evolve.
"""

from planner.tool_selector import ToolSelector

from tools.basic_tools import (
    OpenWebsiteTool,
    EchoTool,
)

from tools.calculator_tool import CalculatorTool
from tools.explain_tool import ExplainTool
from tools.load_doc_tool import LoadDocTool


# ==========================================================
# Fake semantic matcher
# ==========================================================

class FakeSemantic:
    """
    Disable semantic matching so tests remain deterministic.
    """

    def similarity(self, query, tool):
        return 0.0


# ==========================================================
# Fake registry
# ==========================================================

class FakeRegistry:
    def __init__(self):
        self.semantic = FakeSemantic()

        self.tools = {}

        for tool in [
            OpenWebsiteTool(),
            ExplainTool(),
            CalculatorTool(),
            LoadDocTool(None),
            EchoTool(),
        ]:
            self.tools[tool.name] = tool

    def get(self, name):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.values())


# ==========================================================
# Tests
# ==========================================================

def make_selector():
    return ToolSelector(FakeRegistry())


def test_select_open_website():
    selector = make_selector()

    tools = selector.select("open github")

    assert len(tools) == 1
    assert tools[0].name == "open_website"


def test_select_explain():
    selector = make_selector()

    tools = selector.select("explain transformers")

    assert any(t.name == "explain" for t in tools)


def test_select_calculator():
    selector = make_selector()

    tools = selector.select("calculate 2 + 2")

    assert any(t.name == "calculator" for t in tools)


def test_select_load_document():
    selector = make_selector()

    tools = selector.select("summarize report.pdf")

    assert any(t.name == "load_document" for t in tools)


def test_unknown_query_falls_back():
    """
    Unknown queries should still return at least one tool
    through the safe fallback mechanism.
    """
    selector = make_selector()

    tools = selector.select("asdfghjkl")

    assert len(tools) >= 1


def test_navigation_and_information():
    selector = make_selector()

    tools = selector.select("open github and explain git")

    names = {t.name for t in tools}

    assert "open_website" in names or "explain" in names


def test_empty_query():
    selector = make_selector()

    tools = selector.select("")

    assert isinstance(tools, list)


def test_no_duplicate_tools():
    selector = make_selector()

    tools = selector.select("open github")

    names = [t.name for t in tools]

    assert len(names) == len(set(names))


def test_hard_filter_blocks_invalid_open():
    selector = make_selector()

    tools = selector.select("open website")

    names = [t.name for t in tools]

    assert "open_website" not in names


def test_hard_filter_requires_digits_for_calculator():
    selector = make_selector()

    tools = selector.select("calculate")

    names = [t.name for t in tools]

    assert "calculator" not in names
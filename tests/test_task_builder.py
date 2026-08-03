"""
tests/test_task_builder.py

Regression tests for planner.task_builder.TaskBuilder.
"""

from unittest.mock import Mock, patch

from planner.task_builder import TaskBuilder
from planner.task import Task

from tools.calculator_tool import CalculatorTool
from tools.explain_tool import ExplainTool
from tools.load_doc_tool import LoadDocTool
from tools.rag_tool import RAGTool
from tools.web_retriever_tool import WebRetrieverTool
from tools.basic_tools import OpenWebsiteTool


# ==========================================================
# Helper
# ==========================================================

def make_builder(extracted=None):
    extractor = Mock()

    if extracted is None:
        extracted = {}

    extractor.extract.return_value = extracted

    return TaskBuilder(extractor)


# ==========================================================
# Calculator
# ==========================================================

def test_build_calculator_task():
    builder = make_builder()

    tool = CalculatorTool()

    tasks = builder.build_tasks(
        "calculate 5 + 6",
        [tool],
        {}
    )

    assert tasks == [
        Task(
            type="calculator",
            target=None,
            file_path=None,
            query="5+6"
        )
    ]


def test_invalid_calculator_skipped():
    builder = make_builder()

    tool = CalculatorTool()

    tasks = builder.build_tasks(
        "calculate apples",
        [tool],
        {}
    )

    assert tasks == []


# ==========================================================
# Explain
# ==========================================================

def test_explain_prefers_entity_topic():
    builder = make_builder(
        extracted={"query": "wrong"}
    )

    tool = ExplainTool()

    tasks = builder.build_tasks(
        "explain transformers",
        [tool],
        {
            "topics": ["transformers"]
        }
    )

    assert tasks[0].query == "transformers"


def test_explain_uses_arg_extractor_when_no_entity():
    builder = make_builder(
        extracted={"query": "attention"}
    )

    tool = ExplainTool()

    tasks = builder.build_tasks(
        "attention",
        [tool],
        {}
    )

    assert tasks[0].query == "attention"


# ==========================================================
# Web Retriever
# ==========================================================

def test_web_retriever_uses_clean_query():
    builder = make_builder()

    tool = WebRetrieverTool()

    tasks = builder.build_tasks(
        "what is reinforcement learning",
        [tool],
        {}
    )

    assert tasks[0].query == "reinforcement learning"


# ==========================================================
# Website
# ==========================================================

def test_open_website_task():
    builder = make_builder()

    tool = OpenWebsiteTool()

    tasks = builder.build_tasks(
        "open github",
        [tool],
        {
            "websites": ["github"]
        }
    )

    assert tasks == [
        Task(
            type="open_website",
            target="github",
            file_path=None,
            query="open github"
        )
    ]


def test_open_website_without_entity_skipped():
    builder = make_builder()

    tool = OpenWebsiteTool()

    tasks = builder.build_tasks(
        "open website",
        [tool],
        {}
    )

    assert tasks == []


# ==========================================================
# Load Document
# ==========================================================

@patch("planner.task_builder.os.path.exists")
def test_load_document(mock_exists):
    mock_exists.return_value = True

    builder = make_builder()

    tool = LoadDocTool(None)

    tasks = builder.build_tasks(
        "summarize report.pdf",
        [tool],
        {
            "file_path": "report.pdf"
        }
    )

    assert len(tasks) == 1
    assert tasks[0].file_path == "report.pdf"


@patch("planner.task_builder.os.path.exists")
def test_invalid_document_skipped(mock_exists):
    mock_exists.return_value = False

    builder = make_builder()

    tool = LoadDocTool(None)

    tasks = builder.build_tasks(
        "summarize report.pdf",
        [tool],
        {
            "file_path": "report.pdf"
        }
    )

    assert tasks == []


# ==========================================================
# RAG
# ==========================================================

@patch("planner.task_builder.os.path.exists")
def test_rag_summary(mock_exists):
    mock_exists.return_value = True

    builder = make_builder()

    tool = RAGTool()

    tasks = builder.build_tasks(
        "summarize report.pdf",
        [tool],
        {
            "file_path": "report.pdf"
        }
    )

    assert tasks[0].query == "summarize the document"


@patch("planner.task_builder.os.path.exists")
def test_rag_without_document_skipped(mock_exists):
    mock_exists.return_value = False

    builder = make_builder()

    tool = RAGTool()

    tasks = builder.build_tasks(
        "summarize report",
        [tool],
        {}
    )

    assert tasks == []


# ==========================================================
# Deduplication
# ==========================================================

def test_duplicate_tasks_removed():
    builder = make_builder(
        extracted={"query": "git"}
    )

    tool = ExplainTool()

    tasks = builder.build_tasks(
        "explain git",
        [tool, tool],
        {
            "topics": ["git"]
        }
    )

    assert len(tasks) == 1
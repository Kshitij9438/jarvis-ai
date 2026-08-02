from execution.context import ExecutionContext
from execution.context_signals import (
    has_retrieved_content,
    is_document_loaded,
)

def test_open_website_does_not_count_as_retrieval():
    """
    Regression test:

    Simply storing something inside the web bucket must NOT
    convince the resolver that retrieval has happened.
    """

    ctx = ExecutionContext("test")

    # Simulate open_website()
    ctx.store("web", "Opened https://github.com")

    assert has_retrieved_content(ctx) is False

def test_web_retriever_counts_as_retrieval():
    """
    A successful web_retriever execution should satisfy
    web context availability.
    """

    ctx = ExecutionContext("test")

    ctx.update(
        "web_retriever",
        {"query": "transformers"},
        "Transformers are neural networks...",
    )

    assert has_retrieved_content(ctx) is True

def test_failed_web_retrieval_is_not_available():
    """
    Failed retrieval should not satisfy the dependency.
    """

    ctx = ExecutionContext("test")

    ctx.update(
        "web_retriever",
        {"query": "transformers"},
        "❌ Retrieval failed",
    )

    assert has_retrieved_content(ctx) is False

def test_document_bucket_counts_as_loaded():
    ctx = ExecutionContext("test")

    ctx.store("document", "This is a PDF")

    assert is_document_loaded(ctx) is True

def test_load_document_history_counts_as_loaded():
    ctx = ExecutionContext("test")

    ctx.update(
        "load_document",
        {"file_path": "paper.pdf"},
        "Successfully loaded paper.pdf",
    )

    assert is_document_loaded(ctx) is True

def test_failed_document_load_is_not_loaded():
    ctx = ExecutionContext("test")

    ctx.update(
        "load_document",
        {"file_path": "paper.pdf"},
        "❌ File not found",
    )

    assert is_document_loaded(ctx) is False
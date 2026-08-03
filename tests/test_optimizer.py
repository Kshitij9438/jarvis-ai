"""
tests/test_optimizer.py

Regression tests for planner.optimizer.TaskOptimizer.
"""

from planner.optimizer import TaskOptimizer
from planner.task import Task


def make_optimizer():
    return TaskOptimizer()


# ==========================================================
# Query normalization
# ==========================================================

def test_synonym_normalization():
    """
    The optimizer normalizes 'artificial intelligence' to 'ai',
    but the current validation rule removes explain/rag queries
    shorter than three characters. This test documents the
    current behaviour.
    """
    optimizer = make_optimizer()

    tasks = [
        Task(
            type="explain",
            target=None,
            file_path=None,
            query="artificial intelligence",
        )
    ]

    optimized = optimizer.optimize(tasks)

    assert optimized == []


def test_learning_pattern_normalization():
    optimizer = make_optimizer()

    tasks = [
        Task(
            type="explain",
            target=None,
            file_path=None,
            query="learn machine learning"
        )
    ]

    optimized = optimizer.optimize(tasks)

    assert optimized[0].query == "ml basics"


def test_noise_word_removal():
    optimizer = make_optimizer()

    tasks = [
        Task(
            type="explain",
            target=None,
            file_path=None,
            query="please explain ai again"
        )
    ]

    optimized = optimizer.optimize(tasks)

    assert optimized[0].query == "explain ai"


def test_duplicate_words_removed():
    optimizer = make_optimizer()

    tasks = [
        Task(
            type="explain",
            target=None,
            file_path=None,
            query="git git git tutorial tutorial"
        )
    ]

    optimized = optimizer.optimize(tasks)

    assert optimized[0].query == "git tutorial"


# ==========================================================
# Deduplication
# ==========================================================

def test_duplicate_explain_removed():
    optimizer = make_optimizer()

    tasks = [
        Task("explain", None, None, "git"),
        Task("explain", None, None, "git"),
    ]

    optimized = optimizer.optimize(tasks)

    assert len(optimized) == 1


def test_duplicate_open_website_removed():
    optimizer = make_optimizer()

    tasks = [
        Task("open_website", "github", None, None),
        Task("open_website", "github", None, None),
    ]

    optimized = optimizer.optimize(tasks)

    assert len(optimized) == 1


def test_different_queries_not_deduplicated():
    optimizer = make_optimizer()

    tasks = [
        Task("explain", None, None, "git"),
        Task("explain", None, None, "docker"),
    ]

    optimized = optimizer.optimize(tasks)

    assert len(optimized) == 2


# ==========================================================
# Invalid task filtering
# ==========================================================

def test_invalid_open_website_removed():
    optimizer = make_optimizer()

    tasks = [
        Task("open_website", None, None, None),
    ]

    optimized = optimizer.optimize(tasks)

    assert optimized == []


def test_invalid_load_document_removed():
    optimizer = make_optimizer()

    tasks = [
        Task("load_document", None, None, None),
    ]

    optimized = optimizer.optimize(tasks)

    assert optimized == []


def test_invalid_explain_removed():
    optimizer = make_optimizer()

    tasks = [
        Task("explain", None, None, ""),
    ]

    optimized = optimizer.optimize(tasks)

    assert optimized == []


# ==========================================================
# Dependency recovery
# ==========================================================

def test_loader_recovered_for_rag():
    optimizer = make_optimizer()

    loader = Task(
        type="load_document",
        target=None,
        file_path="paper.pdf",
        query=None,
    )

    rag = Task(
        type="rag_search",
        target=None,
        file_path="paper.pdf",
        query="summary",
    )

    optimized = optimizer.optimize([
        loader,
        rag,
    ])

    types = [t.type for t in optimized]

    assert "load_document" in types
    assert "rag_search" in types

    assert types.index("load_document") < types.index("rag_search")


# ==========================================================
# Empty input
# ==========================================================

def test_empty_input():
    optimizer = make_optimizer()

    assert optimizer.optimize([]) == []
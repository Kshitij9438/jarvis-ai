"""
tests/test_plan_optimizer.py

Regression tests for planner.plan_optimizer.PlanOptimizer.
"""

from planner.plan_optimizer import PlanOptimizer
from planner.task import Task


def make_optimizer():
    return PlanOptimizer()


# ==========================================================
# Canonical query consumption
# ==========================================================

def test_plan_optimizer_does_not_reinterpret_query():
    optimizer = make_optimizer()

    tasks = [
        Task(
            type="explain",
            target=None,
            file_path=None,
            query="machine learning",
        )
    ]

    optimized = optimizer.optimize(tasks)

    assert len(optimized) == 1
    assert optimized[0].query == "machine learning"


def test_canonical_short_forms_are_valid():
    optimizer = make_optimizer()

    tasks = [
        Task("explain", None, None, "ai"),
        Task("explain", None, None, "ml"),
        Task("explain", None, None, "dl"),
    ]

    optimized = optimizer.optimize(tasks)

    assert [task.query for task in optimized] == [
        "ai",
        "ml",
        "dl",
    ]


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

    types = [task.type for task in optimized]

    assert "load_document" in types
    assert "rag_search" in types

    assert types.index("load_document") < types.index("rag_search")


# ==========================================================
# Empty input
# ==========================================================

def test_empty_input():
    optimizer = make_optimizer()

    assert optimizer.optimize([]) == []


def test_invalid_short_query_removed():
    optimizer = make_optimizer()

    tasks = [
        Task(
            type="explain",
            target=None,
            file_path=None,
            query="of",
        )
    ]

    optimized = optimizer.optimize(tasks)

    assert optimized == []


def test_all_canonical_short_forms_are_valid():
    optimizer = make_optimizer()

    tasks = [
        Task("explain", None, None, "ai"),
        Task("explain", None, None, "ml"),
        Task("explain", None, None, "dl"),
    ]

    optimized = optimizer.optimize(tasks)

    assert [
        task.query
        for task in optimized
    ] == ["ai", "ml", "dl"]

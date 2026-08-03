"""
tests/test_validator.py

Regression tests for planner.validator.PlanValidator.
"""

from planner.validator import PlanValidator
from planner.schema import Plan, Action


def make_validator():
    return PlanValidator()


# ==========================================================
# Open Website
# ==========================================================

def test_valid_open_website():
    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="open_website",
            args={"url": "https://github.com"}
        )
    ])

    validated = validator.validate(plan)

    assert len(validated.steps) == 1
    assert validated.steps[0].action == "open_website"


def test_invalid_open_website_removed():
    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="open_website",
            args={"url": "github"}
        )
    ])

    validated = validator.validate(plan)

    assert validated.steps == []


def test_url_with_spaces_removed():
    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="open_website",
            args={"url": "https://git hub.com"}
        )
    ])

    validated = validator.validate(plan)

    assert validated.steps == []


# ==========================================================
# Load Document
# ==========================================================

def test_valid_load_document():
    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="load_document",
            args={"file_path": "paper.pdf"}
        )
    ])

    validated = validator.validate(plan)

    assert len(validated.steps) == 1


def test_invalid_load_document_removed():
    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="load_document",
            args={}
        )
    ])

    validated = validator.validate(plan)

    assert validated.steps == []


# ==========================================================
# Explain
# ==========================================================

def test_valid_explain():
    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="explain",
            args={"query": "transformers"}
        )
    ])

    validated = validator.validate(plan)

    assert len(validated.steps) == 1


def test_invalid_explain_removed():
    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="explain",
            args={"query": "explain"}
        )
    ])

    validated = validator.validate(plan)

    assert validated.steps == []


# ==========================================================
# RAG / Summarize
# ==========================================================

def test_valid_rag_search():
    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="rag_search",
            args={"query": "transformers"}
        )
    ])

    validated = validator.validate(plan)

    assert len(validated.steps) == 1


def test_short_rag_query_removed():
    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="rag_search",
            args={"query": "ai"}
        )
    ])

    validated = validator.validate(plan)

    assert validated.steps == []


# ==========================================================
# Unknown Tools
# ==========================================================

def test_unknown_tool_preserved():
    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="future_tool",
            args={}
        )
    ])

    validated = validator.validate(plan)

    assert len(validated.steps) == 1
    assert validated.steps[0].action == "future_tool"


# ==========================================================
# Mixed Plans
# ==========================================================

def test_mixed_plan():
    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="open_website",
            args={"url": "https://github.com"}
        ),
        Action(
            action="open_website",
            args={"url": "github"}
        ),
        Action(
            action="explain",
            args={"query": "git"}
        ),
        Action(
            action="explain",
            args={"query": "explain"}
        ),
    ])

    validated = validator.validate(plan)

    actions = [s.action for s in validated.steps]

    assert actions == [
        "open_website",
        "explain",
    ]


# ==========================================================
# Dependency Validation
# ==========================================================

def test_rag_without_loader_is_preserved():
    """
    Current validator intentionally performs
    non-destructive dependency validation.
    """

    validator = make_validator()

    plan = Plan(steps=[
        Action(
            action="rag_search",
            args={"query": "summary"}
        )
    ])

    validated = validator.validate(plan)

    assert len(validated.steps) == 1
    assert validated.steps[0].action == "rag_search"


# ==========================================================
# Empty Plan
# ==========================================================

def test_empty_plan():
    validator = make_validator()

    validated = validator.validate(
        Plan(steps=[])
    )

    assert validated.steps == []
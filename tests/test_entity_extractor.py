"""
tests/test_entity_extractor.py

Regression tests for planner.entity_extractor.EntityExtractor.
"""

from unittest.mock import patch

from planner.entity_extractor import EntityExtractor


# --------------------------------------------------
# Helper
# --------------------------------------------------

def make_extractor():
    with patch("planner.entity_extractor.LLM"):
        return EntityExtractor()


# --------------------------------------------------
# Website extraction
# --------------------------------------------------

def test_extract_known_website():
    extractor = make_extractor()

    entities = extractor.extract("open github")

    assert entities["websites"] == ["github"]


def test_extract_multiple_websites():
    extractor = make_extractor()

    entities = extractor.extract(
        "open github and open youtube"
    )

    assert set(entities["websites"]) == {
        "github",
        "youtube",
    }


def test_extract_custom_domain():
    extractor = make_extractor()

    entities = extractor.extract(
        "visit openai.com"
    )

    assert "openai.com" in entities["websites"]


# --------------------------------------------------
# File paths
# --------------------------------------------------

def test_extract_windows_file_path():
    extractor = make_extractor()

    entities = extractor.extract(
        r'summarize "C:\Docs\paper.pdf"'
    )

    assert entities["file_path"] == r"C:\Docs\paper.pdf"


def test_extract_relative_file_path():
    extractor = make_extractor()

    entities = extractor.extract(
        "summarize docs/report.pdf"
    )

    assert entities["file_path"] == "docs/report.pdf"


# --------------------------------------------------
# Topic extraction
# --------------------------------------------------

def test_extract_explain_topic():
    extractor = make_extractor()

    entities = extractor.extract(
        "explain transformers"
    )

    assert entities["topics"] == ["transformers"]


def test_extract_learning_topic():
    extractor = make_extractor()

    entities = extractor.extract(
        "learn reinforcement learning"
    )

    assert entities["topics"] == [
        "reinforcement learning"
    ]


# --------------------------------------------------
# Cleanup
# --------------------------------------------------

def test_file_not_added_as_website():
    extractor = make_extractor()

    entities = extractor.extract(
        "summarize report.pdf"
    )

    assert entities["websites"] == []


def test_file_not_added_as_topic():
    extractor = make_extractor()

    entities = extractor.extract(
        "explain report.pdf"
    )

    assert all(
        "report.pdf" not in topic
        for topic in entities["topics"]
    )


def test_invalid_topic_removed():
    extractor = make_extractor()

    entities = extractor.extract(
        "explain"
    )

    assert "explain" not in entities["topics"]


# --------------------------------------------------
# Fallback behaviour
# --------------------------------------------------

def test_fallback_topic_generation():
    extractor = make_extractor()

    entities = extractor.extract(
        "gradient descent"
    )

    assert entities["topics"] == [
        "gradient descent"
    ]


def test_empty_input():
    extractor = make_extractor()

    entities = extractor.extract("")

    assert entities == {
        "websites": [],
        "file_path": None,
        "topics": [],
    }
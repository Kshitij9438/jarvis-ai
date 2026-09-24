from planner.canonical_query import CanonicalQuery


def test_empty_query_becomes_empty():
    assert CanonicalQuery.from_text(None).value == ""
    assert CanonicalQuery.from_text("").value == ""


def test_basic_query_is_lowercased():
    result = CanonicalQuery.from_text("Graph Traversal")

    assert result.value == "graph traversal"


def test_filler_words_are_removed():
    result = CanonicalQuery.from_text(
        "Please explain what is artificial intelligence"
    )

    assert result.value == "ai"


def test_synonym_normalization():
    assert (
        CanonicalQuery.from_text(
            "artificial intelligence"
        ).value
        == "ai"
    )

    assert (
        CanonicalQuery.from_text(
            "machine learning"
        ).value
        == "ml"
    )

    assert (
        CanonicalQuery.from_text(
            "deep learning"
        ).value
        == "dl"
    )


def test_learning_pattern_normalization():
    assert (
        CanonicalQuery.from_text(
            "learn machine learning"
        ).value
        == "ml basics"
    )


def test_noise_words_are_removed():
    result = CanonicalQuery.from_text(
        "please explain ai again"
    )

    assert result.value == "ai"


def test_duplicate_words_are_removed():
    result = CanonicalQuery.from_text(
        "git git git tutorial tutorial"
    )

    assert result.value == "git tutorial"


def test_existing_retrieval_query_semantics_are_preserved():
    result = CanonicalQuery.from_text(
        "what is reinforcement learning"
    )

    assert result.value == "reinforcement learning"


def test_canonical_query_is_immutable():
    result = CanonicalQuery.from_text("transformers")

    try:
        result.value = "changed"
    except AttributeError:
        pass
    else:
        raise AssertionError("CanonicalQuery must be immutable")


def test_canonical_query_is_deterministic():
    query = "Please explain artificial intelligence again"

    first = CanonicalQuery.from_text(query)
    second = CanonicalQuery.from_text(query)

    assert first == second
    assert first.value == second.value

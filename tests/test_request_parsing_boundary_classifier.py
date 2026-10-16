import pytest

from request_parsing.boundary_classifier import BoundaryClassifier
from request_parsing.internal_models import (
    BoundaryLabel,
    BoundaryPrediction,
    BoundarySignalType,
    CandidateBoundary,
)


@pytest.fixture
def classifier():
    return BoundaryClassifier()


def make_candidate(text, phrase, signal_type, occurrence=0):
    """Build a candidate with offsets into the original input."""
    search_from = 0

    for _ in range(occurrence + 1):
        start = text.index(phrase, search_from)
        search_from = start + len(phrase)

    end = start + len(phrase)

    left_end = len(text[:start].rstrip())

    right_start = end
    while right_start < len(text) and text[right_start].isspace():
        right_start += 1

    return CandidateBoundary(
        left_end=left_end,
        right_start=right_start,
        trigger_start=start,
        trigger_end=end,
        signal_type=signal_type,
    )


def assert_prediction(
    classifier,
    text,
    phrase,
    signal_type,
    expected_label,
    occurrence=0,
):
    candidate = make_candidate(text, phrase, signal_type, occurrence)

    predictions = classifier.classify(text, (candidate,))

    assert len(predictions) == 1
    prediction = predictions[0]

    assert isinstance(prediction, BoundaryPrediction)
    assert prediction.candidate == candidate
    assert prediction.label is expected_label
    assert prediction.boundary_probability is None
    assert isinstance(prediction.evidence, tuple)
    assert prediction.evidence

    return prediction


# ---------------------------------------------------------
# Basic contract
# ---------------------------------------------------------

def test_empty_candidates_returns_empty_tuple(classifier):
    assert classifier.classify("Open GitHub and explain Git", ()) == ()


def test_classifier_returns_tuple(classifier):
    text = "Open GitHub and explain Git"
    candidate = make_candidate(
        text, "and", BoundarySignalType.COORDINATOR
    )

    result = classifier.classify(text, (candidate,))

    assert isinstance(result, tuple)


def test_one_prediction_per_candidate(classifier):
    text = "Open GitHub; then explain Git"

    candidates = (
        make_candidate(text, ";", BoundarySignalType.SEMICOLON),
        make_candidate(text, "then", BoundarySignalType.SEQUENCE_MARKER),
    )

    predictions = classifier.classify(text, candidates)

    assert len(predictions) == len(candidates)
    assert tuple(p.candidate for p in predictions) == candidates


def test_classifier_is_deterministic(classifier):
    text = "Open GitHub and explain Git"
    candidate = make_candidate(
        text, "and", BoundarySignalType.COORDINATOR
    )

    assert classifier.classify(text, (candidate,)) == (
        classifier.classify(text, (candidate,))[0],
    )


def test_probability_is_not_invented(classifier):
    text = "Open GitHub and explain Git"
    candidate = make_candidate(
        text, "and", BoundarySignalType.COORDINATOR
    )

    prediction = classifier.classify(text, (candidate,))[0]

    assert prediction.boundary_probability is None


# ---------------------------------------------------------
# Explicit sequence markers
# ---------------------------------------------------------

def test_then_is_classified_as_boundary(classifier):
    prediction = assert_prediction(
        classifier,
        "Open GitHub then explain Git",
        "then",
        BoundarySignalType.SEQUENCE_MARKER,
        BoundaryLabel.BOUNDARY,
    )

    assert "explicit_sequence_marker" in prediction.evidence


def test_after_that_is_classified_as_boundary(classifier):
    prediction = assert_prediction(
        classifier,
        "Open GitHub after that explain Git",
        "after that",
        BoundarySignalType.SEQUENCE_MARKER,
        BoundaryLabel.BOUNDARY,
    )

    assert "explicit_sequence_marker" in prediction.evidence


def test_next_needs_action_evidence(classifier):
    assert_prediction(
        classifier,
        "Open GitHub next explain Git",
        "next",
        BoundarySignalType.SEQUENCE_MARKER,
        BoundaryLabel.BOUNDARY,
    )

    assert_prediction(
        classifier,
        "Open GitHub next my issues",
        "next",
        BoundarySignalType.SEQUENCE_MARKER,
        BoundaryLabel.UNCERTAIN,
    )


# ---------------------------------------------------------
# Semicolons
# ---------------------------------------------------------

def test_semicolon_is_classified_as_boundary(classifier):
    prediction = assert_prediction(
        classifier,
        "Open GitHub; explain Git",
        ";",
        BoundarySignalType.SEMICOLON,
        BoundaryLabel.BOUNDARY,
    )

    assert "semicolon_separator" in prediction.evidence


# ---------------------------------------------------------
# Sentence-ending punctuation
# ---------------------------------------------------------

@pytest.mark.parametrize("punctuation", [".", "?", "!"])
def test_punctuation_with_whitespace_is_boundary(
    classifier, punctuation
):
    text = f"Open GitHub{punctuation} Explain Git"

    prediction = assert_prediction(
        classifier,
        text,
        punctuation,
        BoundarySignalType.PUNCTUATION,
        BoundaryLabel.BOUNDARY,
    )

    assert "sentence_terminal_punctuation" in prediction.evidence


def test_punctuation_without_separator_is_continuation(classifier):
    assert_prediction(
        classifier,
        "Open Git.Explain Git",
        ".",
        BoundarySignalType.PUNCTUATION,
        BoundaryLabel.CONTINUATION,
    )


# ---------------------------------------------------------
# Coordinator: and
# ---------------------------------------------------------

def test_and_between_action_like_phrases_is_boundary(classifier):
    prediction = assert_prediction(
        classifier,
        "Open GitHub and explain Git",
        "and",
        BoundarySignalType.COORDINATOR,
        BoundaryLabel.BOUNDARY,
    )

    assert "two_action_like_phrases" in prediction.evidence


def test_and_between_coordinated_objects_is_continuation(classifier):
    prediction = assert_prediction(
        classifier,
        "Explain Python and C++",
        "and",
        BoundarySignalType.COORDINATOR,
        BoundaryLabel.CONTINUATION,
    )

    assert "right_side_not_action_like" in prediction.evidence


# ---------------------------------------------------------
# Coordinator: or
# ---------------------------------------------------------

def test_or_defaults_to_continuation(classifier):
    prediction = assert_prediction(
        classifier,
        "Open GitHub or explain Git",
        "or",
        BoundarySignalType.COORDINATOR,
        BoundaryLabel.CONTINUATION,
    )

    assert "alternative_coordinator" in prediction.evidence


# ---------------------------------------------------------
# Coordinator: but
# ---------------------------------------------------------

def test_but_returns_uncertain(classifier):
    prediction = assert_prediction(
        classifier,
        "Open GitHub but explain Git differently",
        "but",
        BoundarySignalType.COORDINATOR,
        BoundaryLabel.UNCERTAIN,
    )

    assert "contrast_requires_context" in prediction.evidence


# ---------------------------------------------------------
# Commas
# ---------------------------------------------------------

def test_comma_between_action_like_phrases_is_boundary(classifier):
    prediction = assert_prediction(
        classifier,
        "Open GitHub, explain Git",
        ",",
        BoundarySignalType.COMMA,
        BoundaryLabel.BOUNDARY,
    )

    assert "two_action_like_phrases" in prediction.evidence


def test_comma_without_two_action_like_phrases_is_uncertain(classifier):
    prediction = assert_prediction(
        classifier,
        "Compare Python, C++",
        ",",
        BoundarySignalType.COMMA,
        BoundaryLabel.UNCERTAIN,
    )

    assert "comma_without_two_action_like_phrases" in prediction.evidence


# ---------------------------------------------------------
# Evidence and ordering
# ---------------------------------------------------------

def test_each_prediction_has_a_candidate_and_evidence(classifier):
    text = "Open GitHub; then explain Git"

    candidates = (
        make_candidate(text, ";", BoundarySignalType.SEMICOLON),
        make_candidate(text, "then", BoundarySignalType.SEQUENCE_MARKER),
    )

    predictions = classifier.classify(text, candidates)

    for prediction in predictions:
        assert isinstance(prediction.candidate, CandidateBoundary)
        assert isinstance(prediction.label, BoundaryLabel)
        assert prediction.evidence
        assert all(isinstance(item, str) for item in prediction.evidence)


def test_prediction_order_matches_candidate_order(classifier):
    text = "Open GitHub; then explain Git"

    later = make_candidate(
        text, "then", BoundarySignalType.SEQUENCE_MARKER
    )
    earlier = make_candidate(
        text, ";", BoundarySignalType.SEMICOLON
    )

    candidates = (later, earlier)
    predictions = classifier.classify(text, candidates)

    assert tuple(p.candidate for p in predictions) == candidates

@pytest.mark.parametrize(
    ("text", "phrase", "signal_type", "occurrence"),
    [
        (
            "Download the data and plot the results",
            "and",
            BoundarySignalType.COORDINATOR,
            0,
        ),
        (
            "Build the package next publish it.",
            "next",
            BoundarySignalType.SEQUENCE_MARKER,
            0,
        ),
        (
            'Use the file "report, draft.csv" and summarize it',
            "and",
            BoundarySignalType.COORDINATOR,
            0,
        ),
        (
            "Explain (A or B) and choose the best option",
            "and",
            BoundarySignalType.COORDINATOR,
            0,
        ),
        (
            "Explain {x and y} and simplify the expression",
            "and",
            BoundarySignalType.COORDINATOR,
            1,
        ),
        (
            "Explain the cause and suggest a fix",
            "and",
            BoundarySignalType.COORDINATOR,
            0,
        ),
        (
            "List the issues and prioritize them",
            "and",
            BoundarySignalType.COORDINATOR,
            0,
        ),
    ],
)
def test_action_verb_vocabulary_covers_evaluation_misses(
    classifier,
    text,
    phrase,
    signal_type,
    occurrence,
):
    assert_prediction(
        classifier,
        text,
        phrase,
        signal_type,
        BoundaryLabel.BOUNDARY,
        occurrence=occurrence,
    )
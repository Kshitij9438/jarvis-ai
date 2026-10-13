import pytest

from request_parsing.internal_models import Token
from request_parsing.tokenizer import Tokenizer


@pytest.fixture
def tokenizer():
    return Tokenizer()


def test_tokenize_empty_input(tokenizer):
    assert tokenizer.tokenize("") == ()


def test_tokenize_whitespace_only_input(tokenizer):
    assert tokenizer.tokenize("   \t\n  ") == ()


def test_tokenize_words_and_punctuation(tokenizer):
    tokens = tokenizer.tokenize("Open GitHub, then explain Git.")

    assert tuple(token.text for token in tokens) == (
        "Open",
        "GitHub",
        ",",
        "then",
        "explain",
        "Git",
        ".",
    )


def test_tokenize_preserves_original_character_offsets(tokenizer):
    text = "Open GitHub, then explain Git."

    tokens = tokenizer.tokenize(text)

    for token in tokens:
        assert text[token.start:token.end] == token.text
        assert token.start < token.end


def test_tokenize_repeated_words_with_correct_offsets(tokenizer):
    text = "go go go"

    tokens = tokenizer.tokenize(text)

    assert tuple(token.text for token in tokens) == ("go", "go", "go")
    assert tuple((token.start, token.end) for token in tokens) == (
        (0, 2),
        (3, 5),
        (6, 8),
    )


def test_tokenize_contractions(tokenizer):
    text = "I don't know."

    tokens = tokenizer.tokenize(text)

    assert tuple(token.text for token in tokens) == (
        "I",
        "do",
        "n't",
        "know",
        ".",
    )

    for token in tokens:
        assert text[token.start:token.end] == token.text


def test_tokenize_hyphenated_words(tokenizer):
    text = "Build a request-aware parser."

    tokens = tokenizer.tokenize(text)

    assert tuple(token.text for token in tokens) == (
        "Build",
        "a",
        "request",
        "-",
        "aware",
        "parser",
        ".",
    )

    for token in tokens:
        assert text[token.start:token.end] == token.text


def test_tokenize_unicode_text(tokenizer):
    text = "café naïve 東京"

    tokens = tokenizer.tokenize(text)

    assert tuple(token.text for token in tokens) == (
        "café",
        "naïve",
        "東京",
    )

    for token in tokens:
        assert text[token.start:token.end] == token.text


def test_tokenize_preserves_offsets_with_repeated_whitespace(tokenizer):
    text = "  Open   GitHub  "

    tokens = tokenizer.tokenize(text)

    assert tuple(token.text for token in tokens) == ("Open", "GitHub")
    assert text[tokens[0].start:tokens[0].end] == "Open"
    assert text[tokens[1].start:tokens[1].end] == "GitHub"

    assert (tokens[0].start, tokens[0].end) == (2, 6)
    assert (tokens[1].start, tokens[1].end) == (9, 15)


def test_tokenizer_returns_tuple_of_our_token_model(tokenizer):
    tokens = tokenizer.tokenize("Open GitHub.")

    assert isinstance(tokens, tuple)
    assert all(isinstance(token, Token) for token in tokens)


def test_tokenization_is_deterministic(tokenizer):
    text = "Open GitHub and explain Git."

    first_result = tokenizer.tokenize(text)
    second_result = tokenizer.tokenize(text)

    assert first_result == second_result


def test_token_order_matches_original_text(tokenizer):
    text = "Open GitHub and explain Git."

    tokens = tokenizer.tokenize(text)

    assert all(
        tokens[index].start < tokens[index + 1].start
        for index in range(len(tokens) - 1)
    )

    assert all(
        tokens[index].end <= tokens[index + 1].start
        for index in range(len(tokens) - 1)
    )
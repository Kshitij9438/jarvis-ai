import spacy

from request_parsing.internal_models import Token


class Tokenizer:
    """Tokenize request text while preserving original offsets."""

    def __init__(self) -> None:
        self._nlp = spacy.blank("en")

    def tokenize(self, text: str) -> tuple[Token, ...]:
        doc = self._nlp.make_doc(text)

        return tuple(
            Token(
                text=token.text,
                start=token.idx,
                end=token.idx + len(token.text),
            )
            for token in doc
            if not token.is_space
        )
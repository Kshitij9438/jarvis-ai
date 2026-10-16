
from request_parsing.internal_models import (
    BoundarySignalType,
    StructuralSignal,
)
from request_parsing.tokenizer import Tokenizer


class StructuralScanner:
    """Detect structural signals without deciding request boundaries."""

    def __init__(self, tokenizer: Tokenizer):
        self._tokenizer = tokenizer

    def scan(self, text: str) -> tuple[StructuralSignal, ...]:
        """Return structural signals in original-text order."""
        tokens = self._tokenizer.tokenize(text)
        signals = []

        i = 0

        while i < len(tokens):
            token = tokens[i]
            normalized = token.text.casefold()

            # Detect the multiword sequence marker "and then".
            # Treat it as one signal so the eventual split excludes
            # both words from the resulting request segments.
            if (
                normalized == "and"
                and i + 1 < len(tokens)
                and tokens[i + 1].text.casefold() == "then"
            ):
                signals.append(
                    StructuralSignal(
                        start=token.start,
                        end=tokens[i + 1].end,
                        signal_type=BoundarySignalType.SEQUENCE_MARKER,
                    )
                )
                i += 2
                continue

            # Detect the multiword sequence marker "after that".
            if (
                normalized == "after"
                and i + 1 < len(tokens)
                and tokens[i + 1].text.casefold() == "that"
            ):
                signals.append(
                    StructuralSignal(
                        start=token.start,
                        end=tokens[i + 1].end,
                        signal_type=BoundarySignalType.SEQUENCE_MARKER,
                    )
                )
                i += 2
                continue

            if token.text in {".", "?", "!"}:
                signal_type = BoundarySignalType.PUNCTUATION

            elif token.text == ";":
                signal_type = BoundarySignalType.SEMICOLON

            elif token.text == ",":
                signal_type = BoundarySignalType.COMMA

            elif normalized in {"and", "or", "but"}:
                signal_type = BoundarySignalType.COORDINATOR

            elif normalized in {"then", "next"}:
                signal_type = BoundarySignalType.SEQUENCE_MARKER

            else:
                i += 1
                continue

            signals.append(
                StructuralSignal(
                    start=token.start,
                    end=token.end,
                    signal_type=signal_type,
                )
            )

            i += 1

        return tuple(signals)

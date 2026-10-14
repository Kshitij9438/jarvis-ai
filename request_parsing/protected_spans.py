from request_parsing.internal_models import (
    ProtectedSpan,
    ProtectedSpanKind,
)


class ProtectedSpanDetector:
    """Detect protected regions without modifying the original text."""

    @staticmethod
    def _detect_quoted_text(text: str) -> tuple[ProtectedSpan, ...]:
        spans = []
        i = 0

        while i < len(text):
            if text[i] != '"':
                i += 1
                continue

            # An opening quote must occur at the beginning, after
            # whitespace, or after a plausible opening delimiter.
            is_opener = (
                i == 0
                or text[i - 1].isspace()
                or text[i - 1] in "([{=:,"
            )

            if not is_opener:
                # Treat an unmatched closing quote as ordinary text.
                i += 1
                continue

            end = text.find('"', i + 1)

            if end == -1:
                # An unmatched opening quote protects the remaining text.
                if i + 1 < len(text):
                    spans.append(
                        ProtectedSpan(
                            start=i + 1,
                            end=len(text),
                            kind=ProtectedSpanKind.QUOTED_TEXT,
                        )
                    )
                break

            if i + 1 < end:
                spans.append(
                    ProtectedSpan(
                        start=i + 1,
                        end=end,
                        kind=ProtectedSpanKind.QUOTED_TEXT,
                    )
                )

            i = end + 1

        return tuple(spans)

    @staticmethod
    def _detect_delimited_spans(
        text: str,
        opening: str,
        closing: str,
        kind: ProtectedSpanKind,
    ) -> tuple[ProtectedSpan, ...]:
        """Detect nested or repeated regions enclosed by delimiters."""
        spans = []
        stack = []

        for i, char in enumerate(text):
            if char == opening:
                stack.append(i)

            elif char == closing and stack:
                start = stack.pop() + 1
                end = i

                if start < end:
                    spans.append(
                        ProtectedSpan(
                            start=start,
                            end=end,
                            kind=kind,
                        )
                    )

        # An unmatched opening delimiter protects the remaining text.
        for opening_index in stack:
            start = opening_index + 1
            if start < len(text):
                spans.append(
                    ProtectedSpan(
                        start=start,
                        end=len(text),
                        kind=kind,
                    )
                )

        return tuple(spans)

    @classmethod
    def _detect_parenthetical(
        cls,
        text: str,
    ) -> tuple[ProtectedSpan, ...]:
        return cls._detect_delimited_spans(
            text,
            "(",
            ")",
            ProtectedSpanKind.PARENTHETICAL,
        )

    @classmethod
    def _detect_bracketed(
        cls,
        text: str,
    ) -> tuple[ProtectedSpan, ...]:
        return cls._detect_delimited_spans(
            text,
            "[",
            "]",
            ProtectedSpanKind.BRACKETED,
        )

    @staticmethod
    def _trim_trailing_punctuation(
        text: str,
        start: int,
        end: int,
    ) -> int:
        """Exclude common sentence punctuation following a span."""
        while end > start and text[end - 1] in ".,!?;:)]}":
            end -= 1
        return end

    @classmethod
    def _detect_urls(cls, text: str) -> tuple[ProtectedSpan, ...]:
        spans = []
        prefixes = ("https://", "http://", "www.")
        i = 0

        while i < len(text):
            prefix = next(
                (
                    candidate
                    for candidate in prefixes
                    if text[i:i + len(candidate)].casefold() == candidate
                ),
                None,
            )

            if prefix is None:
                i += 1
                continue

            # Avoid detecting a URL in the middle of an ordinary word.
            if i > 0 and (
                text[i - 1].isalnum() or text[i - 1] in "_+-."
            ):
                i += 1
                continue

            end = i

            while end < len(text) and not text[end].isspace():
                if text[end] in "\"'`<>":
                    break
                end += 1

            end = cls._trim_trailing_punctuation(text, i, end)

            if i < end:
                spans.append(
                    ProtectedSpan(
                        start=i,
                        end=end,
                        kind=ProtectedSpanKind.URL,
                    )
                )
                i = end
            else:
                i += 1

        return tuple(spans)

    @classmethod
    def _detect_code(cls, text: str) -> tuple[ProtectedSpan, ...]:
        """Detect inline or fenced code marked with backticks."""
        spans = []
        i = 0

        while i < len(text):
            if text[i] != "`":
                i += 1
                continue

            # Match the complete opening backtick run.
            marker_end = i
            while marker_end < len(text) and text[marker_end] == "`":
                marker_end += 1

            marker = text[i:marker_end]
            content_start = marker_end
            closing = text.find(marker, content_start)

            if closing == -1:
                # An unmatched code opener protects the remaining text.
                if content_start < len(text):
                    spans.append(
                        ProtectedSpan(
                            start=content_start,
                            end=len(text),
                            kind=ProtectedSpanKind.CODE,
                        )
                    )
                break

            if content_start < closing:
                spans.append(
                    ProtectedSpan(
                        start=content_start,
                        end=closing,
                        kind=ProtectedSpanKind.CODE,
                    )
                )

            i = closing + len(marker)

        return tuple(spans)

    @classmethod
    def _detect_file_paths(
        cls,
        text: str,
        url_spans: tuple[ProtectedSpan, ...] = (),
    ) -> tuple[ProtectedSpan, ...]:
        """Detect absolute Unix-style file paths."""
        spans = []
        i = 0

        while i < len(text):
            if text[i] != "/":
                i += 1
                continue

            # Avoid treating slashes inside a detected URL as file paths.
            if any(span.start <= i < span.end for span in url_spans):
                i += 1
                continue

            # A path must start at a plausible text boundary.
            is_path_start = (
                i == 0
                or text[i - 1].isspace()
                or text[i - 1] in "\"'([{=:,"
            )

            if not is_path_start:
                i += 1
                continue

            end = i
            while end < len(text):
                if text[end].isspace() or text[end] in "\"'`<>":
                    break
                end += 1

            end = cls._trim_trailing_punctuation(text, i, end)

            if i < end:
                spans.append(
                    ProtectedSpan(
                        start=i,
                        end=end,
                        kind=ProtectedSpanKind.FILE_PATH,
                    )
                )
                i = end
            else:
                i += 1

        return tuple(spans)

    def detect(self, text: str) -> tuple[ProtectedSpan, ...]:
        """Return all detected spans in deterministic order."""
        if not text or text.isspace():
            return ()

        # Keep the original text unchanged so all offsets remain valid.
        quoted_spans = self._detect_quoted_text(text)
        parenthetical_spans = self._detect_parenthetical(text)
        bracketed_spans = self._detect_bracketed(text)
        code_spans = self._detect_code(text)
        url_spans = self._detect_urls(text)
        file_path_spans = self._detect_file_paths(text, url_spans)

        spans = (
            quoted_spans
            + parenthetical_spans
            + bracketed_spans
            + code_spans
            + url_spans
            + file_path_spans
        )

        return tuple(
            sorted(
                spans,
                key=lambda span: (
                    span.start,
                    -(span.end - span.start),
                    span.kind.value,
                ),
            )
        )

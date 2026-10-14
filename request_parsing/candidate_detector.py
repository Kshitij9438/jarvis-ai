from request_parsing.internal_models import (
    CandidateBoundary,
    ProtectedSpan,
    StructuralSignal,
)


class CandidateDetector:
    """Generate possible request boundaries without classifying them."""

    def detect(
        self,
        text: str,
        signals: tuple[StructuralSignal, ...],
        protected_spans: tuple[ProtectedSpan, ...],
    ) -> tuple[CandidateBoundary, ...]:
        """Return eligible candidate boundaries in positional order."""
        candidates = []

        for signal in signals:
            # Ignore malformed signal offsets.
            if not (
                0 <= signal.start < signal.end <= len(text)
            ):
                continue

            # A structural signal must not overlap a protected span.
            overlaps_protected_span = any(
                signal.start < span.end
                and span.start < signal.end
                for span in protected_spans
            )

            if overlaps_protected_span:
                continue

            # Find the end of the meaningful text on the left.
            left_end = len(text[:signal.start].rstrip())

            # Find the start of the meaningful text on the right.
            right_start = signal.end

            while (
                right_start < len(text)
                and text[right_start].isspace()
            ):
                right_start += 1

            # A candidate requires meaningful text on both sides.
            if left_end == 0 or right_start >= len(text):
                continue

            candidates.append(
                CandidateBoundary(
                    left_end=left_end,
                    right_start=right_start,
                    trigger_start=signal.start,
                    trigger_end=signal.end,
                    signal_type=signal.signal_type,
                )
            )

        # Preserve all candidates while ensuring deterministic ordering.
        candidates.sort(
            key=lambda candidate: (
                candidate.trigger_start,
                candidate.trigger_end,
                candidate.signal_type.value,
            )
        )

        return tuple(candidates)

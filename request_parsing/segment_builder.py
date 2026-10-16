
from request_parsing.internal_models import (
    BoundaryPrediction,
    CandidateBoundary,
)
from request_parsing.models import RequestParseResult, RequestSegment


class SegmentBuilder:
    """Build request segments from accepted boundary predictions."""

    def build(
        self,
        original_text: str,
        accepted_predictions: tuple[BoundaryPrediction, ...],
    ) -> RequestParseResult:
        """Construct ordered, non-empty segments with original offsets."""

        # Empty or whitespace-only input contains no segments.
        if not original_text or original_text.isspace():
            return RequestParseResult(
                original_text=original_text,
                segments=(),
            )

        # Sort by source position, independent of prediction input order.
        ordered_predictions = sorted(
            accepted_predictions,
            key=lambda prediction: (
                prediction.candidate.trigger_start,
                prediction.candidate.trigger_end,
                prediction.candidate.signal_type.value,
            ),
        )

        segments: list[RequestSegment] = []
        seen_candidates: set[CandidateBoundary] = set()
        segment_start = 0
        text_length = len(original_text)

        for prediction in ordered_predictions:
            candidate = prediction.candidate

            # Ignore exact duplicate candidates.
            if candidate in seen_candidates:
                continue

            self._validate_candidate(candidate, text_length)

            # The decoder should already have resolved overlapping
            # candidates. Fail clearly if that contract is violated.
            if candidate.left_end < segment_start:
                raise ValueError(
                    "Accepted boundary candidates must not overlap. "
                    "Resolve competing boundaries before building segments."
                )

            # The left segment ends immediately before the separator.
            self._append_segment(
                original_text,
                segment_start,
                candidate.left_end,
                segments,
            )

            # Resume after the separator and its leading whitespace.
            segment_start = candidate.right_start
            seen_candidates.add(candidate)

        # Append the final segment after the last accepted boundary.
        self._append_segment(
            original_text,
            segment_start,
            text_length,
            segments,
        )

        return RequestParseResult(
            original_text=original_text,
            segments=tuple(segments),
        )

    @staticmethod
    def _validate_candidate(
        candidate: CandidateBoundary,
        text_length: int,
    ) -> None:
        """Ensure boundary offsets form a valid range in the source text."""

        valid = (
            0 <= candidate.left_end
            <= candidate.trigger_start
            < candidate.trigger_end
            <= candidate.right_start
            <= text_length
        )

        if not valid:
            raise ValueError(
                "Boundary candidate contains invalid offsets for "
                "the original request."
            )

    @staticmethod
    def _append_segment(
        original_text: str,
        start: int,
        end: int,
        segments: list[RequestSegment],
    ) -> None:
        """Append a non-empty segment, trimming whitespace only."""

        # Trim leading whitespace while keeping offsets accurate.
        while start < end and original_text[start].isspace():
            start += 1

        # Trim trailing whitespace while keeping offsets accurate.
        while start < end and original_text[end - 1].isspace():
            end -= 1

        # Never emit empty or whitespace-only segments.
        if start >= end:
            return

        segments.append(
            RequestSegment(
                text=original_text[start:end],
                start=start,
                end=end,
            )
        )


from request_parsing.internal_models import (
    BoundaryLabel,
    BoundaryPrediction,
    BoundarySignalType,
    CandidateBoundary,
)


class BoundaryDecoder:
    """Accept boundary predictions using priority and overlap rules."""

    _SIGNAL_PRIORITY = {
        BoundarySignalType.SEQUENCE_MARKER: 5,
        BoundarySignalType.SEMICOLON: 4,
        BoundarySignalType.PUNCTUATION: 3,
        BoundarySignalType.COORDINATOR: 2,
        BoundarySignalType.COMMA: 1,
    }

    def decode(
        self,
        predictions: tuple[BoundaryPrediction, ...],
    ) -> tuple[BoundaryPrediction, ...]:
        # Only boundary predictions are eligible for acceptance.
        boundary_predictions = [
            prediction
            for prediction in predictions
            if prediction.label is BoundaryLabel.BOUNDARY
        ]

        # Evaluate stronger signals first, independent of input ordering.
        ordered_predictions = sorted(
            boundary_predictions,
            key=lambda prediction: (
                -self._SIGNAL_PRIORITY.get(
                    prediction.candidate.signal_type, 0
                ),
                prediction.candidate.trigger_start,
                prediction.candidate.trigger_end,
                prediction.candidate.signal_type.value,
                prediction.candidate.left_end,
                prediction.candidate.right_start,
            ),
        )

        accepted = []
        seen_candidates: set[CandidateBoundary] = set()

        for prediction in ordered_predictions:
            candidate = prediction.candidate

            # Do not accept the same candidate twice.
            if candidate in seen_candidates:
                continue

            # Resolve candidates whose split regions overlap.
            if any(
                self._overlaps(candidate, existing.candidate)
                for existing in accepted
            ):
                continue

            seen_candidates.add(candidate)
            accepted.append(prediction)

        # Return accepted predictions in their original text order.
        accepted.sort(
            key=lambda prediction: (
                prediction.candidate.trigger_start,
                prediction.candidate.trigger_end,
            )
        )

        return tuple(accepted)

    @staticmethod
    def _overlaps(
        first: CandidateBoundary,
        second: CandidateBoundary,
    ) -> bool:
        """Check whether two candidate split regions overlap."""
        return (
            first.left_end < second.right_start
            and second.left_end < first.right_start
        )


from request_parsing.internal_models import (
    BoundaryLabel,
    BoundaryPrediction,
    CandidateBoundary,
)


class BoundaryDecoder:
    def decode(
        self,
        predictions: tuple[BoundaryPrediction, ...],
    ) -> tuple[BoundaryPrediction, ...]:
        ordered_predictions = sorted(
            predictions,
            key=lambda prediction: (
                prediction.candidate.trigger_start,
                prediction.candidate.trigger_end,
                prediction.candidate.signal_type.value,
            ),
        )

        final_predictions = []
        seen_candidates: set[CandidateBoundary] = set()

        for prediction in ordered_predictions:
            # Accept only predictions classified as boundaries.
            if prediction.label is not BoundaryLabel.BOUNDARY:
                continue

            candidate = prediction.candidate

            # Skip a candidate that has already been accepted.
            if candidate in seen_candidates:
                continue

            seen_candidates.add(candidate)
            final_predictions.append(prediction)

        return tuple(final_predictions)

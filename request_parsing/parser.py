
from request_parsing.boundary_classifier import BoundaryClassifier
from request_parsing.boundary_decoder import BoundaryDecoder
from request_parsing.candidate_detector import CandidateDetector
from request_parsing.protected_spans import ProtectedSpanDetector
from request_parsing.models import RequestParseResult
from request_parsing.segment_builder import SegmentBuilder
from request_parsing.structural_scanner import StructuralScanner
from request_parsing.tokenizer import Tokenizer


class RequestParser:
    """Orchestrate the request-parsing pipeline."""

    def __init__(self) -> None:
        self._tokenizer = Tokenizer()
        self._structural_scanner = StructuralScanner(self._tokenizer)
        self._protected_span_detector = ProtectedSpanDetector()
        self._candidate_detector = CandidateDetector()
        self._boundary_classifier = BoundaryClassifier()
        self._boundary_decoder = BoundaryDecoder()
        self._segment_builder = SegmentBuilder()

    def parse(self, original_text: str) -> RequestParseResult:
        """Parse raw input into independently actionable segments."""

        # Empty and whitespace-only requests have no segments.
        if not original_text or original_text.isspace():
            return self._segment_builder.build(original_text, ())

        # Stage 1: Identify structural signals.
        signals = self._structural_scanner.scan(original_text)

        # Stage 2: Identify spans that should be protected from splitting.
        protected_spans = self._protected_span_detector.detect(original_text)

        # Stage 3: Generate possible boundary candidates.
        candidates = self._candidate_detector.detect(
            original_text,
            signals,
            protected_spans,
        )

        # Stage 4: Classify each candidate.
        predictions = self._boundary_classifier.classify(
            original_text,
            candidates,
        )

        # Stage 5: Resolve competing and overlapping predictions.
        accepted_predictions = self._boundary_decoder.decode(predictions)

        # Stage 6: Construct the public result and its segments.
        return self._segment_builder.build(
            original_text,
            accepted_predictions,
        )

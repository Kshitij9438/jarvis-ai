from __future__ import annotations

from request_parsing.parser import RequestParser

from planner.canonical_query import CanonicalQuery
from planner.entity_extractor import EntityExtractor
from planner.request_understanding import RequestUnderstanding


class RequestUnderstandingAdapter:
    """
    M7.2 compatibility adapter.

    This class introduces an explicit Request Understanding boundary
    without changing the existing planner's behavior.

    It currently owns:
    - request segmentation
    - entity extraction
    - canonical query construction
    - construction of RequestUnderstanding

    Tool selection, task construction, optimization, and planning
    remain owned by the existing Planner pipeline.

    Reference resolution is intentionally not performed here yet.
    That migration belongs to the next incremental step once the
    request-understanding boundary is established.
    """

    def __init__(
        self,
        entity_extractor: EntityExtractor,
        request_parser: RequestParser | None = None,
    ):
        self.entity_extractor = entity_extractor
        self.request_parser = (
            request_parser if request_parser is not None else RequestParser()
        )

    def understand(
        self,
        user_input: str,
        decision,
    ) -> list[RequestUnderstanding]:
        """
        Convert a raw request into structured request-understanding
        records while preserving the current planner's segmentation
        behavior.

        One RequestUnderstanding object is produced per existing
        planner segment.
        """
        parse_result = self.request_parser.parse(user_input)
        segments = [
            segment.text
            for segment in parse_result.segments
        ]
        results = []

        for segment in segments:
            entities = self.entity_extractor.extract(segment)
            canonical_query = CanonicalQuery.from_text(segment)

            results.append(
                RequestUnderstanding(
                    original_query=segment,
                    canonical_query=canonical_query.value,
                    entities=entities,
                    decision=decision,
                )
            )

        return results
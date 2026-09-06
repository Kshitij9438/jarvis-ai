from __future__ import annotations

import re

from planner.entity_extractor import EntityExtractor
from planner.request_understanding import RequestUnderstanding


class RequestUnderstandingAdapter:
    """
    M7.2 compatibility adapter.

    This class introduces an explicit Request Understanding boundary
    without changing the existing planner's behavior.

    It currently owns only orchestration:
    - request segmentation
    - entity extraction
    - construction of RequestUnderstanding

    Tool selection, task construction, optimization, and planning
    remain owned by the existing Planner pipeline.

    Reference resolution is intentionally not performed here yet.
    That migration belongs to the next incremental step once the
    request-understanding boundary is established.
    """

    def __init__(self, entity_extractor: EntityExtractor):
        self.entity_extractor = entity_extractor

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
        segments = [
            segment.strip()
            for segment in re.split(
                r"\band\b|\bthen\b|,",
                user_input,
            )
            if segment.strip()
        ]

        results = []

        for segment in segments:
            entities = self.entity_extractor.extract(segment)

            results.append(
                RequestUnderstanding(
                    original_query=segment,
                    entities=entities,
                    decision=decision,
                )
            )

        return results

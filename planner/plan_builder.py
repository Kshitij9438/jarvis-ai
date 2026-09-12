from __future__ import annotations

import re

from execution.context_signals import has_retrieved_content
from planner.entity_extractor import EntityExtractor
from planner.retrieval_decision import (
    RetrievalDecision,
    should_use_retrieval,
)
from planner.retrieval_signals import (
    has_explicit_search_request,
    requires_current_information,
)
from planner.task_builder import TaskBuilder
from planner.tool_selector import ToolSelector


class PlanBuilder:
    """
    M7 planning boundary.

    Owns the construction of Tasks from a user request.

    Responsibilities:
    - segment the request
    - determine the required capability
    - select concrete tools
    - apply retrieval policy
    - expand static tool dependencies
    - extract entities
    - delegate task construction to TaskBuilder

    This component intentionally preserves the existing Planner behavior.
    It does not optimize, validate, score, or execute plans.
    """

    def __init__(
        self,
        registry,
        capability_selector,
        tool_selector: ToolSelector,
        task_builder: TaskBuilder,
        entity_extractor: EntityExtractor,
    ):
        self.registry = registry
        self.capability_selector = capability_selector
        self.tool_selector = tool_selector
        self.task_builder = task_builder
        self.entity_extractor = entity_extractor

    def build(self, user_input: str, context=None) -> list:
        """
        Build tasks from the user request.

        The implementation intentionally mirrors the existing
        per-segment construction logic from Planner.
        """

        segments = [
            segment.strip()
            for segment in re.split(r"\band\b|\bthen\b|,", user_input)
            if segment.strip()
        ]

        print(f"DEBUG: Segments → {segments}")

        all_tasks = []

        for segment in segments:
            print(f"\n--- SEGMENT: {segment} ---")

            capability = self.capability_selector.select(segment)

            segment_tools = self.tool_selector.select(
                segment,
                top_k=2,
                context=context,
                capability=capability,
            )

            should_retrieve = self._should_use_retriever(
                segment,
                context,
            )

            if should_retrieve:
                retriever = self.registry.get("web_retriever")

                if retriever and all(
                    tool.name != "web_retriever"
                    for tool in segment_tools
                ):
                    segment_tools.append(retriever)

            else:
                segment_tools = [
                    tool
                    for tool in segment_tools
                    if tool.name != "web_retriever"
                ]

            # Static dependency expansion.
            final_tools = []
            added = set()

            for tool in segment_tools:
                for dep_name in getattr(tool, "requires", []):
                    dep_tool = self.registry.get(dep_name)

                    if dep_tool and dep_tool.name not in added:
                        final_tools.append(dep_tool)
                        added.add(dep_tool.name)

                if tool.name not in added:
                    final_tools.append(tool)
                    added.add(tool.name)

            segment_tools = final_tools

            print(
                f"DEBUG: Segment Tools → "
                f"{[tool.name for tool in segment_tools]}"
            )

            if not segment_tools:
                continue

            segment_entities = self.entity_extractor.extract(segment)

            segment_tasks = self.task_builder.build_tasks(
                segment,
                segment_tools,
                segment_entities,
            )

            print(f"DEBUG: Segment Tasks → {segment_tasks}")

            all_tasks.extend(segment_tasks)

        return all_tasks

    def _should_use_retriever(self, query: str, context=None) -> bool:
        """
        Determine whether web retrieval should be used for a query.

        Retrieval remains owned by the existing M6 retrieval policy.
        """

        decision = should_use_retrieval(
            requires_current_information=requires_current_information(query),
            explicit_search_request=has_explicit_search_request(query),
            context_available=has_retrieved_content(context),
        )

        return decision == RetrievalDecision.USE

"""
execution/context_dependency.py

Strict context dependency resolver with a shared context detection layer,
safe dependency injection, and deterministic ordering.
"""

from typing import List

from execution.context_signals import (
    is_document_loaded,
    has_retrieved_content,
)


class ContextDependencyResolver:
    def __init__(self, registry):
        self.registry = registry

    # =========================
    # 🚀 MAIN RESOLVE
    # =========================
    def resolve(self, steps: List, context) -> List:
        if not steps:
            return []

        resolved = []
        available = self._get_available_context(context)

        for step in steps:
            tool = self._get_tool(step)

            # =========================
            # 🔗 DEPENDENCY INJECTION
            # =========================
            if tool:
                required = getattr(tool, "requires_context", [])

                for ctx_type in required:
                    if ctx_type not in available:
                        producer = self._find_producer(ctx_type)

                        if producer:
                            injected = self._inject(step, producer, ctx_type)

                            if injected and not self._exists(injected, resolved):
                                print(f"[Resolver] Injecting {producer} for {ctx_type}")

                                resolved.append(injected)

                                # Context will exist after injected tool executes
                                available.add(ctx_type)

            # =========================
            # ➕ ADD ORIGINAL STEP
            # =========================
            resolved.append(step)

            # =========================
            # 📦 UPDATE AVAILABLE CONTEXT
            # =========================
            if tool:
                for produced in getattr(tool, "produces_context", []):
                    available.add(produced)

        return self._reorder(resolved)

    # =========================
    # 🧠 CONTEXT DETECTION
    # =========================
    def _get_available_context(self, context):
        """
        Build the set of currently available context types.

        Uses the shared context detection helpers so the resolver and
        ControlLayer always agree on what constitutes usable context.
        """
        if context is None:
            return set()

        available = set()

        # Document context
        if is_document_loaded(context):
            available.add("document")

        # Web retrieval context (NOT merely "something wrote into web")
        if has_retrieved_content(context):
            available.add("web")

        # Other context types continue using bucket presence.
        buckets = getattr(context, "_buckets", {})

        for ctx_type, data in buckets.items():
            if ctx_type in {"document", "web"}:
                continue

            if data:
                available.add(ctx_type)

        return available

    # =========================
    # 🔍 TOOL FETCH
    # =========================
    def _get_tool(self, step):
        action = getattr(step, "action", None)
        return self.registry.get(action) if action else None

    # =========================
    # 🔎 FIND PRODUCER
    # =========================
    def _find_producer(self, ctx_type: str):
        for tool in self.registry.list_tools():
            if ctx_type in getattr(tool, "produces_context", []):
                return tool.name
        return None

    # =========================
    # 🧠 SAFE INJECTION
    # =========================
    def _inject(self, dependent_step, producer_name, ctx_type):
        args = getattr(dependent_step, "args", {})

        new_args = {}

        if ctx_type == "web":
            new_args["query"] = args.get("query") or args.get("expression")

        elif ctx_type == "document":
            new_args["file_path"] = args.get("file_path")

        elif ctx_type == "calculation":
            new_args["expression"] = (
                args.get("expression") or args.get("query")
            )

        if not any(v is not None for v in new_args.values()):
            return None

        step_class = dependent_step.__class__

        try:
            return step_class(
                action=producer_name,
                args=new_args,
            )
        except Exception:
            return {
                "action": producer_name,
                "args": new_args,
            }

    # =========================
    # 🧠 DUPLICATE CHECK
    # =========================
    def _exists(self, step, steps):
        for s in steps:
            if getattr(s, "action", None) == getattr(step, "action", None):
                if getattr(s, "args", {}) == getattr(step, "args", {}):
                    return True
        return False

    # =========================
    # 🔥 FINAL ORDERING
    # =========================
    def _reorder(self, steps):
        priority = {
            "load_document": 1,
            "calculator": 1,
            "web_retriever": 2,
            "rag_search": 3,
            "explain": 4,
            "echo": 10,
        }

        return sorted(
            steps,
            key=lambda s: priority.get(
                getattr(s, "action", ""),
                5,
            ),
        )

    # =========================
    # 🎯 CONTEXT RANKING
    # =========================
    def rank_context(
        self,
        query: str,
        context_items: list,
        top_k: int = 3,
    ):
        if not context_items:
            return []

        scored = []

        for item in context_items:
            score = self._simple_score(query, item)
            scored.append((item, score))

        scored.sort(
            key=lambda x: x[1],
            reverse=True,
        )

        return [item for item, _ in scored[:top_k]]

    def _simple_score(self, query: str, text: str):
        q_words = set(query.lower().split())
        t_words = set(text.lower().split())

        overlap = len(q_words & t_words)
        return overlap / (len(q_words) + 1)
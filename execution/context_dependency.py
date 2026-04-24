"""
execution/context_dependency.py

Strict context dependency resolver with correct context detection,
safe injection, and deterministic ordering.
"""

from typing import List


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

                                # 🔥 INSERT BEFORE dependent step
                                resolved.append(injected)

                                # mark as available AFTER injection
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

        # =========================
        # 🔥 FINAL ORDERING (CRITICAL)
        # =========================
        resolved = self._reorder(resolved)

        return resolved

    # =========================
    # 🧠 CONTEXT DETECTION (FIXED)
    # =========================
    def _get_available_context(self, context):
        if not context:
            return set()

        available = set()

        for ctx_type, data in context._buckets.items():
            if data:  # 🔥 ONLY if non-empty
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
    # 🧠 SAFE INJECTION (FIXED)
    # =========================
    def _inject(self, dependent_step, producer_name, ctx_type):
        args = getattr(dependent_step, "args", {})

        new_args = {}

        # 🔥 CONTEXT-SPECIFIC ARG MAPPING
        if ctx_type == "web":
            new_args["query"] = args.get("query") or args.get("expression")

        elif ctx_type == "document":
            new_args["file_path"] = args.get("file_path")

        elif ctx_type == "calculation":
            new_args["expression"] = args.get("expression") or args.get("query")

        # safety: skip invalid injection
        if not new_args:
            return None

        step_class = dependent_step.__class__

        try:
            return step_class(action=producer_name, args=new_args)
        except:
            return {"action": producer_name, "args": new_args}

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
    # 🔥 FINAL ORDERING (NEW)
    # =========================
    def _reorder(self, steps):
        priority = {
            "load_document": 1,
            "calculator": 1,
            "web_retriever": 2,
            "rag_search": 3,
            "explain": 4,
            "echo": 10
        }

        return sorted(
            steps,
            key=lambda s: priority.get(getattr(s, "action", ""), 5)
        )

    # =========================
    # 🎯 CONTEXT RANKING (READY)
    # =========================
    def rank_context(self, query: str, context_items: list, top_k: int = 3):
        if not context_items:
            return []

        scored = []

        for item in context_items:
            score = self._simple_score(query, item)
            scored.append((item, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [item for item, _ in scored[:top_k]]

    def _simple_score(self, query: str, text: str):
        q_words = set(query.lower().split())
        t_words = set(text.lower().split())

        overlap = len(q_words & t_words)
        return overlap / (len(q_words) + 1)
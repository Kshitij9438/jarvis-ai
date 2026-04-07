from planner.schema import Plan


class PlanScorer:
    def __init__(self, registry=None):
        self.registry = registry  # 🧠 NEW — tool-aware

    # =========================
    # 🧠 MAIN ENTRY
    # =========================
    def score(self, plan: Plan, intents: list = None) -> dict:
        return {
            "completeness": self._score_completeness(plan, intents),
            "minimality": self._score_minimality(plan),
            "validity": self._score_validity(plan),
            "coherence": self._score_coherence(plan),
            "total": 0
        } | self._finalize(plan, intents)

    # =========================
    # ✅ COMPLETENESS
    # =========================
    def _score_completeness(self, plan: Plan, intents: list) -> float:
        if not intents:
            return 1.0

        actions = {s.action for s in plan.steps}

        # 🧠 no more intent_map — direct matching
        covered = sum(1 for intent in intents if intent in actions)

        return covered / len(intents)

    # =========================
    # 🧹 MINIMALITY
    # =========================
    def _score_minimality(self, plan: Plan) -> float:
        seen = set()
        duplicates = 0

        for step in plan.steps:
            key = (step.action, str(step.args))

            if key in seen:
                duplicates += 1
            else:
                seen.add(key)

        if not plan.steps:
            return 1.0

        return 1.0 - (duplicates / len(plan.steps))

    # =========================
    # ⚙️ VALIDITY (TOOL-SCHEMA DRIVEN)
    # =========================
    def _score_validity(self, plan: Plan) -> float:
        if not plan.steps:
            return 1.0

        valid = 0

        for step in plan.steps:
            tool = self.registry.get(step.action) if self.registry else None

            # 🧠 validate using tool schema
            if tool and tool.args_schema:
                try:
                    tool.args_schema(**step.args)
                    valid += 1
                except Exception:
                    pass
            else:
                # unknown tool → allow
                valid += 1

        return valid / len(plan.steps)

    # =========================
    # 🔄 COHERENCE (LIGHTWEIGHT)
    # =========================
    def _score_coherence(self, plan: Plan) -> float:
        actions = [s.action for s in plan.steps]

        score = 1.0

        # simple ordering heuristics (tool-agnostic)
        if "explain" in actions and "open_website" in actions:
            if actions.index("explain") < actions.index("open_website"):
                score -= 0.2

        # basic dependency awareness
        if "rag_search" in actions and "load_document" not in actions:
            for step in plan.steps:
                if step.action == "rag_search":
                    query = step.args.get("query", "")
                    if "document" in query:
                        score -= 0.3

        return max(score, 0)

    # =========================
    # 🧠 FINAL AGGREGATION
    # =========================
    def _finalize(self, plan: Plan, intents: list):
        c = self._score_completeness(plan, intents)
        m = self._score_minimality(plan)
        v = self._score_validity(plan)
        h = self._score_coherence(plan)

        total = (c * 0.35) + (m * 0.2) + (v * 0.25) + (h * 0.2)

        return {
            "completeness": c,
            "minimality": m,
            "validity": v,
            "coherence": h,
            "total": round(total, 3)
        }
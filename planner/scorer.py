from planner.schema import Plan


class PlanScorer:
    def __init__(self):
        pass

    # =========================
    # 🧠 MAIN ENTRY
    # =========================
    def score(self, plan: Plan, intents: list = None) -> dict:
        """
        Returns detailed score breakdown.
        """

        return {
            "completeness": self._score_completeness(plan, intents),
            "minimality": self._score_minimality(plan),
            "validity": self._score_validity(plan),
            "coherence": self._score_coherence(plan),
            "total": 0  # filled below
        } | self._finalize(plan, intents)

    # =========================
    # ✅ COMPLETENESS
    # =========================
    def _score_completeness(self, plan: Plan, intents: list) -> float:
        if not intents:
            return 1.0  # cannot judge

        actions = [s.action for s in plan.steps]

        coverage = 0

        intent_map = {
            "open_website": "open_website",
            "explain": "explain",
            "summarize": "rag_search",
            "load_document": "load_document"
        }

        for intent in intents:
            expected_action = intent_map.get(intent)

            if expected_action in actions:
                coverage += 1

        return coverage / len(intents)

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
    # ⚙️ VALIDITY
    # =========================
    def _score_validity(self, plan: Plan) -> float:
        valid = 0

        for step in plan.steps:
            if step.action == "open_website":
                if step.args.get("url"):
                    valid += 1

            elif step.action in ["explain", "rag_search"]:
                if step.args.get("query"):
                    valid += 1

            elif step.action == "load_document":
                if step.args.get("file_path"):
                    valid += 1

            else:
                valid += 1  # unknown tools allowed

        if not plan.steps:
            return 1.0

        return valid / len(plan.steps)

    # =========================
    # 🔄 COHERENCE
    # =========================
    def _score_coherence(self, plan: Plan) -> float:
        actions = [s.action for s in plan.steps]

        # simple rule-based scoring
        score = 1.0

        # explain before open? slight penalty
        if "explain" in actions and "open_website" in actions:
            if actions.index("explain") < actions.index("open_website"):
                score -= 0.2

        # summarize without load? penalty
        if "rag_search" in actions and "load_document" not in actions:
        # Only penalize if query implies document usage
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
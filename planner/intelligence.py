from planner.schema import Plan, Action


class PlannerIntelligence:
    def __init__(self):
        pass

    # =========================
    # 🧠 MAIN ENTRY
    # =========================
    def refine(self, plan: Plan) -> Plan:
        """
        Entry point for intelligence layer.
        Keeps fast path fast, refines only when needed.
        """

        if self._is_high_confidence(plan):
            return plan  # ⚡ fast path

        return self._refine_plan(plan)

    # =========================
    # 🔍 CONFIDENCE CHECK
    # =========================
    def _is_high_confidence(self, plan: Plan) -> bool:
        steps = plan.steps

        if not steps:
            return True

        if len(steps) == 1:
            return True

        actions = [s.action for s in steps]

        # ✅ Mixed meaningful actions → already good
        if "open_website" in actions and "explain" in actions:
            return True

        # ✅ same-type simple actions
        if len(set(actions)) == 1 and len(steps) <= 2:
            return True

        return False

    # =========================
    # 🧠 PLAN REFINEMENT
    # =========================
    def _refine_plan(self, plan: Plan) -> Plan:
        steps = plan.steps

        # 🔥 Step 1: reorder logically
        steps = self._reorder_for_logic(steps)

        # 🔥 Step 2: conservative cleanup
        steps = self._remove_weak_steps(steps)

        return Plan(steps=steps)

    # =========================
    # 🔄 REORDERING
    # =========================
    def _reorder_for_logic(self, steps):
        priority = {
            "open_website": 1,
            "load_document": 2,
            "rag_search": 3,
            "summarize": 3,
            "explain": 4,
        }

        return sorted(steps, key=lambda s: priority.get(s.action, 5))

    # =========================
    # 🧹 SAFE CLEANUP (FIXED)
    # =========================
    def _remove_weak_steps(self, steps):
        """
        Conservative cleanup:
        ONLY remove truly useless steps.
        NEVER remove meaningful ones.
        """
        cleaned = []

        for step in steps:
            if step.action == "explain":
                query = step.args.get("query", "").strip()

                # ❌ remove only completely useless queries
                if not query or query in {"explain", "something"}:
                    continue

            cleaned.append(step)

        return cleaned
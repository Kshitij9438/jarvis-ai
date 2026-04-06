from planner.schema import Plan, Action
import copy


class PlanVariants:
    def __init__(self):
        pass

    # =========================
    # 🧠 MAIN ENTRY
    # =========================
    def generate(self, plan: Plan) -> list[Plan]:
        variants = []

        # A → original
        variants.append(plan)

        # B → reordered
        reordered = self._reorder_variant(plan)
        if reordered:
            variants.append(reordered)

        # C → simplified
        simplified = self._simplify_variant(plan)
        if simplified:
            variants.append(simplified)

        return variants

    # =========================
    # 🔄 REORDER VARIANT
    # =========================
    def _reorder_variant(self, plan: Plan):
        steps = copy.deepcopy(plan.steps)

        priority = {
            "open_website": 1,
            "load_document": 2,
            "rag_search": 3,
            "summarize": 3,
            "explain": 4,
        }

        sorted_steps = sorted(steps, key=lambda s: priority.get(s.action, 5))

        if sorted_steps != steps:
            return Plan(steps=sorted_steps)

        return None

    # =========================
    # 🧹 SIMPLIFY VARIANT
    # =========================
    def _simplify_variant(self, plan: Plan):
        seen = set()
        new_steps = []

        for step in plan.steps:
            key = (step.action, str(step.args))

            if key not in seen:
                seen.add(key)
                new_steps.append(step)

        if len(new_steps) != len(plan.steps):
            return Plan(steps=new_steps)

        return None
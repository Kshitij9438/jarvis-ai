from planner.schema import Plan
from planner.scorer import PlanScorer
from planner.plan_variants import PlanVariants


class PlannerIntelligence:
    def __init__(self):
        self.scorer = PlanScorer()
        self.variants = PlanVariants()

    # =========================
    # 🧠 MAIN ENTRY
    # =========================
    def refine(self, plan: Plan, intents=None) -> Plan:
        """
        Score-guided refinement.
        """

        # 🔥 Generate variants
        candidates = self.variants.generate(plan)

        best_plan = plan
        best_score = self.scorer.score(plan, intents)["total"]

        print(f"DEBUG: Base Score → {best_score}")

        # 🔥 Evaluate alternatives
        for candidate in candidates:
            score = self.scorer.score(candidate, intents)["total"]

            print(f"DEBUG: Candidate Score → {score} | {candidate}")

            if score > best_score:
                best_score = score
                best_plan = candidate

        return best_plan
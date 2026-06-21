"""
control/execution_loop.py

Drives execute → evaluate → (repair → execute)* until the goal is
satisfied, a confidence threshold is hit, or attempts run out.

Repair strategy (current): SUBTRACTIVE ONLY.
  - Drops steps whose execution failed.
  - Keeps steps that succeeded (so we never re-run side effects like
    open_website or re-do a load_document that already worked).
  - Never invents new steps, never calls the LLM, never re-plans.

This means repair can only ever shrink a plan. It cannot fix a bad
query or recover a step that failed for a correctable reason — it
can only cut losses. That's a deliberate, temporary limitation:
LLM-based re-planning (feeding failure context back into Planner.plan)
is a planned follow-up, not implemented here. Don't be surprised when
a fixable failure (e.g. a malformed query) just gets dropped instead
of corrected — that's expected at this stage, not a bug.
"""

from copy import deepcopy
from typing import List, Optional

from planner.schema import Plan, Action
from control.evaluator import Evaluator, EvaluationResult


class ExecutionLoop:
    def __init__(self, executor):
        self.executor = executor
        self.evaluator = Evaluator()

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def run(self, plan: Plan, context, max_attempts: int = 2) -> List[dict]:
        """
        Execute `plan`, evaluate the outcome, and retry with a
        subtractively-repaired plan if the result is weak.

        Returns the results list from whichever attempt is returned —
        always the dict-shaped results coming out of Executor.execute.
        """
        if plan is None or not getattr(plan, "steps", None):
            print("[ExecutionLoop] Empty/None plan — nothing to execute.")
            return []

        current_plan = plan
        last_results: List[dict] = []
        last_eval: Optional[EvaluationResult] = None

        for attempt in range(1, max_attempts + 1):
            print(f"\n🚀 Attempt {attempt}/{max_attempts}")

            results = self.executor.execute(current_plan, context)
            last_results = results

            eval_result = self.evaluator.evaluate(
                context.goal,
                current_plan,
                results
            )
            last_eval = eval_result

            print("🧠 Evaluation:", eval_result)

            # ---- STRONG SUCCESS → stop ----
            if eval_result.success and eval_result.confidence >= 0.75:
                return results

            # ---- PARTIAL SUCCESS → accept, stop ----
            if eval_result.confidence >= 0.6:
                print("⚠️ Accepting partial success (no retry)")
                return results

            # ---- Out of attempts → stop here, don't bother repairing ----
            if attempt >= max_attempts:
                break

            # ---- Weak result and attempts remain → attempt repair ----
            repaired_plan = self._repair_plan(current_plan, results)

            if repaired_plan is None:
                print("⚠️ Nothing to repair (no failed steps identifiable) — stopping")
                return results

            if not repaired_plan.steps:
                print("⚠️ Repair would produce an empty plan — stopping")
                return results

            if self._same_plan(repaired_plan, current_plan):
                print("⚠️ Repair made no changes — stopping")
                return results

            print(f"🔧 Plan repaired: {len(current_plan.steps)} → {len(repaired_plan.steps)} steps")
            current_plan = repaired_plan

        print("⚠️ Max attempts reached — returning last results")
        if last_eval is not None:
            print(f"   final evaluation: {last_eval}")
        return last_results

    # ------------------------------------------------------------------
    # REPAIR — SUBTRACTIVE ONLY
    # ------------------------------------------------------------------

    def _repair_plan(self, plan: Plan, results: List[dict]) -> Optional[Plan]:
        """
        Drop steps that failed; keep steps that succeeded.

        Matching failed steps back to plan actions is done by POSITION,
        not by action name — Executor.execute() returns one result dict
        per step in plan.steps, in the same order, even for duplicate
        action names (e.g. two web_retriever calls with different
        queries). Matching by action name alone would incorrectly drop
        BOTH if only one failed. Position-based matching avoids that.

        Returns:
          - a new Plan with only the previously-successful steps, or
          - None if `results` doesn't line up with `plan.steps` (can't
            safely identify what failed), or if nothing failed at all
            (in which case there's nothing to repair).
        """
        if not results or len(results) != len(plan.steps):
            # Can't safely correlate results to steps positionally.
            # This happens if execution stopped early (step-limit guard
            # in Executor) — results will be shorter than plan.steps.
            print("[Repair] results/steps length mismatch — cannot repair safely.")
            return None

        kept_steps = []
        any_failed = False

        for step, result in zip(plan.steps, results):
            succeeded = isinstance(result, dict) and result.get("success") is True

            if succeeded:
                kept_steps.append(step)
            else:
                any_failed = True
                reason = result.get("error") if isinstance(result, dict) else "unknown"
                print(f"[Repair] dropping failed step: {step.action} ({reason})")

        if not any_failed:
            # Nothing actually failed — low confidence came from weak
            # *content* (e.g. evaluator's heuristic/LLM judged the
            # output insufficient), not from a step-level failure.
            # Subtractive repair has nothing to act on here.
            return None

        return Plan(steps=deepcopy(kept_steps))

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _same_plan(self, a: Plan, b: Plan) -> bool:
        """
        Structural equality check. Plan/Action are pydantic BaseModels,
        so direct `==` already compares field values rather than
        identity — but kept as a named helper since "what counts as the
        same plan" is a decision point, not an accident, if Plan/Action
        gain non-comparable fields later.
        """
        if len(a.steps) != len(b.steps):
            return False
        return all(
            sa.action == sb.action and sa.args == sb.args
            for sa, sb in zip(a.steps, b.steps)
        )
"""
control/evaluator.py

Judges whether a plan's execution actually satisfied the user's goal.

Three-tier evaluation, cheapest first:
  1. Heuristic score from structured step results (no LLM call).
  2. If heuristic is high/low confidence → trust it, return immediately.
  3. If heuristic is borderline → ask the LLM to reflect on goal vs
     results, and use that verdict (falling back to heuristic if the
     LLM is unavailable or returns something unparseable).

This file does NOT decide what to do about a bad evaluation (retry,
repair, give up) — that's ExecutionLoop's job. Evaluator only judges.
"""

from typing import List, Optional
from brain.llm import LLM


# Heuristic score thresholds — kept as named constants so ExecutionLoop
# and Evaluator can't silently drift apart on what "borderline" means.
HIGH_CONFIDENCE_THRESHOLD = 0.8
LOW_CONFIDENCE_THRESHOLD = 0.3

# Minimum length for a step's result to count as "real" content rather
# than a stub/empty string that happened not to trip a failure signal.
MIN_RESULT_LENGTH = 5


class EvaluationResult:
    """
    Outcome of judging a plan's execution.

    `confidence` is always coerced to a float in [0.0, 1.0] at
    construction time — callers (e.g. ExecutionLoop's final fallback
    log, or any future caller) can format it with :.2f without needing
    to know which code path produced it.
    """

    def __init__(self, success: bool, confidence: float, reason: str):
        self.success = bool(success)
        self.confidence = self._coerce_confidence(confidence)
        self.reason = reason or "unknown"

    @staticmethod
    def _coerce_confidence(value) -> float:
        try:
            v = float(value)
        except (TypeError, ValueError):
            return 0.0
        if v < 0.0:
            return 0.0
        if v > 1.0:
            return 1.0
        return v

    def __repr__(self):
        return f"<Eval success={self.success} conf={self.confidence:.2f} reason={self.reason}>"


class Evaluator:
    def __init__(self):
        self.llm = LLM()

    # ------------------------------------------------------------------
    # MAIN ENTRY
    # ------------------------------------------------------------------

    def evaluate(self, goal: str, plan, results: List[dict]) -> EvaluationResult:
        heuristic_score = self._heuristic_score(results)
        print(f"[Evaluator] Heuristic score: {heuristic_score:.2f}")

        if heuristic_score >= HIGH_CONFIDENCE_THRESHOLD:
            return EvaluationResult(True, heuristic_score, "heuristic_success")

        if heuristic_score <= LOW_CONFIDENCE_THRESHOLD:
            return EvaluationResult(False, heuristic_score, "heuristic_failure")

        return self._llm_evaluate(goal, plan, results, heuristic_score)

    # ------------------------------------------------------------------
    # HEURISTIC SCORE
    # ------------------------------------------------------------------

    def _heuristic_score(self, results: List[dict]) -> float:
        """
        Fraction of steps that both reported success AND produced
        non-trivial content. A step marked success=True with an empty
        or near-empty result still counts against the score — "the
        tool didn't error" isn't the same claim as "the tool produced
        something useful."
        """
        if not results:
            return 0.0

        valid_results = [r for r in results if isinstance(r, dict)]

        if not valid_results:
            return 0.0

        success_count = 0

        for r in valid_results:
            if not r.get("success"):
                continue

            result_content = r.get("result")

            if result_content is None:
                continue

            text = str(result_content).strip()

            if len(text) < MIN_RESULT_LENGTH:
                continue

            success_count += 1

        return success_count / len(valid_results)

    # ------------------------------------------------------------------
    # LLM EVALUATION (borderline cases only)
    # ------------------------------------------------------------------

    def _llm_evaluate(self, goal, plan, results, base_score: float) -> EvaluationResult:
        reflection = None

        try:
            reflection = self.llm.generate_reflection(goal, plan, results)
        except Exception as e:
            print(f"[Evaluator] LLM error: {e}")
            return EvaluationResult(False, base_score, "llm_exception")

        if not reflection:
            return EvaluationResult(False, base_score, "llm_failed")

        status: Optional[str] = getattr(reflection, "status", None)
        if isinstance(status, str):
            status = status.strip().lower()

        # NOTE: LLM.generate_reflection's schema/system-prompt contract
        # specifies status is "success" or "fail" — NOT "failure".
        # Matching the wrong string here doesn't raise; it just silently
        # routes every genuine LLM failure verdict into "llm_uncertain"
        # instead of "llm_fail", which is exactly the kind of bug that
        # doesn't show up until you go looking for it.
        if status == "success":
            return EvaluationResult(True, max(base_score, 0.6), "llm_success")

        if status == "fail":
            return EvaluationResult(False, base_score, "llm_fail")

        # Unknown/missing status (e.g. LLM schema drifts in the future)
        # → fall back to the heuristic score rather than guessing.
        return EvaluationResult(base_score >= 0.5, base_score, "llm_uncertain")
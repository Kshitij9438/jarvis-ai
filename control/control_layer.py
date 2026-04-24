"""
control/control_layer.py

Drop-in control layer for the JARVIS AI agent system.
Sits between the Planner output and the Executor, refining plans
before execution with zero LLM calls — purely deterministic logic.

Usage (in main.py):
    from control.control_layer import ControlLayer
    control = ControlLayer()
    plan = control.refine_plan(plan, context)
"""

import os
import ast
import re
import operator
from copy import deepcopy
from typing import Optional

from planner.schema import Plan, Action


# =============================================================================
# CONSTANTS
# =============================================================================

# Tools that are meaningless without an actual topic / real query
QUERY_DEPENDENT_TOOLS = {"web_retriever", "rag_search", "explain", "calculator"}

# Filler / stop words — removed during query sanitization only
FILLER_WORDS = {
    "please", "can", "you", "could", "would", "me", "just", "a", "an",
    "the", "to", "i", "my", "for", "do", "that", "this", "it", "its",
    "tell", "show", "give", "help", "with",
}

# Queries that are too generic for web_retriever to be useful
GENERIC_WEB_QUERIES = {
    "applications", "information", "things", "stuff", "something",
    "anything", "everything", "details", "facts", "topic", "query",
    "search", "find", "look", "result", "results", "data",
}

# Queries that are meaningless regardless of tool
MEANINGLESS_QUERIES = {
    "explain", "summarize", "summary", "describe", "load", "open",
    "search", "find", "get", "fetch", "retrieve", "calculate", "compute",
    "", "none", "null",
}

# Execution-order priority for each tool (lower = runs earlier)
TOOL_ORDER_PRIORITY = {
    "open_website":  1,
    "load_document": 2,
    "calculator":    2,
    "web_retriever": 3,
    "rag_search":    4,
    "explain":       5,
    "echo":          9,
}

# AST operators allowed in safe expression evaluation
_SAFE_OPS = {
    ast.Add:  operator.add,
    ast.Sub:  operator.sub,
    ast.Mult: operator.mul,
    ast.Div:  operator.truediv,
    ast.Mod:  operator.mod,
    ast.Pow:  operator.pow,
    ast.USub: operator.neg,
}

# Explicit function whitelist — anything outside this is rejected
_ALLOWED_FUNCTIONS = {"sqrt", "log"}


# =============================================================================
# INTERNAL HELPERS
# =============================================================================

def _safe_eval(expr: str) -> bool:
    """Return True if `expr` is a valid, safe arithmetic expression."""
    try:
        tree = ast.parse(expr.strip(), mode="eval")
        _check_node(tree.body)
        return True
    except Exception:
        return False


def _check_node(node):
    """Recursively validate that an AST node is safe arithmetic."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return
    if isinstance(node, ast.Num):          # Python < 3.8 compat
        return
    if isinstance(node, ast.BinOp):
        if type(node.op) not in _SAFE_OPS:
            raise ValueError("Unsafe operator")
        _check_node(node.left)
        _check_node(node.right)
        return
    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in _SAFE_OPS:
            raise ValueError("Unsafe unary operator")
        _check_node(node.operand)
        return
    if isinstance(node, ast.Call):
        # Only explicitly whitelisted single-name functions are permitted.
        # This blocks __import__, exec, eval, and any other injection vector.
        if (
            isinstance(node.func, ast.Name)
            and node.func.id in _ALLOWED_FUNCTIONS
        ):
            for arg in node.args:
                _check_node(arg)
            return
        raise ValueError("Unsafe function call")
    raise ValueError(f"Unsafe AST node: {type(node)}")


def _sanitize_query(query: str) -> str:
    """
    Light-touch query sanitization.
    Only removes leading/trailing filler words and extra whitespace.
    Preserves semantic meaning completely.
    """
    if not query:
        return query

    words = query.strip().lower().split()

    # strip leading filler only (preserve middle/end for meaning)
    while words and words[0] in FILLER_WORDS:
        words = words[1:]

    result = " ".join(words).strip()
    return result if result else query.strip()


def _is_meaningful_query(query: Optional[str]) -> bool:
    """Return True if the query has real semantic content."""
    if not query:
        return False
    q = query.strip().lower()
    if q in MEANINGLESS_QUERIES:
        return False
    if len(q) < 3:
        return False
    # purely numeric / punctuation → not a text query
    if re.fullmatch(r"[\d\s\+\-\*\/\^\.\(\)%]+", q):
        return False
    return True


def _is_document_loaded(context) -> bool:
    """
    Heuristically determine whether a document has already been loaded
    by inspecting the execution context.
    """
    if context is None:
        return False

    # Explicit flag (future-proofing: callers may set context.document_loaded)
    if getattr(context, "document_loaded", False):
        return True

    # Check tool_outputs for any load_document output
    tool_outputs = getattr(context, "tool_outputs", {}) or {}
    if tool_outputs.get("document_loaded"):
        return True

    # Walk execution history
    history = getattr(context, "history", []) or []
    for entry in history:
        tool = entry.get("tool", "") if isinstance(entry, dict) else getattr(entry, "tool", "")
        if tool == "load_document":
            result = entry.get("result", "") if isinstance(entry, dict) else getattr(entry, "result", "")
            result_str = str(result).lower()
            # Consider loaded if result is not an error
            if not any(sig in result_str for sig in ("⚠️", "error", "failed", "not found")):
                return True

    return False


def _has_retrieved_content(context) -> bool:
    """Return True if the context already holds retrieved/search content."""
    if context is None:
        return False
    if getattr(context, "retrieved_content", None):
        return True
    tool_outputs = getattr(context, "tool_outputs", {}) or {}
    return bool(tool_outputs.get("retrieved_content") or tool_outputs.get("search_results"))


def _fallback_plan(goal: str) -> Plan:
    """
    Return a minimal safe plan when nothing valid survived validation.
    Prefers a concise explain step; falls back to echo.
    """
    clean = _sanitize_query(goal) if goal else ""
    if clean and _is_meaningful_query(clean):
        return Plan(steps=[
            Action(action="explain", args={"query": clean})
        ])
    return Plan(steps=[
        Action(action="echo", args={"text": f"I'm not sure how to help with: {goal or '?'}"})
    ])


# =============================================================================
# MAIN CLASS
# =============================================================================

class ControlLayer:
    """
    Deterministic plan refinement layer.

    Placed between the Planner and Executor, `refine_plan` inspects,
    validates, reorders, and sanitizes every Action in a Plan before
    execution — preventing hallucinated arguments, broken dependencies,
    irrelevant tool usage, and bad ordering.
    """

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def refine_plan(self, plan: Plan, context=None) -> Plan:
        """
        Main entry point.  Returns a corrected, ready-to-execute Plan.

        Pipeline:
          1. Context-aware pre-filtering (skip redundant work)
          2. Argument validation (paths, expressions, queries)
          3. Plan-level intent validation (weak/meaningless removal)
          4. Dependency enforcement (rag_search needs doc, etc.)
          5. Query sanitization (light filler removal)
          6. Deduplication
          7. Reordering (canonical execution order)
          8. Failure prevention (fallback when empty)
        """
        if plan is None or not plan.steps:
            return _fallback_plan(getattr(context, "goal", "") if context else "")

        goal = getattr(context, "goal", "") if context else ""

        # Work on a deep copy so we never mutate the original plan
        steps: list[Action] = deepcopy(plan.steps)

        # --- Stage 1: Context-aware skipping ---
        steps = self._apply_context_optimizations(steps, context)

        # --- Stage 2: Argument validation ---
        steps = self._validate_arguments(steps)

        # --- Stage 3: Intent / query validation ---
        steps = self._validate_intent(steps, goal)

        # --- Stage 4: Dependency enforcement ---
        steps = self._enforce_dependencies(steps, context)

        # --- Stage 5: Query sanitization ---
        steps = self._sanitize_queries(steps)

        # --- Stage 6: Deduplication ---
        steps = self._deduplicate(steps)

        # --- Stage 7: Reordering ---
        steps = self._reorder(steps)

        # --- Stage 8: Failure prevention ---
        if not steps:
            print("ControlLayer: No valid steps remain — using fallback plan.")
            return _fallback_plan(goal)

        return Plan(steps=steps)

    # ------------------------------------------------------------------
    # STAGE 1 — CONTEXT-AWARE OPTIMIZATIONS
    # ------------------------------------------------------------------

    def _apply_context_optimizations(
        self, steps: list[Action], context
    ) -> list[Action]:
        """
        Skip tools whose work is already done according to the context.

          • If retrieved_content already exists  → skip web_retriever
          • If document is already loaded        → skip load_document
        """
        if context is None:
            return steps

        has_retrieval = _has_retrieved_content(context)
        doc_loaded    = _is_document_loaded(context)

        refined = []
        for step in steps:
            if step.action == "web_retriever" and has_retrieval:
                print(f"ControlLayer [ctx-opt]: skipping web_retriever "
                      f"(retrieved_content already in context)")
                continue

            if step.action == "load_document" and doc_loaded:
                print(f"ControlLayer [ctx-opt]: skipping load_document "
                      f"(document already loaded in context)")
                continue

            refined.append(step)

        return refined

    # ------------------------------------------------------------------
    # STAGE 2 — ARGUMENT VALIDATION
    # ------------------------------------------------------------------

    def _validate_arguments(self, steps: list[Action]) -> list[Action]:
        """
        Per-tool argument validation.  Drops steps whose arguments are
        provably invalid before execution is attempted.

          load_document → file_path must exist on disk
          calculator    → expression must be valid arithmetic
          web_retriever → query must not be a known-generic placeholder
        """
        valid = []
        for step in steps:
            if step.action == "load_document":
                if not self._validate_load_document(step):
                    continue

            elif step.action == "calculator":
                if not self._validate_calculator(step):
                    continue

            elif step.action == "web_retriever":
                if not self._validate_web_retriever(step):
                    continue

            valid.append(step)

        return valid

    def _validate_load_document(self, step: Action) -> bool:
        args = step.args or {}
        path = args.get("file_path") or args.get("filepath") or ""
        path = str(path).strip().strip("'\"")

        if not path:
            print("ControlLayer [arg]: load_document removed — no file_path provided.")
            return False

        # Reject clearly hallucinated paths (placeholder strings)
        hallucination_patterns = [
            r"^/path/to/",
            r"^/your/",
            r"^<",
            r"^example",
            r"^placeholder",
            r"^none$",
            r"^null$",
            r"^file\.(?:pdf|txt|md)$",
        ]
        for pattern in hallucination_patterns:
            if re.match(pattern, path, re.IGNORECASE):
                print(f"ControlLayer [arg]: load_document removed — "
                      f"hallucinated file_path: '{path}'")
                return False

        if not os.path.exists(path):
            print(f"ControlLayer [arg]: load_document removed — "
                  f"file does not exist: '{path}'")
            return False

        return True

    def _validate_calculator(self, step: Action) -> bool:
        args = step.args or {}
        expr = str(args.get("expression", "")).strip()

        if not expr:
            print("ControlLayer [arg]: calculator removed — empty expression.")
            return False

        if not _safe_eval(expr):
            print(f"ControlLayer [arg]: calculator removed — "
                  f"invalid expression: '{expr}'")
            return False

        return True

    def _validate_web_retriever(self, step: Action) -> bool:
        args = step.args or {}
        query = str(args.get("query", "")).strip().lower()

        if not query:
            print("ControlLayer [arg]: web_retriever removed — empty query.")
            return False

        # Single-word generic queries are useless for web retrieval.
        # Multi-word phrases like "applications of transformers" are kept.
        if len(query.split()) == 1 and query in GENERIC_WEB_QUERIES:
            print(f"ControlLayer [arg]: web_retriever removed — "
                  f"query too generic: '{query}'")
            return False

        # Very short or all-stopword queries
        meaningful_words = [w for w in query.split() if w not in FILLER_WORDS]
        if len(meaningful_words) == 0:
            print(f"ControlLayer [arg]: web_retriever removed — "
                  f"no meaningful words in query: '{query}'")
            return False

        return True

    # ------------------------------------------------------------------
    # STAGE 3 — INTENT / QUERY VALIDATION
    # ------------------------------------------------------------------

    def _validate_intent(self, steps: list[Action], goal: str) -> list[Action]:
        """
        Remove steps that don't match the user's intent at all.

          • Tools that need a query but have none / a meaningless one
          • open_website without a valid URL
        """
        valid = []
        goal_lower = (goal or "").lower()

        for step in steps:
            action = step.action
            args   = step.args or {}

            # -- open_website: must have a real URL --
            if action == "open_website":
                url = str(args.get("url", "")).strip()
                if not url or not url.startswith("http"):
                    print(f"ControlLayer [intent]: open_website removed — "
                          f"no valid URL.")
                    continue

            # -- query-dependent tools: must have a meaningful query --
            elif action in QUERY_DEPENDENT_TOOLS:
                query = str(args.get("query", args.get("expression", ""))).strip()

                if not _is_meaningful_query(query):
                    print(f"ControlLayer [intent]: {action} removed — "
                          f"meaningless query: '{query}'")
                    continue

                # Extra guard: explain / web_retriever on a purely
                # greeting-like input ("hello", "hi", etc.)
                if action in {"explain", "web_retriever"}:
                    if self._is_greeting(goal_lower):
                        print(f"ControlLayer [intent]: {action} removed — "
                              f"input is a greeting, no retrieval needed.")
                        continue

            valid.append(step)

        return valid

    def _is_greeting(self, text: str) -> bool:
        """Return True if the entire user goal is a simple greeting."""
        greetings = {
            "hello", "hi", "hey", "howdy", "greetings",
            "good morning", "good afternoon", "good evening",
            "what's up", "whats up", "yo", "sup",
        }
        cleaned = text.strip().rstrip("!.,?").lower()
        return cleaned in greetings

    # ------------------------------------------------------------------
    # STAGE 4 — DEPENDENCY ENFORCEMENT
    # ------------------------------------------------------------------

    def _enforce_dependencies(
        self, steps: list[Action], context
    ) -> list[Action]:
        """
        Ensure dependency constraints are satisfied:

          • rag_search  requires a loaded document (context OR plan)
          • explain     should use web_retriever output when available
          • load_document must not be duplicated within the plan
        """
        actions = [s.action for s in steps]
        doc_loaded_in_context = _is_document_loaded(context)

        refined = []
        seen_load_document = False

        for step in steps:

            # ---- rag_search dependency check ----
            if step.action == "rag_search":
                plan_has_loader = "load_document" in actions
                if not plan_has_loader and not doc_loaded_in_context:
                    print("ControlLayer [dep]: rag_search removed — "
                          "no load_document in plan and no document in context.")
                    continue

            # ---- explain: promote to use retrieved content hint ----
            if step.action == "explain":
                if _has_retrieved_content(context):
                    retrieved = getattr(context, "retrieved_content", None)
                    if retrieved:
                        step = Action(
                            action=step.action,
                            args={**step.args, "context": retrieved}
                            )

            # ---- prevent duplicate load_document ----
            if step.action == "load_document":
                if seen_load_document:
                    print("ControlLayer [dep]: duplicate load_document removed.")
                    continue
                seen_load_document = True

            refined.append(step)

        return refined

    # ------------------------------------------------------------------
    # STAGE 5 — QUERY SANITIZATION
    # ------------------------------------------------------------------

    def _sanitize_queries(self, steps: list[Action]) -> list[Action]:
        """
        Lightly clean query strings — removes leading filler words only.
        Never rewrites the semantic intent of a query.
        """
        sanitized = []
        for step in steps:
            args = dict(step.args or {})

            if "query" in args and isinstance(args["query"], str):
                original = args["query"]
                cleaned  = _sanitize_query(original)
                if cleaned and cleaned != original:
                    print(f"ControlLayer [sanitize]: '{original}' → '{cleaned}'")
                args["query"] = cleaned or original

            sanitized.append(Action(action=step.action, args=args))

        return sanitized

    # ------------------------------------------------------------------
    # STAGE 6 — DEDUPLICATION
    # ------------------------------------------------------------------

    def _deduplicate(self, steps: list[Action]) -> list[Action]:
        """Remove exact duplicate (action, args) pairs."""
        seen   = set()
        unique = []

        for step in steps:
            key = (step.action, str(sorted(step.args.items())))
            if key not in seen:
                seen.add(key)
                unique.append(step)
            else:
                print(f"ControlLayer [dedup]: duplicate {step.action} removed.")

        return unique

    # ------------------------------------------------------------------
    # STAGE 7 — REORDERING
    # ------------------------------------------------------------------

    def _reorder(self, steps: list[Action]) -> list[Action]:
        """
        Sort steps into canonical execution order:

            open_website → load_document / calculator
                        → web_retriever
                        → rag_search
                        → explain
                        → echo (last resort)

        Stable sort: ties preserve original planner ordering.
        """
        return sorted(
            steps,
            key=lambda s: TOOL_ORDER_PRIORITY.get(s.action, 6)
        )
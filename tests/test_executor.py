"""
tests/test_executor.py

Tests against Executor's ACTUAL contract: execute() returns one dict
per step (or per step that was reached, see test_executor_step_limit),
shaped as:

    {"step": action_name, "success": bool, "result": Any, "error": str|None}

NOT bare strings. The previous version of this file asserted
`results == ["hello"]` — that was the contract of an EARLIER executor
implementation. The current executor/executor.py has never returned
bare strings; asserting against that shape was testing code that no
longer exists.
"""

from executor.executor import Executor
from tools.registry import ToolRegistry
from tools.basic_tools import EchoTool
from planner.schema import Action, Plan


def _make_registry_with_echo():
    registry = ToolRegistry()
    registry.register(EchoTool())
    return registry


def test_executor_single_step():
    registry = _make_registry_with_echo()
    executor = Executor(registry)

    plan = Plan(steps=[
        Action(action="echo", args={"text": "hello"})
    ])

    results = executor.execute(plan)

    assert len(results) == 1
    assert results[0]["step"] == "echo"
    assert results[0]["success"] is True
    assert results[0]["result"] == "hello"
    assert results[0]["error"] is None


def test_executor_multiple_steps():
    registry = _make_registry_with_echo()
    executor = Executor(registry)

    plan = Plan(steps=[
        Action(action="echo", args={"text": "hello"}),
        Action(action="echo", args={"text": "world"})
    ])

    results = executor.execute(plan)

    assert len(results) == 2
    assert [r["result"] for r in results] == ["hello", "world"]
    assert all(r["success"] is True for r in results)


def test_executor_missing_args():
    """
    EchoArgs requires `text`. Omitting it fails pydantic schema
    validation inside execute()'s isolated try/except — that's the
    "Schema validation failed" branch, not the outer runtime-error
    branch. The error message is intentionally generic (it doesn't
    leak the underlying pydantic ValidationError text to the caller);
    the full validation detail is only printed to stdout for debugging.
    """
    registry = _make_registry_with_echo()
    executor = Executor(registry)

    plan = Plan(steps=[
        Action(action="echo", args={})
    ])

    results = executor.execute(plan)

    assert len(results) == 1
    assert results[0]["step"] == "echo"
    assert results[0]["success"] is False
    assert results[0]["result"] is None
    assert results[0]["error"] == "Schema validation failed"


def test_executor_unknown_tool():
    registry = ToolRegistry()  # no tools registered
    executor = Executor(registry)

    plan = Plan(steps=[
        Action(action="fake_tool", args={})
    ])

    results = executor.execute(plan)

    assert len(results) == 1
    assert results[0]["step"] == "fake_tool"
    assert results[0]["success"] is False
    assert results[0]["result"] is None
    assert results[0]["error"] == "Unknown tool: fake_tool"


def test_executor_invalid_schema():
    """
    {"wrong": "data"} fails for the SAME reason as
    test_executor_missing_args, just reached a different way: pydantic
    v2's default extra-field policy is "ignore" (not "forbid"), so the
    unrecognized `wrong` key is silently dropped, not rejected — the
    validation failure comes entirely from `text` (EchoArgs' one
    required field) still being absent. Kept as a separate test from
    test_executor_missing_args because "supplied the wrong keys" and
    "supplied no keys" are different caller mistakes, even though they
    currently land in the same code branch for the same underlying
    reason (text missing either way).
    """
    registry = _make_registry_with_echo()
    executor = Executor(registry)

    plan = Plan(steps=[
        Action(action="echo", args={"wrong": "data"})
    ])

    results = executor.execute(plan)

    assert len(results) == 1
    assert results[0]["success"] is False
    assert results[0]["error"] == "Schema validation failed"


def test_executor_none_plan():
    """
    execute(None) has its own explicit early-return shape in
    executor.py, distinct from the "Unknown tool" and "Schema
    validation failed" branches — worth covering directly since it's
    a different code path, not just a variant of the others.
    """
    registry = _make_registry_with_echo()
    executor = Executor(registry)

    results = executor.execute(None)

    assert len(results) == 1
    assert results[0]["step"] is None
    assert results[0]["success"] is False
    assert results[0]["error"] == "No valid plan"


def test_executor_step_limit_guard():
    """
    When context.step_count has already reached context.max_steps
    before execute() starts, the guard breaks the loop immediately —
    so for a plan with N steps, the result list comes back SHORTER
    than N (zero results here, since the guard trips before step 0).

    This short-results behavior is deliberate (see Executor's class
    docstring) — control.execution_loop.ExecutionLoop._repair_plan
    relies on the length mismatch to detect "can't safely repair this."
    Asserting the short length here pins that contract so a future
    change to the guard doesn't silently break repair's safety check
    without a test failing to flag it.
    """
    class FakeContext:
        def __init__(self):
            self.step_count = 5
            self.max_steps = 5

    registry = _make_registry_with_echo()
    executor = Executor(registry)

    plan = Plan(steps=[
        Action(action="echo", args={"text": "hello"}),
        Action(action="echo", args={"text": "world"}),
    ])

    results = executor.execute(plan, context=FakeContext())

    assert results == []
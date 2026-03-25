from executor.executor import Executor
from tools.registry import ToolRegistry
from tools.basic_tools import EchoTool
from planner.schema import Action, Plan


def test_executor_single_step():
    registry = ToolRegistry()
    registry.register(EchoTool())

    executor = Executor(registry)

    plan = Plan(steps=[
        Action(action="echo", args={"text": "hello"})
    ])

    results = executor.execute(plan)

    assert results == ["hello"]


def test_executor_multiple_steps():
    registry = ToolRegistry()
    registry.register(EchoTool())

    executor = Executor(registry)

    plan = Plan(steps=[
        Action(action="echo", args={"text": "hello"}),
        Action(action="echo", args={"text": "world"})
    ])

    results = executor.execute(plan)

    assert results == ["hello", "world"]

def test_executor_missing_args():
    from executor.executor import Executor
    from tools.registry import ToolRegistry
    from tools.basic_tools import EchoTool
    from planner.schema import Action, Plan

    registry = ToolRegistry()
    registry.register(EchoTool())

    executor = Executor(registry)

    plan = Plan(steps=[
        Action(action="echo", args={})
    ])

    results = executor.execute(plan)

    # 🔥 Strict expectation
    assert results == ["⚠️ Missing or invalid arguments for echo"]

def test_executor_unknown_tool():
    from executor.executor import Executor
    from tools.registry import ToolRegistry
    from planner.schema import Action, Plan

    registry = ToolRegistry()  # No tools registered

    executor = Executor(registry)

    plan = Plan(steps=[
        Action(action="fake_tool", args={})
    ])

    results = executor.execute(plan)

    assert results == ["⚠️ Unknown tool: fake_tool"]

def test_executor_invalid_schema():
    from executor.executor import Executor
    from tools.registry import ToolRegistry
    from tools.basic_tools import EchoTool
    from planner.schema import Action, Plan

    registry = ToolRegistry()
    registry.register(EchoTool())

    executor = Executor(registry)

    plan = Plan(steps=[
        Action(action="echo", args={"wrong": "data"})
    ])

    results = executor.execute(plan)

    assert "⚠️ Missing or invalid arguments for echo" == results[0]
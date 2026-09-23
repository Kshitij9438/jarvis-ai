"""
tests/test_optimizer.py

Compatibility tests for the legacy planner.optimizer.TaskOptimizer
facade during the M7 migration.
"""

from planner.optimizer import TaskOptimizer
from planner.plan_optimizer import PlanOptimizer
from planner.task import Task


def test_task_optimizer_remains_a_plan_optimizer():
    assert issubclass(TaskOptimizer, PlanOptimizer)


def test_task_optimizer_preserves_legacy_behavior():
    optimizer = TaskOptimizer()

    tasks = [
        Task(
            type="explain",
            target=None,
            file_path=None,
            query="artificial intelligence",
        )
    ]

    optimized = optimizer.optimize(tasks)

    assert len(optimized) == 1
    assert optimized[0].query == "ai"

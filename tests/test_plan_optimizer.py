from unittest.mock import Mock

from planner.plan_optimizer import PlanOptimizer
from planner.task import Task


def test_plan_optimizer_delegates_to_legacy_optimizer():
    optimizer = Mock()
    optimizer.optimize.return_value = [
        Task("explain", query="git")
    ]

    plan_optimizer = PlanOptimizer(optimizer=optimizer)

    tasks = [Task("explain", query="git")]

    result = plan_optimizer.optimize(tasks)

    assert result == [Task("explain", query="git")]
    optimizer.optimize.assert_called_once_with(tasks)


def test_plan_optimizer_returns_empty_for_empty_tasks():
    optimizer = Mock()
    optimizer.optimize.return_value = []

    plan_optimizer = PlanOptimizer(optimizer=optimizer)

    assert plan_optimizer.optimize([]) == []
    optimizer.optimize.assert_called_once_with([])

from __future__ import annotations

from planner.optimizer import TaskOptimizer


class PlanOptimizer:
    """
    M7 planning boundary for plan optimization.

    This is the transitional boundary between Planner and the
    legacy TaskOptimizer implementation.

    M7 migration step:
    - exposes the PlanOptimizer ownership boundary;
    - preserves the existing optimization behavior;
    - delegates implementation to TaskOptimizer temporarily.

    The legacy optimizer will be migrated behind this boundary
    incrementally.
    """

    def __init__(self, optimizer: TaskOptimizer | None = None):
        self._optimizer = optimizer or TaskOptimizer()

    def optimize(self, tasks: list):
        return self._optimizer.optimize(tasks)

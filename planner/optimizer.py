from planner.plan_optimizer import PlanOptimizer


class TaskOptimizer(PlanOptimizer):
    """
    Backward-compatible facade for the legacy TaskOptimizer name.

    The optimization implementation now belongs to PlanOptimizer.
    This class remains temporarily so existing imports and callers
    continue to work during the incremental M7 migration.
    """

    pass

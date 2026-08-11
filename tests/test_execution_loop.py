import threading
from concurrent.futures import ThreadPoolExecutor

from control.execution_loop import ExecutionLoop
from planner.schema import Action, Plan


class FakeExecutor:
    def __init__(self, barrier):
        self.barrier = barrier

    def execute(self, plan, context):
        self.barrier.wait(timeout=5)

        return [
            {
                "success": True,
                "data": "ok",
            }
            for _ in plan.steps
        ]


class FakeEvaluator:
    def evaluate(self, goal, plan, results):
        class Result:
            success = True
            confidence = 1.0

        return Result()


class FakeContext:
    goal = "test"


def test_concurrent_execution_uses_request_local_event_callbacks():
    barrier = threading.Barrier(2)

    loop = ExecutionLoop(FakeExecutor(barrier))
    loop.evaluator = FakeEvaluator()

    plan = Plan(
        steps=[
            Action(
                action="test",
                args={},
            )
        ]
    )

    events_a = []
    events_b = []

    def callback_a(event_type, data):
        events_a.append(event_type)

    def callback_b(event_type, data):
        events_b.append(event_type)

    def run_a():
        return loop.run(
            plan,
            FakeContext(),
            event_callback=callback_a,
        )

    def run_b():
        return loop.run(
            plan,
            FakeContext(),
            event_callback=callback_b,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        future_a = pool.submit(run_a)
        future_b = pool.submit(run_b)

        future_a.result()
        future_b.result()

    expected_events = [
        "execution started",
        "attempt started",
        "attempt.executed",
        "evaluation completed",
        "execution.completed",
    ]

    assert events_a == expected_events
    assert events_b == expected_events
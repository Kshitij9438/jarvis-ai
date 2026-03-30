from planner.planner import Planner
from planner.schema import Plan


# =========================
# 🧪 TEST: PLANNER RETRY (NEW LLM API)
# =========================
def test_planner_retry(monkeypatch):
    class FakeRegistry:
        def list_tools(self):
            return []

    planner = Planner(FakeRegistry())

    calls = {"count": 0}

    def fake_generate_plan(user_input, schema, tool_info):
        calls["count"] += 1

        if calls["count"] == 1:
            return None  # ❌ first attempt fails
        else:
            return Plan(steps=[])  # ✅ second attempt succeeds

    # 🔥 Patch new method
    monkeypatch.setattr(planner.llm, "generate_plan", fake_generate_plan)

    plan = planner.plan("test")

    assert plan is not None
    assert isinstance(plan, Plan)
    assert calls["count"] == 2


# =========================
# 🧪 TEST: CONTROL LAYER PATH
# =========================
def test_control_layer_trigger(monkeypatch):
    class FakeRegistry:
        def list_tools(self):
            return []

    planner = Planner(FakeRegistry())

    # 🔥 Force intent to hit control layer
    monkeypatch.setattr(
        "planner.intent.classify_intent",
        lambda llm, user_input: ["open_website"]
    )

    plan = planner.plan("open youtube")

    assert plan is not None
    assert len(plan.steps) > 0
    assert plan.steps[0].action == "open_website"


# =========================
# 🧪 TEST: LLM FALLBACK PATH
# =========================
def test_llm_fallback(monkeypatch):
    class FakeRegistry:
        def list_tools(self):
            return []

    planner = Planner(FakeRegistry())

    # 🔥 Force no control-layer trigger
    monkeypatch.setattr(
        "planner.intent.classify_intent",
        lambda llm, user_input: ["general"]
    )

    def fake_generate_plan(user_input, schema, tool_info):
        return Plan(steps=[{"action": "echo", "args": {"text": "hi"}}])

    monkeypatch.setattr(planner.llm, "generate_plan", fake_generate_plan)

    plan = planner.plan("random input")

    assert plan is not None
    assert plan.steps[0].action == "echo"
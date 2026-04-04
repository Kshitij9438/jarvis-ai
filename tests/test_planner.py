def test_dedup_and_normalization():
    from planner.planner import Planner

    class FakeRegistry:
        def list_tools(self):
            return []

    planner = Planner(FakeRegistry())

    plan = planner.plan("open github and open github and explain git and explain git again")

    assert len(plan.steps) == 2

    actions = [step.action for step in plan.steps]
    assert "open_website" in actions
    assert "explain" in actions

def test_entity_extraction_multiple():
    from planner.planner import Planner

    class FakeRegistry:
        def list_tools(self):
            return []

    planner = Planner(FakeRegistry())

    plan = planner.plan("open github and open youtube")

    urls = [step.args["url"] for step in plan.steps if step.action == "open_website"]

    assert "https://github.com" in urls
    assert "https://youtube.com" in urls

def test_validator_no_fake_load():
    from planner.planner import Planner

    class FakeRegistry:
        def list_tools(self):
            return []

    planner = Planner(FakeRegistry())

    plan = planner.plan("summarize this")

    actions = [step.action for step in plan.steps]

    # ❌ should NOT inject load_document(None)
    assert "load_document" not in actions

def test_invalid_website_filtered():
    from planner.planner import Planner

    class FakeRegistry:
        def list_tools(self):
            return []

    planner = Planner(FakeRegistry())

    plan = planner.plan("open website with no url")

    # ✅ Case 1: empty plan (ideal)
    if len(plan.steps) == 0:
        assert True
        return

    # ✅ Case 2: if steps exist, they must be valid open_website actions
    for step in plan.steps:
        if step.action == "open_website":
            assert "url" in step.args
            assert step.args["url"].startswith("http")

def test_empty_explain():
    from planner.planner import Planner

    class FakeRegistry:
        def list_tools(self):
            return []

    planner = Planner(FakeRegistry())

    plan = planner.plan("explain")

    # should not produce meaningless explain
    assert len(plan.steps) == 0 or plan.steps[0].args["query"] != "explain"

def test_full_pipeline_complex():
    from planner.planner import Planner

    class FakeRegistry:
        def list_tools(self):
            return []

    planner = Planner(FakeRegistry())

    plan = planner.plan(
        "open github and github, then explain git and explain git again, and also open youtube"
    )

    actions = [step.action for step in plan.steps]

    assert "open_website" in actions
    assert "explain" in actions
    assert len(plan.steps) == 3  # github + youtube + explain


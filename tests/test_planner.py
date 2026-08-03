from planner.planner import Planner

class FakeRegistry:
    def __init__(self):
        from tools.basic_tools import OpenWebsiteTool, EchoTool
        from tools.explain_tool import ExplainTool
        from tools.load_doc_tool import LoadDocTool

        open_web = OpenWebsiteTool()
        open_web.requires_context = []
        open_web.produces_context = []

        explain = ExplainTool()
        explain.requires_context = []
        explain.produces_context = []

        self.tools = {
            "open_website": open_web,
            "explain": explain,
            "echo": EchoTool(),
            "load_document": LoadDocTool(None)
        }

    def get(self, name):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.values())


def test_dedup_and_normalization():
    planner = Planner(FakeRegistry())

    plan = planner.plan("open github and open github and explain git and explain git again")

    assert len(plan.steps) == 2

    actions = [step.action for step in plan.steps]
    assert "open_website" in actions
    assert "explain" in actions


def test_entity_extraction_multiple():
    planner = Planner(FakeRegistry())

    plan = planner.plan("open github and open youtube")

    urls = [step.args["url"] for step in plan.steps if step.action == "open_website"]

    assert "https://github.com" in urls
    assert "https://youtube.com" in urls


def test_validator_no_fake_load():
    planner = Planner(FakeRegistry())

    plan = planner.plan("summarize this")

    actions = [step.action for step in plan.steps]

    # ❌ should NOT inject load_document(None)
    assert "load_document" not in actions


def test_invalid_website_filtered():
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
    planner = Planner(FakeRegistry())

    plan = planner.plan("explain")

    # should not produce meaningless explain
    assert len(plan.steps) == 0 or "query" not in plan.steps[0].args or plan.steps[0].args["query"] != "explain"


def test_full_pipeline_complex():
    planner = Planner(FakeRegistry())

    plan = planner.plan(
        "open github and github, then explain git and explain git again, and also open youtube"
    )

    actions = [step.action for step in plan.steps]

    assert "open_website" in actions
    assert "explain" in actions
    assert len(plan.steps) == 4  # open_website (github) + explain (github) + explain (git) + open_website (youtube)

def test_trivial_input_returns_echo():
    planner = Planner(FakeRegistry())

    plan = planner.plan("hello")

    assert len(plan.steps) == 1
    assert plan.steps[0].action == "echo"

def test_empty_input():
    planner = Planner(FakeRegistry())

    plan = planner.plan("")

    assert len(plan.steps) == 1
    assert plan.steps[0].action == "echo"

def test_every_step_has_action():
    planner = Planner(FakeRegistry())

    plan = planner.plan("open github and explain git")

    for step in plan.steps:
        assert step.action
        assert isinstance(step.args, dict)
    
def test_same_input_same_plan():
    planner = Planner(FakeRegistry())

    p1 = planner.plan("open github and explain git")
    p2 = planner.plan("open github and explain git")

    assert p1 == p2
def test_duplicate_commands_removed():
    planner = Planner(FakeRegistry())

    plan = planner.plan(
        "open github and open github and open github"
    )

    opens = [s for s in plan.steps if s.action == "open_website"]

    assert len(opens) == 1
def test_segment_order_preserved():
    planner = Planner(FakeRegistry())

    plan = planner.plan(
        "open github then explain git"
    )

    actions = [s.action for s in plan.steps]

    assert actions == [
        "open_website",
        "explain",
    ]

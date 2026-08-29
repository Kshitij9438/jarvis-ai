from planner.planner import Planner


class FakeRegistry:
    def __init__(self):
        from tools.basic_tools import OpenWebsiteTool, EchoTool
        from tools.explain_tool import ExplainTool
        from tools.load_doc_tool import LoadDocTool
        from tools.web_retriever_tool import WebRetrieverTool
        from brain.llm import LLM

        open_web = OpenWebsiteTool()
        open_web.requires_context = []
        open_web.produces_context = []

        explain = ExplainTool()
        explain.requires_context = []
        explain.produces_context = []

        web_retriever = WebRetrieverTool(LLM())
        web_retriever.requires_context = []
        web_retriever.produces_context = ["web"]

        self.tools = {
            "open_website": open_web,
            "explain": explain,
            "web_retriever": web_retriever,
            "echo": EchoTool(),
            "load_document": LoadDocTool(None),
        }

    def get(self, name):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.values())


def has_web_retriever(plan):
    return any(
        step.action == "web_retriever"
        for step in plan.steps
    )


def test_explain_and_describe_have_same_retrieval_behavior():
    planner = Planner(FakeRegistry())

    explain_plan = planner.plan("explain transformers")
    describe_plan = planner.plan("describe transformers")

    assert has_web_retriever(explain_plan) == has_web_retriever(
        describe_plan
    )


def test_latest_information_requires_retrieval():
    planner = Planner(FakeRegistry())

    plan = planner.plan(
        "explain the latest transformer architectures"
    )

    assert has_web_retriever(plan)


def test_recent_information_requires_retrieval():
    planner = Planner(FakeRegistry())

    plan = planner.plan(
        "describe recent transformer architectures"
    )

    assert has_web_retriever(plan)


def test_explicit_search_request_requires_retrieval():
    planner = Planner(FakeRegistry())

    plan = planner.plan(
        "search the web for transformer applications"
    )

    assert has_web_retriever(plan)

def test_retrieval_policy_does_not_depend_on_explain_keyword():
    planner = Planner(FakeRegistry())

    assert planner._should_use_retriever("explain transformers") == \
        planner._should_use_retriever("describe transformers")

def test_architecture_keyword_does_not_automatically_trigger_retrieval():
    planner = Planner(FakeRegistry())

    assert planner._should_use_retriever(
        "describe transformer architecture"
    ) is False

def test_latest_changes_retrieval_decision():
    planner = Planner(FakeRegistry())

    normal_plan = planner.plan(
        "describe transformer architecture"
    )

    latest_plan = planner.plan(
        "describe the latest transformer architecture"
    )

    assert not has_web_retriever(normal_plan)
    assert has_web_retriever(latest_plan)

def test_explicit_search_changes_retrieval_decision():
    planner = Planner(FakeRegistry())

    normal_plan = planner.plan(
        "describe transformer applications"
    )

    search_plan = planner.plan(
        "search the web for transformer applications"
    )

    assert has_web_retriever(search_plan)
def test_neutral_wording_produces_same_retrieval_decision():
    planner = Planner(FakeRegistry())

    explain_plan = planner.plan(
        "explain transformers"
    )

    describe_plan = planner.plan(
        "describe transformers"
    )

    assert has_web_retriever(explain_plan) == has_web_retriever(
        describe_plan
    )

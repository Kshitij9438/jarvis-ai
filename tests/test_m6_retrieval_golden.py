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


def test_explain_does_not_force_web_retrieval():
    planner = Planner(FakeRegistry())

    plan = planner.plan("explain transformers")

    assert not has_web_retriever(plan)


def test_latest_information_uses_web_retrieval():
    planner = Planner(FakeRegistry())

    plan = planner.plan(
        "explain the latest transformer architectures"
    )

    assert has_web_retriever(plan)


def test_explicit_search_uses_web_retrieval():
    planner = Planner(FakeRegistry())

    plan = planner.plan(
        "search the web for transformer applications"
    )

    assert has_web_retriever(plan)


def test_neutral_wording_does_not_change_retrieval_policy():
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
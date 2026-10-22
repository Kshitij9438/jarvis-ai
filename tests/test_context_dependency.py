from execution.context import ExecutionContext
from execution.context_dependency import ContextDependencyResolver
from planner.schema import Action
from tools.basic_tools import OpenWebsiteTool
from tools.explain_tool import ExplainTool


class FakeRegistry:
    def get(self, name):
        return {
            "explain": ExplainTool,
            "open_website": OpenWebsiteTool,
        }.get(name)

    def list_tools(self):
        return [OpenWebsiteTool, ExplainTool]


def test_explain_without_web_context_does_not_inject_website():
    resolver = ContextDependencyResolver(FakeRegistry())
    context = ExecutionContext("explain transformers")

    steps = resolver.resolve(
        [Action(action="explain", args={"query": "transformers"})],
        context,
    )

    assert [step.action for step in steps] == ["explain"]

from tools.semantic_matcher import SemanticMatcher


class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.semantic = SemanticMatcher()

    def register(self, tool):
        self.tools[tool.name] = tool
        self.semantic.register_tool(tool)

    def get(self, name):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.values())


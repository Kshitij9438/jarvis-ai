from tools.semantic_matcher import SemanticMatcher


class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.semantic = SemanticMatcher()  # 🔥 new

    def register(self, tool):
        self.tools[tool.name] = tool

        # 🔥 register tool for semantic matching
        self.semantic.register_tool(tool)

    def get(self, name):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.values())

    # =========================
    # 🧠 HYBRID MATCHING (KEYWORD + SEMANTIC)
    # =========================
    def match_tools(self, user_input: str, top_k: int = 3):
        text = user_input.lower()
        scored = []

        for tool in self.tools.values():
            keyword_score = 0

            # 🔥 intent matching (strong)
            for intent in getattr(tool, "intents", []):
                if intent in text:
                    keyword_score += 2

            # 🔥 entity matching (weak)
            for entity in getattr(tool, "entities", []):
                if entity in text:
                    keyword_score += 1

            # 🔥 semantic similarity
            semantic_score = self.semantic.similarity(user_input, tool)

            # 🔥 hybrid score
            final_score = keyword_score + (semantic_score * 2)

            # ⚠️ minimal threshold
            if final_score > 0.5:
                scored.append((final_score, tool))

        # sort by score
        scored.sort(key=lambda x: x[0], reverse=True)

        # DEBUG (optional but useful)
        print("DEBUG: Tool Scores →", [
            (t.name, round(s, 2)) for s, t in scored
        ])

        return [tool for _, tool in scored[:top_k]]

    # =========================
    # 🧠 TOOL PROMPT BUILDER
    # =========================
    def build_tool_prompt(self) -> str:
        lines = []

        for tool in self.tools.values():
            args = []

            if tool.args_schema:
                try:
                    schema = tool.args_schema.model_json_schema()
                    args = list(schema.get("properties", {}).keys())
                except Exception:
                    pass

            lines.append(
                f"- {tool.name}: {tool.description}\n"
                f"  intents: {tool.intents}\n"
                f"  args: {args}"
            )

        return "\n".join(lines)
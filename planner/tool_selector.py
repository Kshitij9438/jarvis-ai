class ToolSelector:
    def __init__(self, registry):
        self.registry = registry

    def select(self, query: str, top_k: int = 2):
        """
        Select top-K tools using registry.match_tools()
        """

        # 🔥 use existing registry method
        candidate_tools = self.registry.match_tools(query)

        scored = []

        q = query.lower()

        for tool in candidate_tools:
            score = 0

            # intent match
            for word in getattr(tool, "intents", []):
                if word in q:
                    score += 2

            # entity match
            for word in getattr(tool, "entities", []):
                if word in q:
                    score += 1

            # base score
            score += 0.1

            scored.append((tool, score))

        # sort by score
        scored.sort(key=lambda x: x[1], reverse=True)

        print("DEBUG: Tool Scores →", [(t.name, round(s, 2)) for t, s in scored])

        selected = [tool for tool, _ in scored[:top_k]]

        return selected
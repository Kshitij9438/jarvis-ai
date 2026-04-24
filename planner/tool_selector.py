import re
from typing import List, Set, Tuple


class ToolSelector:
    """
    V3 — Clean, Intent-Driven Tool Selector
    Responsibilities:
    - Select best tools for a query
    - NO dependency logic
    - NO context mutation logic
    """

    def __init__(self, registry):
        self.registry = registry

        self.KNOWN_SITES = {
            "youtube", "google", "coursera", "spotify",
            "github", "amazon", "netflix", "leetcode"
        }

        self.MATH_KEYWORDS = {
            "+", "-", "*", "/", "calculate", "compute",
            "evaluate", "sqrt", "square", "cube",
            "power", "percent", "%"
        }

    # =========================
    # 🚀 MAIN SELECT
    # =========================
    def select(self, query: str, top_k: int = 2, context=None) -> List:
        print(f"\n[ToolSelector V3] Query: '{query}'")

        tools = self.registry.list_tools()

        # 1. HARD FILTER (ONLY INPUT BASED)
        valid_tools = self._hard_filter(query, tools)

        if not valid_tools:
            return self._safe_fallback()

        # 2. INTENT DETECTION
        intents = self._detect_intents(query)
        if not intents:
            intents.add("information")

        print(f"[ToolSelector] Intents → {intents}")

        # 3. SCORING
        scored = self._score_tools(query, valid_tools, intents)

        print("[ToolSelector] Scores →", [
            (t.name, round(s, 2)) for t, s in scored
        ])

        if not scored:
            return self._safe_fallback()

        best_score = scored[0][1]

        # Weak confidence → fallback
        if best_score < 0.8:
            return self._safe_fallback()

        # Relative filtering
        selected = [
            tool for tool, score in scored
            if score >= best_score * 0.8
        ]

        return selected[:top_k]

    # =========================
    # 🧠 HARD FILTER (NO CONTEXT)
    # =========================
    def _hard_filter(self, query: str, tools: List) -> List:
        valid = []
        q = query.lower()

        for tool in tools:
            name = tool.name

            if name == "calculator":
                if not re.search(r'\d', q):
                    continue

            elif name == "open_website":
                has_target = any(site in q for site in self.KNOWN_SITES) \
                             or bool(re.search(r'\.[a-z]{2,3}', q))
                has_nav = any(w in q for w in ["open", "visit", "go to"])

                if not (has_target and has_nav):
                    continue

            elif name == "load_document":
                if not re.search(r'\.(pdf|txt|md)', q):
                    continue

            valid.append(tool)

        return valid

    # =========================
    # 🧠 INTENT DETECTION
    # =========================
    def _detect_intents(self, query: str) -> Set[str]:
        q = query.lower()
        intents = set()

        signatures = {
            "navigation": ["open", "visit", "go to", "launch"],
            "calculation": list(self.MATH_KEYWORDS),
            "document": ["file", "pdf", "document", "summarize"],
            "information": [
                "explain", "what is", "who is",
                "how", "guide", "learn", "teach"
            ]
        }

        for intent, words in signatures.items():
            if any(w in q for w in words):
                intents.add(intent)

        return intents

    # =========================
    # 🧠 SCORING
    # =========================
    def _score_tools(self, query: str, tools: List, intents: Set[str]) -> List[Tuple]:
        q = query.lower()
        scored = []

        for tool in tools:
            score = 0.0

            # Intent alignment
            if tool.name == "calculator" and "calculation" in intents:
                score += 3

            if tool.name == "open_website" and "navigation" in intents:
                score += 3

            if tool.name in ["load_document", "rag_search"] and "document" in intents:
                score += 3

            if tool.name in ["explain", "web_retriever"] and "information" in intents:
                score += 3

            # Keyword matching
            for kw in getattr(tool, "intents", []):
                if kw in q:
                    score += 1.5

            for ent in getattr(tool, "entities", []):
                if ent in q:
                    score += 1.0

            # Semantic similarity
            if hasattr(self.registry, "semantic"):
                sim = self.registry.semantic.similarity(query, tool)
                score += min(sim, 0.6) * 2

            scored.append((tool, score))

        return sorted(scored, key=lambda x: x[1], reverse=True)

    # =========================
    # 🧠 FALLBACK
    # =========================
    def _safe_fallback(self):
        tool = self.registry.get("explain")
        return [tool] if tool else []
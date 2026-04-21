from planner.task import Task
from calculator.parser import CalculatorParser


class TaskBuilder:
    def __init__(self, arg_extractor):
        self.arg_extractor = arg_extractor
        self.calculator_parser = CalculatorParser()

    def build_tasks(self, user_input: str, matched_tools: list, entities: dict) -> list[Task]:
        tasks = []
        text = user_input.lower().strip()

        for tool in matched_tools:

            # =========================
            # 🧮 CALCULATOR (STRICT + CLEAN)
            # =========================
            if tool.name == "calculator":
                expr = self.calculator_parser.parse(user_input)

                # ❌ skip if no valid expression
                if not expr:
                    continue

                task = Task(
                    type="calculator",
                    target=None,
                    file_path=None,
                    query=expr
                )
                tasks.append(task)
                continue  # 🔥 do not fall through

            # =========================
            # 🧠 ARG EXTRACTION (SAFE)
            # =========================
            try:
                extracted = self.arg_extractor.extract(user_input, tool) or {}
            except Exception:
                extracted = {}

            # =========================
            # 🧱 ENTITY MERGE
            # =========================
            if entities.get("file_path"):
                extracted["file_path"] = entities["file_path"]

            if entities.get("websites"):
                extracted["url"] = entities["websites"][0]

            query = extracted.get("query")

            # =========================
            # 🧠 TOOL-SPECIFIC LOGIC
            # =========================

            # 🌐 WEB RETRIEVER (CLEAN QUERY)
            if tool.name == "web_retriever":
                if not query or len(query.strip()) < 3:
                    query = self._clean_query(user_input)

            # 🧠 EXPLAIN (USE ENTITIES FIRST)
            elif tool.name == "explain":
                if entities.get("topics"):
                    query = entities["topics"][0]

                elif not query or len(query.strip()) < 3:
                    query = self._clean_query(user_input)

            # 📄 RAG SEARCH
            elif tool.name == "rag_search":
                if "summarize" in text:
                    query = "summarize the document"
                elif not query or len(query.strip()) < 3:
                    query = "summarize the document"

            # 🌐 OPEN WEBSITE
            elif tool.name == "open_website":
                if entities.get("websites"):
                    extracted["url"] = entities["websites"][0]

            # =========================
            # 🔁 FINAL FALLBACK
            # =========================
            if not query:
                query = self._clean_query(user_input)

            # =========================
            # 🧱 BUILD TASK
            # =========================
            task = Task(
                type=tool.name,
                target=extracted.get("url"),
                file_path=extracted.get("file_path"),
                query=query
            )

            tasks.append(task)

        # =========================
        # 🔥 DEDUPLICATION (CRITICAL)
        # =========================
        unique_tasks = []
        seen = set()

        for t in tasks:
            key = (t.type, t.query, t.target, t.file_path)

            if key not in seen:
                seen.add(key)
                unique_tasks.append(t)

        return unique_tasks

    # =========================
    # 🧠 QUERY CLEANER (SHARED)
    # =========================
    def _clean_query(self, query: str) -> str:
        q = query.lower().strip()

        fillers = [
            "please", "can you", "could you",
            "tell me", "give me", "i want to know",
            "explain", "what is", "who is"
        ]

        for f in fillers:
            q = q.replace(f, " ")

        return " ".join(q.split())
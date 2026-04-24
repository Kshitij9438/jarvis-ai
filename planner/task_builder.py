from planner.task import Task
from calculator.parser import CalculatorParser
import os


class TaskBuilder:
    def __init__(self, arg_extractor):
        self.arg_extractor = arg_extractor
        self.calculator_parser = CalculatorParser()

    def build_tasks(self, user_input: str, matched_tools: list, entities: dict) -> list[Task]:
        tasks = []
        text = user_input.lower().strip()

        for tool in matched_tools:

            # =========================
            # 🧮 CALCULATOR (STRICT)
            # =========================
            if tool.name == "calculator":
                expr = self.calculator_parser.parse(user_input)

                if not expr:
                    continue

                tasks.append(Task(
                    type="calculator",
                    target=None,
                    file_path=None,
                    query=expr
                ))
                continue

            # =========================
            # 🧠 SAFE ARG EXTRACTION (LOW TRUST)
            # =========================
            try:
                extracted = self.arg_extractor.extract(user_input, tool) or {}
            except Exception:
                extracted = {}

            # =========================
            # 🧱 ENTITY PRIORITY (HIGH TRUST)
            # =========================
            file_path = None
            url = None

            # 🔥 STRICT FILE PATH VALIDATION
            if entities.get("file_path"):
                fp = entities["file_path"]

                # only accept if actually exists
                if isinstance(fp, str) and os.path.exists(fp):
                    file_path = fp

            # 🔥 WEBSITE ENTITY
            if entities.get("websites"):
                url = entities["websites"][0]

            query = extracted.get("query")

            # =========================
            # 🧠 TOOL-SPECIFIC LOGIC
            # =========================

            # 🌐 WEB RETRIEVER
            if tool.name == "web_retriever":
                if not query or len(query.strip()) < 3:
                    query = self._clean_query(user_input)

                if not query:
                    continue  # 🔥 skip useless retrieval

            # 🧠 EXPLAIN
            elif tool.name == "explain":
                if entities.get("topics"):
                    query = entities["topics"][0]

                elif not query or len(query.strip()) < 3:
                    query = self._clean_query(user_input)

                if not query:
                    continue

            # 📄 RAG SEARCH (ONLY IF DOCUMENT CONTEXT EXISTS)
            elif tool.name == "rag_search":
                if not file_path:
                    continue  # 🔥 DO NOT hallucinate document usage

                if "summarize" in text:
                    query = "summarize the document"
                else:
                    query = extracted.get("query") or "summarize the document"

            # 🌐 OPEN WEBSITE
            elif tool.name == "open_website":
                if not url:
                    continue

            # =========================
            # 🔁 FINAL FALLBACK (SAFE)
            # =========================
            if not query:
                cleaned = self._clean_query(user_input)

                if not cleaned:
                    continue

                query = cleaned

            # =========================
            # 🧱 BUILD TASK
            # =========================
            tasks.append(Task(
                type=tool.name,
                target=url,
                file_path=file_path,
                query=query
            ))

        # =========================
        # 🔥 DEDUPLICATION
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
    # 🧠 QUERY CLEANER
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

        q = " ".join(q.split())

        # 🔥 reject useless queries
        if len(q) < 3:
            return ""

        return q
from planner.task import Task
from calculator.parser import CalculatorParser


class TaskBuilder:
    def __init__(self, arg_extractor):
        self.arg_extractor = arg_extractor
        self.calculator_parser = CalculatorParser()  # 🔥 new

    def build_tasks(self, user_input: str, matched_tools: list, entities: dict) -> list[Task]:
        tasks = []

        text = user_input.lower()

        for tool in matched_tools:

            # =========================
            # 🚫 CALCULATOR GUARD
            # =========================
            if tool.name == "calculator":
                math_signals = [
                    "+", "-", "*", "/", "^",
                    "divide", "multiply", "add", "subtract",
                    "calculate", "compute", "evaluate",
                    "percent", "percentage",
                    "sqrt", "square", "cube"
                ]

                if not any(signal in text for signal in math_signals):
                    continue

                if not any(char.isdigit() for char in text):
                    continue

            # =========================
            # 🧠 Extract args (optional fallback)
            # =========================
            extracted = self.arg_extractor.extract(user_input, tool)

            # =========================
            # 🧱 Merge entities
            # =========================
            if entities.get("file_path"):
                extracted["file_path"] = entities["file_path"]

            if entities.get("websites"):
                extracted["url"] = entities["websites"][0]

            query = extracted.get("query")

            # =========================
            # 🧠 TOOL-SPECIFIC LOGIC
            # =========================

            # 🧮 CALCULATOR (CLEAN ARCHITECTURE)
            if tool.name == "calculator":
                expr = self.calculator_parser.parse(user_input)

                if not expr:
                    continue  # 🔥 skip invalid math completely

                query = expr

            # 📄 RAG
            elif tool.name == "rag_search":
                if "summarize" in text:
                    query = "summarize the document"
                elif not query or len(query.strip()) < 3:
                    query = "summarize the document"

            # 🧠 EXPLAIN
            elif tool.name == "explain":
                if entities.get("topics"):
                    query = entities["topics"][0]

            # =========================
            # 🔁 FALLBACK
            # =========================
            if not query:
                query = user_input

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

        return tasks
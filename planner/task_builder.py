from planner.task import Task


class TaskBuilder:
    def __init__(self, arg_extractor):
        self.arg_extractor = arg_extractor

    def build_tasks(self, user_input: str, matched_tools: list, entities: dict) -> list[Task]:
        tasks = []

        for tool in matched_tools:
            # =========================
            # 🧠 1. Extract structured args
            # =========================
            extracted = self.arg_extractor.extract(user_input, tool)

            # =========================
            # 🧱 2. Merge reliable entities
            # =========================
            if entities.get("file_path"):
                extracted["file_path"] = entities["file_path"]

            if entities.get("websites"):
                extracted["url"] = entities["websites"][0]

            # =========================
            # 🧠 3. TOOL-SPECIFIC QUERY FIXES (CRITICAL)
            # =========================
            query = extracted.get("query")

            # 🔥 RAG FIX
            if tool.name == "rag_search":
                if "summarize" in user_input.lower():
                    query = "summarize the document"
                elif not query or len(query.strip()) < 3:
                    query = "summarize the document"

            # 🔥 EXPLAIN FIX
            elif tool.name == "explain":
                if entities.get("topics"):
                    query = entities["topics"][0]

            # 🔥 FALLBACK
            if not query:
                query = user_input

            # =========================
            # 🧱 4. Build task
            # =========================
            task = Task(
                type=tool.name,
                target=extracted.get("url") or extracted.get("website"),
                file_path=extracted.get("file_path"),
                query=query
            )

            tasks.append(task)

        return tasks
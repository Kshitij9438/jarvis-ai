from planner.task import Task


class TaskBuilder:
    def __init__(self, arg_extractor):
        self.arg_extractor = arg_extractor

    def build_tasks(self, user_input: str, matched_tools: list, entities: dict) -> list[Task]:
        tasks = []

        for tool in matched_tools:
            # 🧠 1. Extract structured args using LLM + schema
            extracted = self.arg_extractor.extract(user_input, tool)

            # 🧱 2. Merge reliable regex entities (override if needed)
            if "file_path" in entities:
                extracted["file_path"] = entities["file_path"]

            if "url" in entities:
                extracted["url"] = entities["url"]

            # 🧠 3. Build generic task
            task = Task(
                type=tool.name,
                target=extracted.get("url") or extracted.get("website"),
                file_path=extracted.get("file_path"),
                query=extracted.get("query") or user_input
            )

            tasks.append(task)

        return tasks
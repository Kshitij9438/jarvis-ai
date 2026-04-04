from planner.task import Task


class TaskBuilder:
    def __init__(self):
        pass

    def build_tasks(self, user_input: str, intents: list, entities: dict) -> list[Task]:
        tasks = []

        # =========================
        # 🌐 OPEN WEBSITE TASKS (DYNAMIC)
        # =========================
        if "open_website" in intents:
            for site in entities.get("websites", []):
                tasks.append(Task(
                    type="open_website",
                    target=site
                ))

        # =========================
        # 📄 LOAD DOCUMENT TASK
        # =========================
        if "load_document" in intents:
            file_path = entities.get("file_path")

            if file_path:
                tasks.append(Task(
                    type="load_document",
                    file_path=file_path
                ))

        # =========================
        # 📝 SUMMARIZE TASK
        # =========================
        if "summarize" in intents:
            tasks.append(Task(
                type="summarize",
                query="summary of loaded document"
            ))

        # =========================
        # 📚 EXPLAIN TASK (DYNAMIC)
        # =========================
        if "explain" in intents:
            topics = entities.get("topics", [])

            if topics:
                for topic in topics:
                    tasks.append(Task(
                        type="explain",
                        query=topic
                    ))
            else:
                # fallback
                tasks.append(Task(
                    type="explain",
                    query=user_input
                ))

        return tasks
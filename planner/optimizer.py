from planner.task import Task


class TaskOptimizer:
    def __init__(self):
        # 🔥 simple synonym map (extend later)
        self.synonyms = {
            "artificial intelligence": "ai",
            "machine learning": "ml",
        }

        # 🔥 noise words to remove
        self.noise_words = {"again", "please", "now", "once", "more"}

    def optimize(self, tasks: list[Task]) -> list[Task]:
        """
        Optimization pipeline:
        1. Normalize
        2. Deduplicate (semantic)
        3. Filter invalid
        """
        tasks = self._normalize(tasks)
        tasks = self._deduplicate(tasks)
        tasks = self._filter_invalid(tasks)

        return tasks

    # =========================
    # 🧠 NORMALIZATION
    # =========================
    def _normalize(self, tasks: list[Task]) -> list[Task]:
        normalized = []

        for task in tasks:
            query = self._normalize_query(task.query)

            t = Task(
                type=task.type,
                target=task.target.lower().strip() if task.target else None,
                file_path=task.file_path.strip() if task.file_path else None,
                query=query
            )
            normalized.append(t)

        return normalized

    # =========================
    # 🧠 QUERY NORMALIZATION
    # =========================
    def _normalize_query(self, query: str | None) -> str | None:
        if not query:
            return query

        query = query.lower().strip()

        # remove noise words
        words = query.split()
        words = [w for w in words if w not in self.noise_words]
        query = " ".join(words)

        # synonym replacement
        for phrase, replacement in self.synonyms.items():
            if phrase in query:
                query = replacement

        return query

    # =========================
    # 🔁 DEDUPLICATION
    # =========================
    def _deduplicate(self, tasks: list[Task]) -> list[Task]:
        seen = set()
        unique = []

        for task in tasks:
            key = self._task_key(task)

            if key not in seen:
                seen.add(key)
                unique.append(task)

        return unique

    def _task_key(self, task: Task):
        if task.type == "open_website":
            return (task.type, task.target)

        elif task.type == "load_document":
            return (task.type, task.file_path)

        elif task.type in ["summarize", "explain"]:
            return (task.type, task.query)

        return (task.type, task.target, task.file_path, task.query)

    # =========================
    # 🚫 FILTER INVALID TASKS
    # =========================
    def _filter_invalid(self, tasks: list[Task]) -> list[Task]:
        valid = []

        for task in tasks:
            if task.type == "open_website":
                if task.target:
                    valid.append(task)

            elif task.type == "load_document":
                if task.file_path:
                    valid.append(task)

            elif task.type in ["summarize", "explain"]:
                if task.query:
                    valid.append(task)

            else:
                valid.append(task)

        return valid
from planner.task import Task
import re


class TaskOptimizer:
    def __init__(self):
        # 🔥 synonym map (EXTENSIBLE)
        self.synonyms = {
            "artificial intelligence": "ai",
            "machine learning": "ml",
            "deep learning": "dl",
        }

        # 🔥 learning patterns → canonical form
        self.learning_patterns = [
            r"how to (.+)",
            r"learn (.+)",
            r"teach me (.+)",
            r"understand (.+)",
            r"guide me (.+)",
        ]

        # 🔥 noise words
        self.noise_words = {
            "again", "please", "now", "once", "more",
            "me", "about", "on", "in", "the", "a", "an"
        }

    # =========================
    # 🧠 MAIN PIPELINE
    # =========================
    def optimize(self, tasks: list[Task]) -> list[Task]:
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
    # 🧠 QUERY NORMALIZATION (UPGRADED)
    # =========================
    def _normalize_query(self, query: str | None) -> str | None:
        if not query:
            return query

        query = query.lower().strip()

        # 🔥 1. Remove noise words
        words = query.split()
        words = [w for w in words if w not in self.noise_words]
        query = " ".join(words)

        # 🔥 2. Apply synonym compression
        for phrase, replacement in self.synonyms.items():
            if phrase in query:
                query = query.replace(phrase, replacement)

        # 🔥 3. Learning intent normalization
        for pattern in self.learning_patterns:
            match = re.search(pattern, query)
            if match:
                topic = match.group(1).strip()

                # apply synonyms again on extracted topic
                for phrase, replacement in self.synonyms.items():
                    if phrase in topic:
                        topic = topic.replace(phrase, replacement)

                return f"{topic} basics"

        # 🔥 4. Remove duplicate words (e.g., "git git")
        words = query.split()
        seen = set()
        cleaned_words = []

        for w in words:
            if w not in seen:
                seen.add(w)
                cleaned_words.append(w)

        query = " ".join(cleaned_words)

        return query.strip()

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
                # ❌ reject meaningless queries
                if task.query and len(task.query.strip()) > 2:
                    valid.append(task)

            else:
                valid.append(task)

        return valid
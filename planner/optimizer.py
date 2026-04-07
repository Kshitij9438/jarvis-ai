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
        if not tasks:
            return []

        original_tasks = list(tasks)  # 🔥 keep original for recovery

        tasks = self._normalize(tasks)
        tasks = self._deduplicate(tasks)
        tasks = self._filter_invalid(tasks)

        # =========================
        # 🔥 DEPENDENCY PROTECTION (CRITICAL)
        # =========================
        task_types = {t.type for t in tasks}

        if "rag_search" in task_types:
            has_loader = any(t.type == "load_document" for t in tasks)

            if not has_loader:
                # 🔥 recover loader from ORIGINAL tasks
                for t in original_tasks:
                    if t.type == "load_document" and t.file_path:
                        tasks.insert(0, t)
                        break

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

        # 🔥 remove noise
        words = query.split()
        words = [w for w in words if w not in self.noise_words]
        query = " ".join(words)

        # 🔥 synonyms
        for phrase, replacement in self.synonyms.items():
            if phrase in query:
                query = query.replace(phrase, replacement)

        # 🔥 learning normalization
        for pattern in self.learning_patterns:
            match = re.search(pattern, query)
            if match:
                topic = match.group(1).strip()

                for phrase, replacement in self.synonyms.items():
                    if phrase in topic:
                        topic = topic.replace(phrase, replacement)

                return f"{topic} basics"

        # 🔥 remove duplicates
        words = query.split()
        seen = set()
        cleaned = []

        for w in words:
            if w not in seen:
                seen.add(w)
                cleaned.append(w)

        return " ".join(cleaned).strip()

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

        elif task.type in ["rag_search", "explain"]:  # ✅ FIXED
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

            elif task.type in ["rag_search", "explain"]:  # ✅ FIXED
                if task.query and len(task.query.strip()) > 2:
                    valid.append(task)

            else:
                valid.append(task)

        return valid
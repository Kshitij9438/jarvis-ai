from __future__ import annotations

import re

from planner.task import Task


class PlanOptimizer:
    """
    M7 planning boundary for plan optimization.

    Owns deterministic optimization of the task collection produced
    by PlanBuilder.

    Responsibilities:
    - normalize tasks
    - normalize task queries
    - deduplicate tasks
    - filter invalid tasks
    - recover required document-loading dependencies

    This implementation intentionally preserves the existing
    TaskOptimizer behavior. The CanonicalQuery redesign remains
    a later M7 concern.
    """

    def __init__(self):
        # Synonym map.
        self.synonyms = {
            "artificial intelligence": "ai",
            "machine learning": "ml",
            "deep learning": "dl",
        }

        self.short_form_queries = set(self.synonyms.values())

        # Learning patterns → canonical form.
        self.learning_patterns = [
            r"how to (.+)",
            r"learn (.+)",
            r"teach me (.+)",
            r"understand (.+)",
            r"guide me (.+)",
        ]

        # Noise words.
        self.noise_words = {
            "again",
            "please",
            "now",
            "once",
            "more",
            "me",
            "about",
            "on",
            "in",
            "the",
            "a",
            "an",
        }

    # =========================
    # MAIN PIPELINE
    # =========================

    def optimize(self, tasks: list[Task]) -> list[Task]:
        if not tasks:
            return []

        original_tasks = list(tasks)

        tasks = self._normalize(tasks)
        tasks = self._deduplicate(tasks)
        tasks = self._filter_invalid(tasks)

        # =========================
        # DEPENDENCY PROTECTION
        # =========================

        task_types = {task.type for task in tasks}

        if "rag_search" in task_types:
            has_loader = any(
                task.type == "load_document"
                for task in tasks
            )

            if not has_loader:
                # Recover loader from ORIGINAL tasks.
                for task in original_tasks:
                    if task.type == "load_document" and task.file_path:
                        tasks.insert(0, task)
                        break

        return tasks

    # =========================
    # NORMALIZATION
    # =========================

    def _normalize(self, tasks: list[Task]) -> list[Task]:
        normalized = []

        for task in tasks:
            query = self._normalize_query(task.query)

            normalized_task = Task(
                type=task.type,
                target=(
                    task.target.lower().strip()
                    if task.target
                    else None
                ),
                file_path=(
                    task.file_path.strip()
                    if task.file_path
                    else None
                ),
                query=query,
            )

            normalized.append(normalized_task)

        return normalized

    # =========================
    # QUERY NORMALIZATION
    # =========================

    def _normalize_query(
        self,
        query: str | None,
    ) -> str | None:
        if not query:
            return query

        query = query.lower().strip()

        # Remove noise.
        words = query.split()
        words = [
            word
            for word in words
            if word not in self.noise_words
        ]
        query = " ".join(words)

        # Synonyms.
        for phrase, replacement in self.synonyms.items():
            if phrase in query:
                query = query.replace(
                    phrase,
                    replacement,
                )

        # Learning normalization.
        for pattern in self.learning_patterns:
            match = re.search(pattern, query)

            if match:
                topic = match.group(1).strip()

                for phrase, replacement in self.synonyms.items():
                    if phrase in topic:
                        topic = topic.replace(
                            phrase,
                            replacement,
                        )

                return f"{topic} basics"

        # Remove duplicate words.
        words = query.split()
        seen = set()
        cleaned = []

        for word in words:
            if word not in seen:
                seen.add(word)
                cleaned.append(word)

        return " ".join(cleaned).strip()

    # =========================
    # DEDUPLICATION
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
            return (
                task.type,
                task.target,
            )

        elif task.type == "load_document":
            return (
                task.type,
                task.file_path,
            )

        elif task.type in ["rag_search", "explain"]:
            return (
                task.type,
                task.query,
            )

        return (
            task.type,
            task.target,
            task.file_path,
            task.query,
        )

    # =========================
    # FILTER INVALID TASKS
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

            elif task.type in ["rag_search", "explain"]:
                if self._is_valid_query(task.query):
                    valid.append(task)

            else:
                valid.append(task)

        return valid

    def _is_valid_query(self, query: str | None) -> bool:
        if not query:
            return False

        query = query.strip()

        if not query:
            return False

        if len(query) > 2:
            return True

        return query in self.short_form_queries

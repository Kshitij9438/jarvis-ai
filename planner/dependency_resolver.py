from planner.task import Task


class DependencyResolver:
    def __init__(self):
        # 🔥 Dependency rules (EXTENSIBLE)
        self.dependencies = {
            "summarize": ["load_document"],
        }

    def resolve(self, tasks: list[Task]) -> list[Task]:
        """
        Resolves task order using context-aware dependency rules.
        """

        if not tasks:
            return []

        ordered = []
        visited = set()

        # 🔥 Map tasks by type
        task_map = {}
        for task in tasks:
            task_map.setdefault(task.type, []).append(task)

        # 🔥 Resolve each task
        for task in tasks:
            self._resolve_task(task, task_map, ordered, visited)

        return ordered

    # =========================
    # 🔗 CORE RESOLUTION LOGIC
    # =========================
    def _resolve_task(self, task: Task, task_map, ordered, visited):
        key = self._task_key(task)

        if key in visited:
            return

        # 🔥 1. Resolve dependencies (CONTEXT-AWARE)
        deps = self.dependencies.get(task.type, [])

        for dep in deps:
            if self._should_apply_dependency(task, dep):
                if dep in task_map:
                    for dep_task in task_map[dep]:
                        self._resolve_task(dep_task, task_map, ordered, visited)
                else:
                    # ⚠️ Missing dependency → handled gracefully
                    pass

        # 🔥 2. Add current task
        ordered.append(task)
        visited.add(key)

    # =========================
    # 🧠 CONTEXT-AWARE CHECK
    # =========================
    def _should_apply_dependency(self, task: Task, dep: str) -> bool:
        """
        Decide whether dependency should apply.
        """

        # 🔥 Case: summarize
        if task.type == "summarize":
            # Only require load_document if file_path exists
            if task.file_path:
                return True
            return False

        return True

    # =========================
    # 🧠 UNIQUE TASK ID
    # =========================
    def _task_key(self, task: Task):
        return (task.type, task.target, task.file_path, task.query)
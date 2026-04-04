from planner.task import Task


class DependencyResolver:
    def __init__(self):
        # 🔥 Dependency rules (EXTENSIBLE)
        self.dependencies = {
            "summarize": ["load_document"],
            # future:
            # "analyze": ["load_document"],
            # "send_email": ["compose_email"]
        }

    def resolve(self, tasks: list[Task]) -> list[Task]:
        """
        Resolves task order using dependency rules.
        """

        if not tasks:
            return []

        ordered = []
        visited = set()

        # 🔥 Map tasks by type (first occurrence)
        task_map = {}
        for task in tasks:
            if task.type not in task_map:
                task_map[task.type] = []
            task_map[task.type].append(task)

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

        # 1. Resolve dependencies first
        deps = self.dependencies.get(task.type, [])

        for dep in deps:
            if dep in task_map:
                for dep_task in task_map[dep]:
                    self._resolve_task(dep_task, task_map, ordered, visited)

        # 2. Add current task
        ordered.append(task)
        visited.add(key)

    # =========================
    # 🧠 UNIQUE TASK ID
    # =========================
    def _task_key(self, task: Task):
        return (task.type, task.target, task.file_path, task.query)
from planner.schema import Plan, Action


class PlanValidator:
    def __init__(self):
        pass

    def validate(self, plan: Plan) -> Plan:
        """
        Validation pipeline:
        1. Remove invalid steps
        2. Sanity checks
        3. Dependency validation (non-destructive)
        """
        steps = plan.steps

        steps = self._remove_invalid_steps(steps)
        steps = self._validate_dependencies(steps)

        return Plan(steps=steps)

    # =========================
    # 🚫 REMOVE INVALID STEPS
    # =========================
    def _remove_invalid_steps(self, steps: list[Action]) -> list[Action]:
        valid = []

        for step in steps:
            action = step.action
            args = step.args

            # -------------------------
            # 🌐 OPEN WEBSITE
            # -------------------------
            if action == "open_website":
                url = args.get("url")

                if url and self._is_valid_url(url):
                    valid.append(step)

            # -------------------------
            # 📄 LOAD DOCUMENT
            # -------------------------
            elif action == "load_document":
                file_path = args.get("file_path")

                if file_path:
                    valid.append(step)

            # -------------------------
            # 🧠 SUMMARIZE / RAG
            # -------------------------
            elif action in ["summarize", "rag_search"]:
                query = args.get("query")

                if query and len(query.strip()) > 3:
                    valid.append(step)

            # -------------------------
            # 📚 EXPLAIN
            # -------------------------
            elif action == "explain":
                query = args.get("query")

                if query and query.strip() != "explain":
                    valid.append(step)

            # -------------------------
            # 🔮 FUTURE TOOLS
            # -------------------------
            else:
                valid.append(step)

        return valid

    # =========================
    # 🔗 DEPENDENCY VALIDATION
    # =========================
    def _validate_dependencies(self, steps: list[Action]) -> list[Action]:
        """
        Non-destructive dependency handling
        """

        actions = [s.action for s in steps]

        has_load = "load_document" in actions
        has_summarize = any(a in ["summarize", "rag_search"] for a in actions)

        # 🔥 Rule: summarize without load → convert to generic summarize
        if has_summarize and not has_load:
            for step in steps:
                if step.action in ["summarize", "rag_search"]:
                    # keep as-is (standalone summarize)
                    continue

        return steps

    # =========================
    # 🌐 URL VALIDATION
    # =========================
    def _is_valid_url(self, url: str) -> bool:
        if not url:
            return False

        if " " in url:
            return False

        if not (url.startswith("http://") or url.startswith("https://")):
            return False

        # basic domain check
        if "." not in url:
            return False

        return True
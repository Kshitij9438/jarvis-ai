from planner.schema import Plan, Action

from planner.task_builder import TaskBuilder
from planner.dependency_resolver import DependencyResolver
from planner.entity_extractor import EntityExtractor
from planner.arg_extractor import ArgExtractor

from brain.llm import LLM
from planner.optimizer import TaskOptimizer
from planner.validator import PlanValidator
from planner.intelligence import PlannerIntelligence
from planner.scorer import PlanScorer

# 🔥 NEW
from planner.tool_selector import ToolSelector


class Planner:
    def __init__(self, registry):
        self.registry = registry

        self.llm = LLM()
        self.arg_extractor = ArgExtractor(self.llm)
        self.task_builder = TaskBuilder(self.arg_extractor)
        self.dependency_resolver = DependencyResolver(self.registry)
        self.entity_extractor = EntityExtractor()

        self.optimizer = TaskOptimizer()
        self.validator = PlanValidator()
        self.intelligence = PlannerIntelligence()
        self.scorer = PlanScorer(registry=self.registry)

        # 🔥 NEW
        self.tool_selector = ToolSelector(self.registry)

    def plan(self, user_input: str):

        # =========================
        # 🧠 Step 0: SEGMENTATION (ONLY for tasks)
        # =========================
        segments = [s.strip() for s in user_input.split(" and ")]

        # =========================
        # 🧠 Step 1: GLOBAL TOOL SELECTION (NEW CORE)
        # =========================
        matched_tools = self.tool_selector.select(user_input, top_k=2)

        # =========================
        # 🔗 Step 1.5: DEPENDENCY EXPANSION
        # =========================
        final_tools = []
        added = set()

        for tool in matched_tools:
            # add dependencies first
            for dep_name in getattr(tool, "requires", []):
                dep_tool = self.registry.get(dep_name)
                if dep_tool and dep_tool.name not in added:
                    final_tools.append(dep_tool)
                    added.add(dep_tool.name)

            # add main tool
            if tool.name not in added:
                final_tools.append(tool)
                added.add(tool.name)

        matched_tools = final_tools

        print(f"DEBUG: Final Matched Tools → {[t.name for t in matched_tools]}")

        if not matched_tools:
            return Plan(steps=[
                Action(action="echo", args={"text": "🤔 No matching tool found"})
            ])

        # =========================
        # 🧱 Step 2: TASK BUILDING
        # =========================
        tasks = []

        for segment in segments:
            segment_entities = self.entity_extractor.extract(segment)

            segment_tasks = self.task_builder.build_tasks(
                segment,
                matched_tools,   # 🔥 IMPORTANT CHANGE
                segment_entities
            )

            tasks.extend(segment_tasks)

        print(f"DEBUG: Raw Tasks → {tasks}")

        # =========================
        # ⚙️ Step 3: OPTIMIZATION
        # =========================
        tasks = self.optimizer.optimize(tasks)
        print(f"DEBUG: Optimized Tasks → {tasks}")

        if not tasks:
            return Plan(steps=[
                Action(action="echo", args={"text": "⚠️ Could not build tasks"})
            ])

        # =========================
        # 🔗 Step 4: DEPENDENCY RESOLUTION
        # =========================
        ordered_tasks = self.dependency_resolver.resolve(tasks)

        ordered_tasks.sort(
            key=lambda t: self.registry.get(t.type).priority
            if self.registry.get(t.type) else 5
        )

        print(f"DEBUG: Ordered Tasks → {ordered_tasks}")

        # =========================
        # ⚙️ Step 5: TASK → ACTIONS
        # =========================
        steps = []

        for task in ordered_tasks:
            args = {}

            tool = self.registry.get(task.type)

            # 🌐 URL handling
            if task.type == "open_website" and task.target:
                args["url"] = self._normalize_url(task.target)

            # 📄 file path
            if task.file_path:
                args["file_path"] = task.file_path

            # 🧠 SMART ARG MAPPING
            if tool and task.query:
                try:
                    schema = tool.args_schema.model_json_schema()
                    fields = list(schema.get("properties", {}).keys())
                except Exception:
                    fields = []

                if "expression" in fields:
                    args["expression"] = task.query
                elif "query" in fields:
                    args["query"] = task.query
                else:
                    args["query"] = task.query

            steps.append(Action(
                action=task.type,
                args=args
            ))

        print(f"DEBUG: Steps → {steps}")

        # =========================
        # ✅ Step 6: VALIDATION
        # =========================
        plan = Plan(steps=steps)
        plan = self.validator.validate(plan)
        print(f"DEBUG: Validated Plan → {plan}")

        # =========================
        # 🧠 Step 7: INTELLIGENCE
        # =========================
        plan = self.intelligence.refine(plan)
        print(f"DEBUG: Final Plan → {plan}")

        # =========================
        # 🧠 Step 8: SCORING
        # =========================
        score = self.scorer.score(plan)
        print(f"DEBUG: Plan Score → {score}")

        return plan

    def _normalize_url(self, site: str) -> str:
        site = site.strip().lower()

        sites = {
            "youtube": "https://youtube.com",
            "google": "https://www.google.com",
            "coursera": "https://www.coursera.org",
            "spotify": "https://www.spotify.com",
            "github": "https://github.com",
            "amazon": "https://www.amazon.com",
            "netflix": "https://www.netflix.com",
            "leetcode": "https://leetcode.com",
        }

        if site in sites:
            return sites[site]

        if site.startswith("http://") or site.startswith("https://"):
            return site

        if "." in site:
            return f"https://{site}"

        return f"https://www.{site}.com"
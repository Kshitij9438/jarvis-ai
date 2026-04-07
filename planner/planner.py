from planner.schema import Plan, Action

# 🧠 TOOL-CENTRIC IMPORTS
from planner.task_builder import TaskBuilder
from planner.dependency_resolver import DependencyResolver
from planner.entity_extractor import EntityExtractor
from planner.arg_extractor import ArgExtractor

# 🔥 CORE SYSTEM
from brain.llm import LLM
from planner.optimizer import TaskOptimizer
from planner.validator import PlanValidator
from planner.intelligence import PlannerIntelligence
from planner.scorer import PlanScorer


class Planner:
    def __init__(self, registry):
        self.registry = registry

        # 🧠 CORE COMPONENTS
        self.llm = LLM()
        self.arg_extractor = ArgExtractor(self.llm)
        self.task_builder = TaskBuilder(self.arg_extractor)
        self.dependency_resolver = DependencyResolver(self.registry)
        self.entity_extractor = EntityExtractor()

        # 🔥 EXISTING PIPELINE
        self.optimizer = TaskOptimizer()
        self.validator = PlanValidator()
        self.intelligence = PlannerIntelligence()
        self.scorer = PlanScorer(registry=self.registry)

    # =========================
    # 🤖 MAIN PLANNER
    # =========================
    def plan(self, user_input: str):

        # =========================
        # 🧠 Step 1: MULTI-INTENT SPLITTING
        # =========================
        segments = [s.strip() for s in user_input.split(" and ")]

        all_tools = []

        for segment in segments:
            tools = self.registry.match_tools(segment)
            print(f"DEBUG: Segment '{segment}' → {[t.name for t in tools]}")
            all_tools.extend(tools)

        # remove duplicates (preserve order)
        seen = set()
        matched_tools = []

        for tool in all_tools:
            if tool.name not in seen:
                matched_tools.append(tool)
                seen.add(tool.name)

        print(f"DEBUG: Final Matched Tools → {[t.name for t in matched_tools]}")

        # ⚠️ fallback if nothing matched
        if not matched_tools:
            return Plan(steps=[
                Action(action="echo", args={"text": "🤔 No matching tool found"})
            ])

        # =========================
        # 🧱 Step 2: SEGMENT-AWARE TASK BUILDING (🔥 FIX)
        # =========================
        tasks = []

        for segment in segments:
            segment_tools = self.registry.match_tools(segment)

            if not segment_tools:
                continue

            segment_entities = self.entity_extractor.extract(segment)

            segment_tasks = self.task_builder.build_tasks(
                segment,
                segment_tools,
                segment_entities
            )

            tasks.extend(segment_tasks)

        print(f"DEBUG: Raw Tasks → {tasks}")

        # =========================
        # ⚙️ Step 3: OPTIMIZATION
        # =========================
        tasks = self.optimizer.optimize(tasks)
        print(f"DEBUG: Optimized Tasks → {tasks}")

        # ⚠️ fallback
        if not tasks:
            return Plan(steps=[
                Action(action="echo", args={"text": "⚠️ Could not build tasks"})
            ])

        # =========================
        # 🔗 Step 4: DEPENDENCY RESOLUTION
        # =========================
        ordered_tasks = self.dependency_resolver.resolve(tasks)

        # ⚡ priority-based ordering
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

            if task.target:
                args["url"] = self._normalize_url(task.target)

            if task.file_path:
                args["file_path"] = task.file_path

            if task.query:
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

    # =========================
    # 🌐 URL NORMALIZATION
    # =========================
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
from planner.schema import Plan, Action

from planner.task_builder import TaskBuilder
from planner.entity_extractor import EntityExtractor
from planner.arg_extractor import ArgExtractor

from brain.llm import LLM
from planner.optimizer import TaskOptimizer
from planner.validator import PlanValidator
from planner.intelligence import PlannerIntelligence
from planner.scorer import PlanScorer

from planner.tool_selector import ToolSelector
from control.control_layer import ControlLayer
from execution.context_dependency import ContextDependencyResolver
from planner.retrieval_signals import (
    has_explicit_search_request,
    requires_current_information,
)
from planner.retrieval_decision import (
    RetrievalDecision,
    should_use_retrieval,
)
from execution.context_signals import has_retrieved_content
from planner.capability_selector import CapabilitySelector
from planner.plan_builder import PlanBuilder



class Planner:
    def __init__(self, registry):
        self.registry = registry

        self.llm = LLM()
        self.arg_extractor = ArgExtractor(self.llm)
        self.task_builder = TaskBuilder(self.arg_extractor)
        self.entity_extractor = EntityExtractor()

        self.optimizer = TaskOptimizer()
        self.validator = PlanValidator()
        self.intelligence = PlannerIntelligence()
        self.scorer = PlanScorer(registry=self.registry)

        self.tool_selector = ToolSelector(self.registry)
        self.control_layer = ControlLayer()
        self.context_resolver = ContextDependencyResolver(self.registry)
        self.capability_selector = CapabilitySelector()
        self.plan_builder = PlanBuilder(
            registry=self.registry,
            capability_selector=self.capability_selector,
            tool_selector=self.tool_selector,
            task_builder=self.task_builder,
            entity_extractor=self.entity_extractor,
        )

    # =========================
    # RETRIEVAL DECISION
    # =========================
    def _should_use_retriever(self, query: str, context=None) -> bool:
        """
        Determine whether web retrieval should be used for a query.

        Retrieval is driven by explicit currentness/search signals and
        existing retrieved context, not by lexical presence of words such
        as "explain" or "architecture".
        """
        decision = should_use_retrieval(
            requires_current_information=requires_current_information(query),
            explicit_search_request=has_explicit_search_request(query),
            context_available=has_retrieved_content(context),
        )

        return decision == RetrievalDecision.USE


    def _is_trivial_input(self, text: str) -> bool:
        t = text.lower().strip()
        greetings = {
            "hi", "hello", "hey", "yo", "sup",
            "good morning", "good afternoon", "good evening"
        }
        return t in greetings or len(t) <= 3

    # =========================
    # 🚀 MAIN PLANNER
    # =========================
    def plan(self, user_input: str, context=None):

        if self._is_trivial_input(user_input):
            return Plan(steps=[
                Action(action="echo", args={"text": "Hey! How can I help you?"})
            ])

        # =========================
        # 🧱 PLAN BUILDING
        # =========================
        all_tasks = self.plan_builder.build(
            user_input,
            context,
        )
        # =========================
        # ❌ NO TASKS
        # =========================
        if not all_tasks:
            return Plan(steps=[
                Action(action="echo", args={"text": "⚠️ Could not build tasks"})
            ])

        print(f"\nDEBUG: ALL TASKS → {all_tasks}")

        # =========================
        # ⚙️ STEP 2: OPTIMIZATION
        # =========================
        tasks = self.optimizer.optimize(all_tasks)
        print(f"DEBUG: Optimized Tasks → {tasks}")

        if not tasks:
            return Plan(steps=[
                Action(action="echo", args={"text": "⚠️ Tasks vanished after optimization"})
            ])

        # =========================
        # 🔗 STEP 3: CLEAN ORDERING
        # =========================
        def _task_order_key(t):
            tool = self.registry.get(t.type)
            return tool.priority if tool else 5

        ordered_tasks = sorted(tasks, key=_task_order_key)
        print(f"DEBUG: Ordered Tasks → {ordered_tasks}")

        # =========================
        # ⚙️ STEP 4: TASK → ACTIONS
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

            # 🧠 argument mapping
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
        # ✅ STEP 5: VALIDATION
        # =========================
        plan = Plan(steps=steps)
        plan = self.validator.validate(plan)
        print(f"DEBUG: Validated Plan → {plan}")

        # =========================
        # 🧠 STEP 6: INTELLIGENCE
        # =========================
        plan = self.intelligence.refine(plan)
        print(f"DEBUG: Intelligent Plan → {plan}")

        # =========================
        # 🧠 STEP 7: CONTROL LAYER
        # =========================
        plan = self.control_layer.refine_plan(plan, context)
        print(f"DEBUG: Controlled Plan → {plan}")

        # =========================
        # 🧠 STEP 8: CONTEXT DEPENDENCY RESOLUTION (CRITICAL)
        # =========================
        resolved_steps = self.context_resolver.resolve(plan.steps, context)
        plan = Plan(steps=resolved_steps)
        print(f"DEBUG: Context-Resolved Plan → {plan}")

        # =========================
        # 🧠 STEP 9: SCORING
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
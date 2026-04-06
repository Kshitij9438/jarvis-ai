from planner.schema import Plan, Action

# 🔥 Core deterministic pipeline
from planner.intent import classify_intent
from planner.task_builder import TaskBuilder
from planner.dependency_resolver import DependencyResolver
from planner.entity_extractor import EntityExtractor

# 🔥 LLM enhancement layer
from planner.llm_enhancer import LLMEnhancer
from brain.llm import LLM
from planner.optimizer import TaskOptimizer
from planner.validator import PlanValidator
from planner.intelligence import PlannerIntelligence

# 🧠 NEW: Plan Scorer
from planner.scorer import PlanScorer
from planner.completeness import CompletenessChecker


class Planner:
    def __init__(self, registry):
        self.registry = registry
        self.task_builder = TaskBuilder()
        self.dependency_resolver = DependencyResolver()

        # 🔥 Hybrid layer
        self.llm = LLM()
        self.enhancer = LLMEnhancer(self.llm)
        self.entity_extractor = EntityExtractor()
        self.optimizer = TaskOptimizer()
        self.validator = PlanValidator()
        self.intelligence = PlannerIntelligence()

        # 🧠 NEW
        self.scorer = PlanScorer()
        self.completeness = CompletenessChecker()

    # =========================
    # 🤖 MAIN PLANNER (V2.6 - WITH SCORING)
    # =========================
    def plan(self, user_input: str, max_retries: int = 2):

        # =========================
        # 🧠 Step 1: Intent Classification
        # =========================
        intents = classify_intent(self.llm, user_input)
        print(f"DEBUG: Intents → {intents}")

        # =========================
        # 🧠 Step 2: Entity Extraction
        # =========================
        entities = self.entity_extractor.extract(user_input)
        print(f"DEBUG: Entities → {entities}")

        # =========================
        # 🧱 Step 3: Task Building
        # =========================
        tasks = self.task_builder.build_tasks(user_input, intents, entities)
        print(f"DEBUG: Raw Tasks → {tasks}")

        tasks = self.optimizer.optimize(tasks)
        print(f"DEBUG: Optimized Tasks → {tasks}")

        # =========================
        # ⚠️ Fallback (no tasks)
        # =========================
        if not tasks:
            return Plan(steps=[
                Action(action="echo", args={"text": "👍"})
            ])

        # =========================
        # 🔗 Step 4: Dependency Resolution
        # =========================
        ordered_tasks = self.dependency_resolver.resolve(tasks)
        print(f"DEBUG: Ordered Tasks → {ordered_tasks}")

        # =========================
        # ⚙️ Step 5: Task → Actions
        # =========================
        steps = []

        for task in ordered_tasks:
            if task.type == "open_website":
                steps.append(Action(
                    action="open_website",
                    args={"url": self._normalize_url(task.target)}
                ))

            elif task.type == "load_document":
                steps.append(Action(
                    action="load_document",
                    args={"file_path": task.file_path}
                ))

            elif task.type == "summarize":
                steps.append(Action(
                    action="rag_search",
                    args={"query": task.query}
                ))

            elif task.type == "explain":
                steps.append(Action(
                    action="explain",
                    args={"query": task.query}
                ))

        print(f"DEBUG: Base Steps → {steps}")

        # =========================
        # 🤖 Step 6: LLM Enhancement (SAFE)
        # =========================
        # try:
        #     enhanced_steps = self.enhancer.enhance(user_input, steps)
        #
        #     # ✅ Safety check: fallback if bad output
        #     if enhanced_steps and len(enhanced_steps) >= len(steps):
        #         print(f"DEBUG: Enhanced Steps → {enhanced_steps}")
        #         steps = enhanced_steps
        #     else:
        #         print("⚠️ Enhancement ignored (unsafe or empty)")
        #
        # except Exception as e:
        #     print("⚠️ Enhancement failed:", e)

        # =========================
        # ✅ Step 7: Validation
        # =========================
        plan = Plan(steps=steps)
        plan = self.validator.validate(plan)
        print(f"DEBUG: Validated Plan → {plan}")
        # 🧠 NEW: completeness check
        plan = self.completeness.ensure(plan, intents, entities)
        print(f"DEBUG: After Completeness → {plan}")

        # =========================
        # 🧠 Step 8: Intelligence Layer
        # =========================
        plan = self.intelligence.refine(plan,intents)
        print(f"DEBUG: Final Plan (after intelligence) → {plan}")

        # =========================
        # 🧠 NEW: Step 9 → SCORING
        # =========================
        score = self.scorer.score(plan, intents)
        print(f"DEBUG: Plan Score → {score}")

        return plan

    # =========================
    # 🌐 URL NORMALIZATION
    # =========================
    def _normalize_url(self, site: str) -> str:
        site = site.strip().lower()

        # 🔥 Known high-quality mappings
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

        # 🔥 If already full URL
        if site.startswith("http://") or site.startswith("https://"):
            return site

        # 🔥 If looks like domain
        if "." in site:
            return f"https://{site}"

        # 🔥 Default fallback
        return f"https://www.{site}.com"
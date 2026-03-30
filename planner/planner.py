from brain.llm import LLM
from planner.schema import Plan

# 🔥 New modular imports
from planner.intent import classify_intent
from planner.control import control_layer
from planner.tool_prompt import build_tool_prompt


class Planner:
    def __init__(self, registry):
        self.llm = LLM()
        self.registry = registry

    # =========================
    # 🤖 MAIN PLANNER (ORCHESTRATOR)
    # =========================
    def plan(self, user_input: str, max_retries: int = 2):
        # =========================
        # 🧠 Step 1: Intent Classification
        # =========================
        intents = classify_intent(self.llm, user_input)

        # =========================
        # ⚙️ Step 2: Control Layer (fast deterministic path)
        # =========================
        controlled = control_layer(user_input, intents)

        if controlled is not None:
            return controlled

        # =========================
        # 🧱 Step 3: Tool Context
        # =========================
        tool_info = build_tool_prompt(self.registry)

        # =========================
        # 🤖 Step 4: LLM Planning (fallback)
        # =========================
        for attempt in range(max_retries):
            print(f"DEBUG: Planning attempt {attempt+1}")

            plan = self.llm.generate_plan(
                user_input=user_input,
                schema=Plan,
                tool_info=tool_info
            )

            if plan is not None:
                return plan

            print("⚠️ Plan generation failed, retrying...")

        print("❌ Failed to generate plan after retries")
        return None
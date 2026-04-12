class ExecutionContext:
    def __init__(self, user_input: str):
        # 🎯 Goal
        self.goal = user_input

        # 🧠 Core memory
        self.history = []              # [(tool, input, output)]
        self.tool_outputs = {}         # {"key": value}

        # 📦 Shared knowledge
        self.search_results = None
        self.retrieved_content = None

        # 🔄 Execution tracking
        self.current_plan = None
        self.last_result = None

        # ⚙️ Control
        self.step_count = 0
        self.max_steps = 5

    # =========================
    # 🧠 UPDATE AFTER EACH STEP
    # =========================
    def update(self, tool_name: str, args: dict, result):
        self.history.append({
            "tool": tool_name,
            "args": args,
            "result": result
        })

        self.last_result = result
        self.step_count += 1

    # =========================
    # 📦 STORE OUTPUT
    # =========================
    def store(self, key: str, value):
        self.tool_outputs[key] = value

    # =========================
    # 📦 RETRIEVE OUTPUT
    # =========================
    def get(self, key: str):
        return self.tool_outputs.get(key)
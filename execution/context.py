class ExecutionContext:
    def __init__(self, user_input: str):
        self.goal = user_input

        # =========================
        # 🧠 STRICT CONTEXT BUCKETS
        # =========================
        self._buckets = {
            "web": [],
            "document": [],
            "memory": [],
            "calculation": []
        }

        # expose read-only view for resolver
        self.buckets = self._buckets

        # =========================
        # 🧠 EXECUTION TRACE
        # =========================
        self.history = []

        self.last_result = None
        self.step_count = 0
        self.max_steps = 5

        # 🔥 LIMITS (important)
        self.MAX_PER_BUCKET = 10

    # =========================
    # 🧠 STORE CONTEXT
    # =========================
    def store(self, context_type: str, data):
        if not data:
            return

        if context_type not in self._buckets:
            self._buckets[context_type] = []

        self._buckets[context_type].append(data)

        # 🔥 prevent uncontrolled growth
        if len(self._buckets[context_type]) > self.MAX_PER_BUCKET:
            self._buckets[context_type] = self._buckets[context_type][-self.MAX_PER_BUCKET:]

    # =========================
    # 🧠 GET CONTEXT (TOP-K + MERGED)
    # =========================
    def get(self, context_type: str, k: int = 3):
        data = self._buckets.get(context_type, [])

        if not data:
            return None

        selected = data[-k:]

        # 🔥 flatten into string (critical for LLM)
        if isinstance(selected, list):
            return "\n\n".join(str(x) for x in selected)

        return selected

    # =========================
    # 🧠 CHECK CONTEXT
    # =========================
    def has(self, context_type: str) -> bool:
        return bool(self._buckets.get(context_type))

    # =========================
    # 🧠 UPDATE HISTORY
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
    # 🧠 CLEAR CONTEXT (OPTIONAL)
    # =========================
    def clear(self, context_type: str = None):
        if context_type:
            self._buckets[context_type] = []
        else:
            for k in self._buckets:
                self._buckets[k] = []

    # =========================
    # 🧠 DEBUG VIEW
    # =========================
    def debug(self):
        return {
            "goal": self.goal,
            "buckets": self._buckets,
            "history": self.history
        }
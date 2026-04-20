class ExecutionContext:
    def __init__(self, user_input: str):
        self.goal = user_input

        self.history = []
        self.tool_outputs = {}

        self.search_results = None
        self.retrieved_content = None

        self.current_plan = None
        self.last_result = None

        self.step_count = 0
        self.max_steps = 5

    def update(self, tool_name: str, args: dict, result):
        self.history.append({
            "tool": tool_name,
            "args": args,
            "result": result
        })
        self.last_result = result
        self.step_count += 1

    def store(self, key: str, value):
        self.tool_outputs[key] = value
        # ✅ sync to attribute so context.retrieved_content works
        #    (was outside this function before — silent bug)
        setattr(self, key, value)

    def get(self, key: str):
        return self.tool_outputs.get(key)
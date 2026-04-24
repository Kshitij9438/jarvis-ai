class Executor:
    def __init__(self, registry):
        self.registry = registry

    # =========================
    # 🔧 NORMALIZATION
    # =========================
    def normalize_args(self, action, args):
        args = args.copy()

        if action == "load_document":
            if "filepath" in args:
                args["file_path"] = args.pop("filepath")

            if "file_path" in args:
                args["file_path"] = args["file_path"].strip('"').strip("'")

        return args

    # =========================
    # 🧠 RELIABILITY CHECK
    # =========================
    def is_reliable(self, result):
        if result is None:
            return False

        text = str(result).lower()

        failure_signals = [
            "⚠️", "error", "failed", "not found",
            "no result", "no useful", "invalid",
            "exception", "could not", "unable to"
        ]

        if any(signal in text for signal in failure_signals):
            return False

        if len(text.strip()) < 5:
            return False

        return True

    # =========================
    # 🧠 CONTEXT FETCH (STRICT + CLEAN)
    # =========================
    def get_context_for_tool(self, tool, context):
        if not context:
            return None

        required = getattr(tool, "requires_context", [])

        if not required:
            return None

        collected = []

        for ctx_type in required:
            if not context.has(ctx_type):
                continue

            data = context.get(ctx_type)

            # 🔥 Clean list → string
            if isinstance(data, list):
                data = "\n\n".join(map(str, data))

            if data:
                collected.append(str(data))

        if not collected:
            return None

        final_context = "\n\n".join(collected)

        print(f"[Executor] Injecting context → {tool.name} | types={required}")

        return final_context

    # =========================
    # 🚀 EXECUTION
    # =========================
    def execute(self, plan, context=None):
        if plan is None:
            return ["⚠️ No valid plan."]

        results = []

        for step in plan.steps:

            # 🔥 execution safety guard
            if context and context.step_count >= context.max_steps:
                print("⚠️ Max steps reached — stopping execution")
                break

            tool = self.registry.get(step.action)

            if tool is None:
                results.append(f"⚠️ Unknown tool: {step.action}")
                continue

            try:
                # =========================
                # 🔧 NORMALIZE + VALIDATE
                # =========================
                normalized_args = self.normalize_args(step.action, step.args)
                validated_args = tool.args_schema(**normalized_args)
                args_dict = validated_args.model_dump()

                # =========================
                # 🧠 CONTEXT INJECTION (SAFE)
                # =========================
                tool_context = self.get_context_for_tool(tool, context)

                # 🔥 Only inject if tool actually supports it
                if tool_context and "context" in tool.args_schema.model_fields:
                    args_dict["context"] = tool_context

                # =========================
                # 🚀 EXECUTE
                # =========================
                result = tool.run(**args_dict)

                print(f"EXECUTED: {step.action}")

                # 🔍 Debug context usage
                if tool_context:
                    print(f"[Executor] Context used for {tool.name}:\n{tool_context[:200]}...")

                # =========================
                # 🧠 UPDATE CONTEXT
                # =========================
                if context:
                    context.update(step.action, args_dict, result)

                    if self.is_reliable(result):
                        for ctx_type in getattr(tool, "produces_context", []):
                            context.store(ctx_type, result)

                results.append(result)

            except Exception as e:
                print(f"DEBUG EXECUTOR ERROR ({step.action}):", e)
                results.append(f"⚠️ Missing or invalid arguments for {step.action}")

        return results
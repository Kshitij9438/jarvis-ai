class Executor:
    def __init__(self, registry):
        self.registry = registry

    # =========================
    # 🔧 NORMALIZATION LAYER
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
    # 🧠 OUTPUT KEY RESOLUTION (NEW)
    # =========================
    def get_output_key(self, tool, action):
        # 🔥 Preferred: tool-defined output key
        if hasattr(tool, "output_key"):
            return tool.output_key

        # 🔁 Fallback (for existing tools)
        fallback_map = {
            "web_search": "search_results",
            "web_retriever": "retrieved_content",
            "calculator": "calculation_result",
        }

        return fallback_map.get(action)

    # =========================
    # 🚀 EXECUTION
    # =========================
    def execute(self, plan, context=None):
        if plan is None:
            return ["⚠️ No valid plan."]

        results = []

        for step in plan.steps:
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
                # 🧠 EXECUTION
                # =========================
                result = tool.run(**args_dict)

                # 🔍 Debug (optional but useful)
                print(f"EXECUTED: {step.action}")

                # =========================
                # 🧠 UPDATE CONTEXT
                # =========================
                if context:
                    context.update(step.action, args_dict, result)

                    if self.is_reliable(result):
                        output_key = self.get_output_key(tool, step.action)

                        if output_key:
                            context.store(output_key, result)

                results.append(result)

            except Exception as e:
                print(f"DEBUG EXECUTOR ERROR ({step.action}):", e)
                results.append(f"⚠️ Missing or invalid arguments for {step.action}")

        return results
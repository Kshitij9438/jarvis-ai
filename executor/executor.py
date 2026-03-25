class Executor:
    def __init__(self, registry):
        self.registry = registry

    # 🔥 NEW: normalization layer
    def normalize_args(self, action, args):
        args = args.copy()

        # =========================
        # 📄 load_document fixes
        # =========================
        if action == "load_document":
            # Fix wrong key names
            if "filepath" in args:
                args["file_path"] = args.pop("filepath")

            # Remove quotes from file path
            if "file_path" in args:
                args["file_path"] = args["file_path"].strip('"').strip("'")

        return args

    def execute(self, plan):
        if plan is None:
            return ["⚠️ No valid plan."]

        results = []

        for step in plan.steps:
            tool = self.registry.get(step.action)

            if tool is None:
                results.append(f"⚠️ Unknown tool: {step.action}")
                continue

            try:
                # 🔥 normalize BEFORE validation
                normalized_args = self.normalize_args(step.action, step.args)

                validated_args = tool.args_schema(**normalized_args)
                result = tool.run(**validated_args.model_dump())

                results.append(result)

            except Exception as e:
                # 🔥 optional debug (can remove later)
                print(f"DEBUG EXECUTOR ERROR ({step.action}):", e)

                results.append(f"⚠️ Missing or invalid arguments for {step.action}")

        return results
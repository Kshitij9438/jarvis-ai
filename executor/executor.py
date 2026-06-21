class Executor:
    """
    Executes a Plan's steps against the tool registry, returning one
    structured result dict per step:

        {"step": action_name, "success": bool, "result": Any, "error": str|None}

    Contract notes (read before "fixing" anything below):

    - If the step-count guard trips mid-plan, fewer result dicts are
      returned than there are plan.steps. This is intentional, not a
      bug — ExecutionLoop._repair_plan() explicitly checks for
      len(results) != len(plan.steps) and refuses to repair when it
      can't safely correlate results to steps. Padding the result list
      with synthetic "skipped" entries here would silently break that
      safety check by making a partial execution look complete.

    - context.update() is called even when a step fails. This is also
      intentional: it records the attempted args + failure result in
      context.history, which is what lets ExecutionLoop's subtractive
      repair print a meaningful reason for why a step was dropped.
    """

    def __init__(self, registry):
        self.registry = registry

    # =========================
    # 🔧 NORMALIZATION
    # =========================
    def normalize_args(self, action, args):
        """
        Tool-specific argument cleanup applied before schema validation.

        file_path is guarded with an explicit type check rather than
        calling .strip() directly — a bad LLM extraction or a malformed
        plan can hand this a None, int, or list instead of a string,
        and an unguarded .strip() would raise AttributeError with a
        confusing message ("'NoneType' object has no attribute
        'strip'") that obscures the actual problem. Schema validation
        right after this still catches the bad value either way; this
        just makes the failure legible instead of cryptic.
        """
        args = args.copy() if args else {}

        if action == "load_document":
            if "filepath" in args:
                args["file_path"] = args.pop("filepath")

            if "file_path" in args:
                fp = args["file_path"]
                if isinstance(fp, str):
                    args["file_path"] = fp.strip('"').strip("'")
                # non-string file_path is left as-is; args_schema
                # validation in execute() will reject it with a clear
                # "Schema validation failed" error instead of crashing
                # here with an unrelated AttributeError.

        return args

    # =========================
    # 🧠 RELIABILITY CHECK
    # =========================
    def is_reliable(self, result):
        """
        Determines whether a tool's output counts as a real, usable
        result rather than a failure.

        Anchored on the "⚠️" prefix convention that every tool in this
        codebase already uses to signal failure (CalculatorTool,
        RAGTool, WebRetrieverTool, LoadDocTool via rag.load_file) —
        NOT on generic English words like "error"/"failed"/"invalid".

        That word-list approach was the previous implementation and it
        produces false negatives on any tool that returns prose
        containing those words for legitimate reasons — e.g. explain
        or web_retriever output describing "a 404 error" or "an
        invalid state transition" as part of the actual answer. Since
        failure here means "drop this step's content, mark it for
        repair," a false negative silently discards correct output.

        If you add a new tool, it MUST prefix failure strings with
        "⚠️" for this check to recognize them as failures — that's the
        contract, not an implementation detail.
        """
        if result is None:
            return False

        text = str(result).strip()

        if text.startswith("⚠️"):
            return False

        if len(text) < 5:
            return False

        return True

    # =========================
    # 🧠 CONTEXT FETCH
    # =========================
    def get_context_for_tool(self, tool, context):
        """
        Assumes `tool` is not None — execute() already returns early
        with an "Unknown tool" error before this is ever called, so
        that invariant holds for the current call site. Flagged here
        because this is a public-ish helper method; if it's ever
        called from somewhere else, that assumption travels with it.
        """
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
            return [{
                "step": None,
                "success": False,
                "result": None,
                "error": "No valid plan"
            }]

        results = []

        for step in plan.steps:

            # =========================
            # 🔥 STEP LIMIT GUARD
            # =========================
            # Breaking here (rather than appending a placeholder result
            # for remaining steps) is deliberate — see class docstring.
            if context and context.step_count >= context.max_steps:
                print("⚠️ Max steps reached — stopping execution")
                break

            tool = self.registry.get(step.action)

            if tool is None:
                results.append({
                    "step": step.action,
                    "success": False,
                    "result": None,
                    "error": f"Unknown tool: {step.action}"
                })
                continue

            try:
                # =========================
                # 🔧 NORMALIZE
                # =========================
                normalized_args = self.normalize_args(step.action, step.args)

                # =========================
                # 🧠 SCHEMA VALIDATION (ISOLATED)
                # =========================
                try:
                    validated_args = tool.args_schema(**normalized_args)
                    args_dict = validated_args.model_dump()
                except Exception as schema_error:
                    print(f"[Executor] Schema error ({step.action}):", schema_error)

                    results.append({
                        "step": step.action,
                        "success": False,
                        "result": None,
                        "error": "Schema validation failed"
                    })
                    continue

                # =========================
                # 🧠 CONTEXT INJECTION
                # =========================
                tool_context = self.get_context_for_tool(tool, context)

                if tool_context and "context" in tool.args_schema.model_fields:
                    args_dict["context"] = tool_context

                # =========================
                # 🚀 TOOL EXECUTION
                # =========================
                result = tool.run(**args_dict)

                success = self.is_reliable(result)

                print(f"[Executor] Step={step.action} | Success={success}")

                # =========================
                # 🧠 UPDATE CONTEXT
                # =========================
                # Called on failure too — see class docstring.
                if context:
                    context.update(step.action, args_dict, result)

                    if success:
                        for ctx_type in getattr(tool, "produces_context", []):

                            # 🔥 CONTEXT FILTER (prevents pollution)
                            if isinstance(result, str) and len(result) > 20:
                                context.store(ctx_type, result)

                # =========================
                # 📦 STRUCTURED OUTPUT
                # =========================
                results.append({
                    "step": step.action,
                    "success": success,
                    "result": result,
                    "error": None if success else str(result)
                })

                # =========================
                # 🔍 DEBUG CONTEXT USAGE
                # =========================
                if tool_context:
                    print(f"[Executor] Context used for {tool.name}:\n{tool_context[:200]}...")

            except Exception as runtime_error:
                print(f"[Executor] Runtime error ({step.action}):", runtime_error)

                results.append({
                    "step": step.action,
                    "success": False,
                    "result": None,
                    "error": str(runtime_error)
                })

        return results
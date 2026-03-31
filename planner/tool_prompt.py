def build_tool_prompt(registry) -> str:
    tools = registry.list_tools()

    if not tools:
        return "No tools available."

    tool_descriptions = []

    for tool in tools:
        desc = f"- {tool.name}: {tool.description}"

        # 🔥 OPTIONAL: include argument schema (huge upgrade)
        if hasattr(tool, "args_schema"):
            try:
                schema = tool.args_schema.model_json_schema()
                desc += f"\n  args: {schema}"
            except:
                pass

        tool_descriptions.append(desc)

    return "\n".join(tool_descriptions)
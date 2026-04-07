import json


class ArgExtractor:
    def __init__(self, llm):
        self.llm = llm

    def extract(self, user_input: str, tool) -> dict:
        """
        Extract structured arguments for a tool using its args_schema.

        Strategy:
        1. Use LLM guided by tool schema
        2. Clean JSON safely
        3. Validate fields against schema
        4. Fail gracefully (never crash planner)
        """

        # no schema → no args
        if not tool.args_schema:
            return {}

        try:
            schema = tool.args_schema.model_json_schema()
            fields = schema.get("properties", {})

            prompt = f"""
Extract arguments for the tool "{tool.name}".

Tool description: {tool.description}

Expected fields:
{list(fields.keys())}

Field details:
{fields}

User input:
"{user_input}"

RULES:
- Return ONLY valid JSON
- Do NOT include explanation
- Do NOT include extra keys
- Keep values SHORT and precise
- If a field is missing, omit it

Example:
{{"query": "machine learning"}}
"""

            # 🔥 LLM call
            response = self.llm.generate_text(prompt)

            # 🔧 CLEAN JSON (reuse your existing cleaner)
            response = self._clean_json(response)

            # ⚠️ guard against garbage output
            if not response or not response.strip().startswith("{"):
                return {}

            parsed = json.loads(response)

            # ✅ keep only valid schema fields
            valid_fields = set(fields.keys())
            filtered = {
                k: v for k, v in parsed.items()
                if k in valid_fields
            }

            return filtered

        except Exception as e:
            print(f"DEBUG ArgExtractor failed for {tool.name}: {e}")
            return {}

    # =========================
    # 🧹 JSON CLEANER
    # =========================
    def _clean_json(self, text: str) -> str:
        if not text:
            return ""

        text = text.strip()

        # remove ``` blocks
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines).strip()

        return text
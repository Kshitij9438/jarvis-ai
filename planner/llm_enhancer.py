from planner.schema import Action


class LLMEnhancer:
    def __init__(self, llm):
        self.llm = llm

    def enhance(self, user_input: str, existing_steps: list[Action]) -> list[Action]:
        """
        Uses LLM to enhance or add missing steps.
        """

        prompt = f"""
User request:
{user_input}

Current plan:
{existing_steps}

Your job:
- Add missing steps if needed
- Fix incorrect steps
- Keep steps SHORT
- Do NOT remove correct steps

Return ONLY JSON:

[
  {{
    "action": "tool_name",
    "args": {{}}
  }}
]
"""

        try:
            response = self.llm.generate_text(prompt)

            # ⚠️ minimal parsing (safe fallback)
            import json
            steps = json.loads(response)

            enhanced = []
            for step in steps:
                enhanced.append(Action(
                    action=step["action"],
                    args=step["args"]
                ))

            return enhanced

        except:
            return existing_steps  # fallback safety
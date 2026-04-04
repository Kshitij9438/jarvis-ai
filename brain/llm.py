import ollama
from config.settings import settings
from typing import Type, Optional
from pydantic import BaseModel, ValidationError


DEFAULT_SYSTEM_PROMPT = "You are JARVIS. Be concise and avoid unnecessary greetings."


class LLM:
    def __init__(self):
        self.model = settings.model_name

    # =========================
    # 🔧 CORE LOW-LEVEL CALL (REDUCED RETRIES)
    # =========================
    def _call(self, prompt: str, system_prompt: str, retries: int = 1):
        for attempt in range(retries):
            print(f"DEBUG: Using model: {self.model} (Attempt {attempt+1})")

            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    options={
                        "temperature": settings.temperature,
                        "num_predict": 300
                    }
                )

                content = response.get("message", {}).get("content", "").strip()

                if content:
                    print("DEBUG: Received response")
                    return content

            except Exception as e:
                print(f"ERROR (attempt {attempt+1}):", e)

        return "⚠️ LLM failed"

    # =========================
    # 🧹 CLEAN JSON
    # =========================
    def _clean_json(self, text: str) -> str:
        text = text.strip()

        if text.startswith("```"):
            lines = text.split("\n")
            lines = [line for line in lines if not line.strip().startswith("```")]
            text = "\n".join(lines).strip()

        return text

    # =========================
    # 🧠 TEXT
    # =========================
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        return self._call(prompt, system_prompt)

    # =========================
    # 📦 STRUCTURED (REDUCED RETRIES)
    # =========================
    def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel],
        system_prompt: str,
        retries: int = 2
    ):
        strict_prompt = f"""
Return ONLY valid JSON in this format:

{{
  "steps": [
    {{
      "action": "tool_name",
      "args": {{
        "url": "short string OR",
        "query": "short string"
      }}
    }}
  ]
}}

STRICT RULES:
- No markdown
- No explanation
- Only JSON
- Keep arguments VERY SHORT
- DO NOT include long explanations inside JSON
- DO NOT generate full answers in args

User request:
{prompt}
"""

        for attempt in range(retries):
            print(f"DEBUG: Structured attempt {attempt+1}")

            response = self._call(strict_prompt, system_prompt)
            response = self._clean_json(response)

            try:
                return schema.model_validate_json(response)
            except ValidationError as e:
                print("VALIDATION ERROR:", e)

        return None

    # =========================
    # 🤖 PLANNER
    # =========================
    def generate_plan(self, user_input: str, schema: Type[BaseModel], tool_info: str):
        system_prompt = f"""
You are an AI planner.

Break the user request into steps.

Available tools:
{tool_info}

CRITICAL RULES:
- You MUST cover ALL parts of the user request
- If user asks multiple things → create multiple steps
- DO NOT skip any intent
- Each step must correspond to a user request
- Use rag_search for:
  - explain
  - summarize

STRICT:
- Output ONLY JSON
- No markdown
- Each step must be atomic

Think carefully before answering.
"""

        return self.generate_structured(
            prompt=user_input,
            schema=schema,
            system_prompt=system_prompt
        )

    # =========================
    # 🔁 REFLECTION (REDUCED RETRIES)
    # =========================
    def generate_reflection(self, goal: str, plan, results):
        system_prompt = """
You are a strict but practical evaluator for an AI assistant.

Your job is to determine if the USER'S GOAL was completed.

=========================
EVALUATION METHOD (VERY IMPORTANT)
=========================

1. BREAK THE USER GOAL INTO SUB-TASKS
Example:
User: "open netflix and explain AI"

Subtasks:
- open netflix
- explain AI

2. CHECK EACH SUBTASK INDEPENDENTLY

3. MARK EACH:
- DONE ✔
- NOT DONE ❌

4. FINAL DECISION:
- If ALL subtasks are DONE → SUCCESS
- If ANY subtask is NOT DONE → FAIL

=========================
IMPORTANT RULES
=========================

- DO NOT require subtasks to be related
- DO NOT merge subtasks
- DO NOT assume dependency unless explicit

Example:
"open netflix and explain AI"
→ these are independent tasks

If:
✔ Netflix opened
✔ AI explained

→ SUCCESS

=========================
TOOL UNDERSTANDING
=========================

- open_website → task completed if site opened
- rag_search → valid for explain/summarize
- load_document → document loaded

=========================
FAIL ONLY IF
=========================

- A subtask is missing
- Output is clearly wrong or irrelevant

=========================
OUTPUT FORMAT
=========================

Return ONLY JSON:

{
  "status": "success" or "fail",
  "reason": "short explanation"
}
"""
        class ReflectionSchema(BaseModel):
            status: str
            reason: str

        strict_prompt = f"""
Return ONLY JSON:

{{
  "status": "success" or "fail",
  "reason": "string"
}}

Goal: {goal}

Plan: {plan}

Results: {results}
"""

        for attempt in range(2):
            print(f"DEBUG: Reflection attempt {attempt+1}")
            response = self._call(strict_prompt, system_prompt)
            response = self._clean_json(response)
            try:
                return ReflectionSchema.model_validate_json(response)
            except ValidationError:
                pass
        return None
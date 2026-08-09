import json
import ollama
from config.settings import settings
from typing import Type, Optional, get_args, get_origin
from pydantic import BaseModel, ValidationError


DEFAULT_SYSTEM_PROMPT = "You are JARVIS. Be concise and avoid unnecessary greetings."

# Defined at module level (not inside generate_reflection) so it isn't
# rebuilt on every call — it's a fixed, stateless schema.
class ReflectionSchema(BaseModel):
    status: str
    reason: str


# =============================================================================
# SCHEMA → EXAMPLE SKELETON
# =============================================================================
# generate_structured needs to show the model what JSON shape to produce.
# Dumping raw pydantic model_json_schema() (title/$defs/additionalProperties
# noise) at a small local model is unreliable — what works is a minimal
# *example instance* built from the schema's field names and types, e.g.
# {"action": "string", "args": {}} rather than the full JSON-Schema dict.
#
# This is intentionally best-effort: it produces a plausible filler value
# per field based on its declared type. It does not attempt to resolve
# deeply nested or recursive models beyond one level — for those, the
# placeholder is just "{}" or "[]", which is enough to show the model
# the right top-level keys even if the inner shape is approximate.

def _placeholder_for_type(annotation) -> object:
    """Best-effort example value for a single field's type annotation."""
    origin = get_origin(annotation)

    # list[...] / List[...] → one-element example list.
    # Also handles the bare, unparameterized `list` (get_origin(list) is
    # None, so it must be checked separately from get_origin(...) is list).
    if origin is list or annotation is list:
        args = get_args(annotation)
        inner = _placeholder_for_type(args[0]) if args else "string"
        return [inner]

    # dict[...] / Dict[...] → empty object (keys are caller-specific).
    # Also handles bare `dict` (e.g. Action.args: Dict in planner/schema.py) —
    # get_origin(dict) is None for the unparameterized form, same issue as list.
    if origin is dict or annotation is dict:
        return {}

    # Optional[X] / Union[X, None] → use X's placeholder
    if origin is not None and type(None) in get_args(annotation):
        non_none = [a for a in get_args(annotation) if a is not type(None)]
        return _placeholder_for_type(non_none[0]) if non_none else None

    # Nested pydantic model → recurse one level
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return _example_from_schema(annotation)

    if annotation in (int, float):
        return 0
    if annotation is bool:
        return False

    return "string"  # str and anything unrecognized


def _example_from_schema(schema: Type[BaseModel]) -> dict:
    """Build a minimal example dict {field_name: placeholder_value, ...}."""
    example = {}
    for field_name, field_info in schema.model_fields.items():
        example[field_name] = _placeholder_for_type(field_info.annotation)
    return example


class LLM:
    def __init__(self):
        self.model = settings.model_name

    # =========================
    # 🔧 CORE LOW-LEVEL CALL
    # =========================
    def _call(self, prompt: str, system_prompt: str, retries: int = 1):
        """
        retries=1 means a single attempt, no retry — this is intentional
        (reduced-retry mode for latency), not an off-by-one.
        """
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
    # 📦 STRUCTURED — NOW GENERIC OVER `schema`
    # =========================
    def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel],
        system_prompt: str,
        retries: int = 2
    ):
        """
        Generic structured-output call: the example JSON shown to the
        model is built FROM `schema` itself, not hardcoded to the
        planner's {"steps": [...]} shape. Any pydantic schema passed
        here now gets a prompt that actually matches what it validates
        against — previously this always showed the planner's Plan
        shape regardless of which schema was passed in, which silently
        broke any non-planner caller.
        """
        example = _example_from_schema(schema)
        example_json = json.dumps(example, indent=2)

        strict_prompt = f"""
Return ONLY valid JSON matching this exact shape:

{example_json}

STRICT RULES:
- No markdown
- No explanation
- Only JSON
- Keep argument/field values VERY SHORT
- DO NOT include long explanations inside JSON
- DO NOT generate full answers inside field values

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
    # 🔁 REFLECTION
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
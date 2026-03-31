from pydantic import BaseModel
from typing import List
from brain.llm import LLM


class IntentOutput(BaseModel):
    intents: List[str]


def classify_intent(llm: LLM, user_input: str) -> list:
    text = user_input.lower()
    intents = set()

    # =========================
    # ⚡ RULE-BASED EXTRACTION (ACCUMULATIVE)
    # =========================
    if "open" in text:
        intents.add("open_website")

    if ".pdf" in text or ".txt" in text or ".md" in text or "load" in text:
        intents.add("load_document")

    if "summarize" in text:
        intents.add("summarize")

    if "explain" in text:
        intents.add("explain")

    # =========================
    # 🤖 LLM AUGMENTATION (ONLY IF NEEDED)
    # =========================
    if len(intents) == 0:
        prompt = f"""
Classify the user intent into ONE OR MORE of the following categories:

- load_document
- summarize
- explain
- open_website
- general

Return ONLY JSON:
{{ "intents": ["...", "..."] }}

User input:
{user_input}
"""

        result = llm.generate_structured(
            prompt=prompt,
            schema=IntentOutput,
            system_prompt="Return only valid JSON."
        )

        if result and result.intents:
            intents.update(result.intents)

    # =========================
    # 🛡️ FINAL FALLBACK
    # =========================
    if not intents:
        return ["general"]

    return list(intents)
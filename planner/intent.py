from pydantic import BaseModel
from typing import List
from brain.llm import LLM


class IntentOutput(BaseModel):
    intents: List[str]


def classify_intent(llm: LLM, user_input: str) -> list:
    text = user_input.lower()
    intents = set()

    # =========================
    # 🧠 PHRASE + SYNONYM MAP
    # =========================
    INTENT_KEYWORDS = {
        "open_website": [
            "open", "go to", "visit", "launch", "browse"
        ],
        "load_document": [
            "load", "open file", "read file"
        ],
        "summarize": [
            "summarize", "summary", "brief"
        ],
        "explain": [
            "explain", "teach", "learn", "study",
            "understand", "guide", "how to"
        ],
    }

    # =========================
    # ⚡ RULE-BASED MATCHING
    # =========================
    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                intents.add(intent)
                break

    # =========================
    # 📄 FILE DETECTION BOOST
    # =========================
    if any(ext in text for ext in [".pdf", ".txt", ".md"]):
        intents.add("load_document")

    # =========================
    # 🎯 CONTEXTUAL RULES (IMPORTANT)
    # =========================

    # 👉 "learn X from youtube"
    if "youtube" in text and any(k in text for k in ["learn", "study", "teach"]):
        intents.add("open_website")
        intents.add("explain")

    # 👉 "how to X"
    if "how to" in text:
        intents.add("explain")

    # =========================
    # 🤖 LLM FALLBACK (RARE)
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
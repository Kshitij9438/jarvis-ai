import json
from difflib import get_close_matches
from brain.llm import LLM
from planner.schema import Plan
import re


def extract_json(text: str) -> str:
    start = text.find("[")
    if start != -1:
        bracket_count = 0
        for i in range(start, len(text)):
            if text[i] == "[":
                bracket_count += 1
            elif text[i] == "]":
                bracket_count -= 1
                if bracket_count == 0:
                    return text[start:i+1]

    start = text.find("{")
    if start != -1:
        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    return text[start:i+1]

    return ""


class Planner:
    def __init__(self, registry):
        self.llm = LLM()
        self.registry = registry

    # =========================
    # 🧱 TOOL PROMPT
    # =========================
    def build_tool_prompt(self) -> str:
        tools = self.registry.list_tools()

        if not tools:
            return "No tools available."

        return "\n".join(
            f"- {tool.name}: {tool.description}" for tool in tools
        )

    # =========================
    # 🧠 MULTI-INTENT CLASSIFIER (LLM)
    # =========================
    def classify_intent(self, user_input: str) -> list:
        prompt = f"""
Classify the user intent into ONE OR MORE of the following categories:

- load_document
- summarize
- explain
- open_website
- general

User input:
{user_input}

If multiple intents exist, return them separated by commas.
Output ONLY category names.
"""

        try:
            response = self.llm.generate(prompt=prompt)

            intents = response.strip().lower()
            intents = [i.strip() for i in intents.split(",") if i.strip()]

            return intents

        except:
            return ["general"]

    # =========================
    # 🔥 CONTROL LAYER (FIXED POSITION)
    # =========================
    def control_layer(self, user_input: str):
        text = user_input.lower()
        intents = self.classify_intent(user_input)

        print(f"DEBUG: Intents → {intents}")

        steps = []

        if "load_document" in intents:
            match = re.search(
                r'["\']?([A-Za-z]:\\[^"\']+\.(pdf|txt|md))["\']?',
                user_input
            )

            if match:
                file_path = match.group(1).strip()

                steps.append({
                    "action": "load_document",
                    "args": {"file_path": file_path}
                })
            else:
                steps.append({
                    "action": "echo",
                    "args": {"text": "Could not detect a valid file path."}
                })

        if "summarize" in intents:
            steps.append({
                "action": "rag_search",
                "args": {"query": "summary of loaded document"}
            })

        if "explain" in intents:
            steps.append({
                "action": "rag_search",
                "args": {"query": user_input}
            })

        if "open_website" in intents or text.startswith("open"):
            sites = {
                "youtube": "https://youtube.com",
                "google": "https://www.google.com",
                "coursera": "https://www.coursera.org",
                "spotify": "https://www.spotify.com",
                "github": "https://github.com"
            }

            words = text.replace("open", "").split()

            for word in words:
                match = get_close_matches(word, sites.keys(), n=1, cutoff=0.7)
                if match:
                    steps.append({
                        "action": "open_website",
                        "args": {"url": sites[match[0]]}
                    })

        if steps:
            print("DEBUG: Control layer triggered")
            return Plan(steps=steps)

        return None

    # =========================
    # 🤖 MAIN PLANNER (FIXED POSITION)
    # =========================
    def plan(self, user_input: str, max_retries: int = 2):
        controlled = self.control_layer(user_input)

        if controlled is not None:
            return controlled

        tool_info = self.build_tool_prompt()

        system_prompt = f"""
You are an AI planner.

Convert user input into a sequence of actions.

Available actions:
{tool_info}

CRITICAL RULES:
- Output ONLY valid JSON
- No explanation
- No markdown
- No extra text
- ALWAYS return a list of steps
- DO NOT invent actions
- DO NOT use "exit"
- DO NOT use unknown keys

STRICT ARGUMENT RULES:
- load_document MUST use key: file_path
- file_path MUST NOT contain quotes
- open_website MUST include full URL
- rag_search MUST include meaningful query

Format:

{{
  "steps": [
    {{"action": "...", "args": {{...}}}},
    {{"action": "...", "args": {{...}}}}
  ]
}}
"""

        for attempt in range(max_retries):
            response = self.llm.generate(
                prompt=user_input,
                system_prompt=system_prompt
            )

            print(f"DEBUG: Attempt {attempt+1} response:", response)

            try:
                cleaned = extract_json(response)

                if not cleaned:
                    cleaned = response.strip()

                data = json.loads(cleaned)

                if isinstance(data, list):
                    data = {"steps": data}

                return Plan(**data)

            except Exception as e:
                print(f"ERROR (attempt {attempt+1}):", e)

        return None
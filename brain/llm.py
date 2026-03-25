import ollama
from config.settings import settings

DEFAULT_SYSTEM_PROMPT = "You are JARVIS. Be concise and avoid unnecessary greetings."

class LLM:
    def __init__(self):
        self.model = settings.model_name

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

        print(f"DEBUG: Using model: {self.model}")
        print("DEBUG: Sending request to Ollama...")

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": settings.temperature,
                    "num_predict": 200
                }
            )
        except Exception as e:
            print("ERROR:", e)
            return "⚠️ JARVIS encountered an error."

        print("DEBUG: Received response")

        return response.get("message", {}).get("content", "⚠️ Empty response from model.").strip()
from planner.schema import Plan
from difflib import get_close_matches
import re


def is_high_confidence(intents):
    simple = {"open_website", "load_document"}
    return len(intents) == 1 and list(intents)[0] in simple


def control_layer(user_input: str, intents: list):
    text = user_input.lower()

    print(f"DEBUG: Intents → {intents}")

    steps = []

    # =========================
    # 📄 LOAD DOCUMENT
    # =========================
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

    # =========================
    # 📚 SUMMARIZE
    # =========================
    if "summarize" in intents:
        if "load_document" in intents:
            steps.append({
                "action": "rag_search",
                "args": {"query": "summary of loaded document"}
            })
        else:
            steps.append({
                "action": "rag_search",
                "args": {"query": user_input}
            })

    # =========================
    # 🌐 OPEN WEBSITE
    # =========================
    if "open_website" in intents or text.startswith("open"):
        sites = {
            "youtube": "https://youtube.com",
            "google": "https://www.google.com",
            "coursera": "https://www.coursera.org",
            "spotify": "https://www.spotify.com",
            "github": "https://github.com",
            "hotstar": "https://www.hotstar.com"
        }

        words = text.replace("open", "").split()

        for word in words:
            match = get_close_matches(word, sites.keys(), n=1, cutoff=0.7)
            if match:
                steps.append({
                    "action": "open_website",
                    "args": {"url": sites[match[0]]}
                })

    # =========================
    # ✅ CONFIDENCE GATE
    # =========================
    if steps and is_high_confidence(intents):
        print("DEBUG: Control layer triggered (high confidence)")
        return Plan(steps=steps)

    return None
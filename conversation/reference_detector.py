import re


REFERENCE_WORDS = {
    "it",
    "its",
    "they",
    "them",
    "their",
    "this",
    "that",
    "these",
    "those",
}


def contains_reference(user_input: str) -> bool:
    """
    Return True when the user input contains a known
    conversational reference/pronoun.
    """
    pattern = r"\b(" + "|".join(REFERENCE_WORDS) + r")\b"

    return bool(re.search(pattern, user_input.lower()))

def extract_reference(user_input: str) -> str | None:
    for word in user_input.lower().split():
        if word in REFERENCE_WORDS:
            return word
    return None
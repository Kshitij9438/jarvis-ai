from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CanonicalQuery:
    """
    Canonical semantic representation of a user query.

    This component owns deterministic query normalization only.
    It does not perform:
    - tool selection
    - argument extraction
    - validation
    - execution
    - LLM calls
    """

    value: str

    @classmethod
    def from_text(cls, query: str | None) -> "CanonicalQuery":
        return cls(value=cls._canonicalize(query))

    @staticmethod
    def _canonicalize(query: str | None) -> str:
        if not query:
            return ""

        query = query.lower().strip()

        # Preserve the existing TaskBuilder cleanup behavior.
        fillers = [
            "please",
            "can you",
            "could you",
            "tell me",
            "give me",
            "i want to know",
            "explain",
            "what is",
            "who is",
        ]

        for filler in fillers:
            query = query.replace(filler, " ")

        # Preserve the existing PlanOptimizer noise removal behavior.
        noise_words = {
            "again",
            "please",
            "now",
            "once",
            "more",
            "me",
            "about",
            "on",
            "in",
            "the",
            "a",
            "an",
        }

        words = [
            word
            for word in query.split()
            if word not in noise_words
        ]
        query = " ".join(words)

        # Preserve existing synonym normalization.
        synonyms = {
            "artificial intelligence": "ai",
            "machine learning": "ml",
            "deep learning": "dl",
        }

        for phrase, replacement in synonyms.items():
            query = query.replace(phrase, replacement)

        # Preserve existing learning-pattern normalization.
        learning_patterns = [
            r"how to (.+)",
            r"learn (.+)",
            r"teach me (.+)",
            r"understand (.+)",
            r"guide me (.+)",
        ]

        for pattern in learning_patterns:
            match = re.search(pattern, query)

            if match:
                topic = match.group(1).strip()

                for phrase, replacement in synonyms.items():
                    topic = topic.replace(
                        phrase,
                        replacement,
                    )

                return f"{topic} basics"

        # Preserve existing duplicate-word removal.
        words = query.split()
        seen = set()
        cleaned = []

        for word in words:
            if word not in seen:
                seen.add(word)
                cleaned.append(word)

        return " ".join(cleaned).strip()

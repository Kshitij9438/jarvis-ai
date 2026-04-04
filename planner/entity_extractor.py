import re
from brain.llm import LLM


class EntityExtractor:
    def __init__(self):
        self.llm = LLM()

        # 🔥 Config
        self.OPEN_KEYWORDS = ["open", "launch", "go to", "visit", "browse"]

        self.STOPWORDS = {
            "and", "then", "also", "with", "no", "url",
            "the", "a", "an", "please", "me", "for"
        }

        self.KNOWN_SITES = {
            "youtube", "google", "github", "spotify",
            "netflix", "amazon", "leetcode", "coursera"
        }

        self.LEARN_WORDS = {
            "learn", "teach", "study", "understand", "how"
        }

        self.FILLER_WORDS = {"from", "on", "using"}

    def extract(self, user_input: str) -> dict:
        text = user_input.lower()

        entities = {
            "websites": [],
            "file_path": None,
            "topics": []
        }

        # =========================
        # 📄 FILE PATH
        # =========================
        match = re.search(
            r'["\']?([A-Za-z]:\\[^"\']+\.(pdf|txt|md))["\']?',
            user_input
        )
        if match:
            entities["file_path"] = match.group(1).strip()

        # =========================
        # 🧠 SEGMENTATION
        # =========================
        segments = re.split(r",| and | then ", text)

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            words = segment.split()

            # =========================
            # 🌐 WEBSITE EXTRACTION
            # =========================
            for word in words:
                word = word.strip()

                if not word or word in self.STOPWORDS:
                    continue

                if word in self.KNOWN_SITES:
                    entities["websites"].append(word)
                    continue

                if "." in word:
                    entities["websites"].append(word)
                    continue

            # =========================
            # 🧠 TOPIC EXTRACTION
            # =========================

            # 👉 Case 1: "explain X"
            if "explain" in segment:
                match = re.search(r"explain (.+)", segment)
                if match:
                    topic = match.group(1).strip()
                    if topic:
                        entities["topics"].append(topic)
                        continue

            # 👉 Case 2: learn/teach pattern (FIXED)
            if any(w in segment for w in self.LEARN_WORDS):
                topic_words = []

                for word in words:
                    word = word.strip()

                    if not word:
                        continue

                    if word in self.LEARN_WORDS:
                        continue

                    if word in self.KNOWN_SITES:
                        continue

                    if word in self.STOPWORDS:
                        continue

                    if word in self.FILLER_WORDS:
                        continue

                    topic_words.append(word)

                topic = " ".join(topic_words)

                if topic:
                    entities["topics"].append(topic)

        # =========================
        # 🧠 FALLBACK TOPIC
        # =========================
        if not entities["topics"]:
            words = text.split()

            filtered = [
                w for w in words
                if w not in self.STOPWORDS and w not in self.KNOWN_SITES
            ]

            if filtered:
                entities["topics"].append(" ".join(filtered))

        return entities
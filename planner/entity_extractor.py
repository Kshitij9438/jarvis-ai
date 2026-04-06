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
        # 📄 FILE PATH (FIXED - PRECISE)
        # =========================
        match = re.search(
    r'([A-Za-z0-9_\-\\/:]+?\.(pdf|txt|md))',
    user_input)

        if match:
            path = match.group(1).strip()
            # 🔥 clean accidental prefixes like "summarize "
            path = re.sub(r'^(summarize|open|load)\s+', '', path, flags=re.IGNORECASE)

            entities["file_path"] = path.lower()

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
            # 🌐 WEBSITE EXTRACTION (FIXED)
            # =========================
            for word in words:
                word = word.strip()

                if not word or word in self.STOPWORDS:
                    continue

                # ❌ skip file-like things
                if re.search(r"\.(pdf|txt|md)$", word):
                    continue

                # ✅ known sites
                if word in self.KNOWN_SITES:
                    entities["websites"].append(word)
                    continue

                # ✅ domain-like (but not file)
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

            # 👉 Case 2: learn/teach pattern
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

                    # ❌ skip file-like
                    if re.search(r"\.(pdf|txt|md)$", word):
                        continue

                    topic_words.append(word)

                topic = " ".join(topic_words)

                if topic:
                    entities["topics"].append(topic)

        # =========================
        # 🧠 CLEANUP (CRITICAL FIX)
        # =========================

        # ❌ remove file_path from websites if mistakenly added
        if entities["file_path"]:
            entities["websites"] = [
                w for w in entities["websites"]
                if entities["file_path"] not in w
            ]

        # =========================
        # 🧠 FALLBACK TOPIC
        # =========================
        if not entities["topics"]:
            words = text.split()

            filtered = [
                w for w in words
                if w not in self.STOPWORDS
                and w not in self.KNOWN_SITES
                and not re.search(r"\.(pdf|txt|md)$", w)
            ]

            if filtered:
                entities["topics"].append(" ".join(filtered))
        # =========================
        # 🧠 REMOVE INVALID TOPICS
        # =========================
        INVALID_TOPICS = {"explain", "summarize", "open", "load"}

        entities["topics"] = [
    t for t in entities["topics"]
    if t.strip() not in INVALID_TOPICS
]

        return entities
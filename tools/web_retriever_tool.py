from tools.base import BaseTool
from pydantic import BaseModel

from retriever.web_fetcher import WebFetcher
from retriever.text_extractor import TextExtractor

from urllib.parse import quote
from bs4 import BeautifulSoup


class WebRetrieverArgs(BaseModel):
    query: str


class WebRetrieverTool(BaseTool):
    name = "web_retriever"
    description = "Retrieve and answer using web pages (Wikipedia-focused retrieval)"

    intents = [
        "learn",
        "explain",
        "understand",
        "what is",
        "who is",
        "concept"
    ]

    entities = ["internet", "web", "online"]

    priority = 3
    args_schema = WebRetrieverArgs

    def __init__(self, llm):
        self.fetcher = WebFetcher()
        self.extractor = TextExtractor()
        self.llm = llm

    # =========================
    # 🧠 EXTRACT ENTITY + INTENT (FIXED)
    # =========================
    def _extract_entity_intent(self, query: str):
        q = query.lower().strip()

        # 🔥 detect intent
        intent_keywords = ["ceo", "founder", "president", "capital"]

        intent = None
        for word in intent_keywords:
            if word in q:
                intent = word
                break

        # 🔥 smarter entity extraction
        entity = q

        # case 1: "X of Y"
        if " of " in q:
            entity = q.split(" of ")[-1]

        # case 2: "who is Y"
        elif q.startswith("who is"):
            entity = q.replace("who is", "")

        # case 3: "what is Y"
        elif q.startswith("what is"):
            entity = q.replace("what is", "")

        # remove noise
        noise = [
            "current", "the", "a", "an",
            "please", "tell me", "explain"
        ]

        for word in noise:
            entity = entity.replace(word, "")

        entity = entity.strip()

        return entity, intent

    # =========================
    # 🔗 DIRECT WIKI URL
    # =========================
    def _direct_url(self, entity: str):
        q = entity.replace(" ", "_")
        return f"https://en.wikipedia.org/wiki/{q}"

    # =========================
    # 🔍 WIKI SEARCH FALLBACK
    # =========================
    def _search_wikipedia(self, entity: str):
        search_url = f"https://en.wikipedia.org/w/index.php?search={quote(entity)}"

        html = self.fetcher.fetch(search_url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        for link in soup.select("a.mw-search-result-heading"):
            href = link.get("href")
            if href:
                return "https://en.wikipedia.org" + href

        return None

    # =========================
    # 🚀 RUN
    # =========================
    def run(self, **kwargs):
        query = kwargs.get("query", "")

        if not query:
            return "⚠️ No query provided"

        entity, intent = self._extract_entity_intent(query)

        urls_to_try = []

        # 🔹 primary
        urls_to_try.append(self._direct_url(entity))

        # 🔹 fallback
        fallback_url = self._search_wikipedia(entity)
        if fallback_url:
            urls_to_try.append(fallback_url)

        all_text = ""

        for url in urls_to_try:
            html = self.fetcher.fetch(url)

            # 🔥 DEBUG (keep for now)
            print("DEBUG URL:", url)
            print("DEBUG HTML LENGTH:", len(html))

            text = self.extractor.extract(html)

            if text and len(text) > 200:
                all_text = text[:4000]
                break

        if not all_text:
            return "⚠️ Could not retrieve useful content."

        # =========================
        # 🧠 SMART PROMPT
        # =========================
        if intent:
            instruction = f"Find the {intent} of {entity} from the context."
        else:
            instruction = "Answer the question."

        prompt = f"""
{instruction}

Question: {query}

Context:
{all_text}

Give a precise answer only. No extra explanation.
"""

        return self.llm.generate_text(prompt)
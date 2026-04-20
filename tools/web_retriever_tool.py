from tools.base import BaseTool
from pydantic import BaseModel

from retriever.web_fetcher import WebFetcher
from retriever.text_extractor import TextExtractor

from ddgs import DDGS
import wikipedia
from urllib.parse import urlparse


class WebRetrieverArgs(BaseModel):
    query: str


class WebRetrieverTool(BaseTool):
    name = "web_retriever"
    description = "Retrieve relevant information from the internet using reliable sources"

    intents = ["learn", "explain", "understand", "what is", "who is", "concept"]
    entities = ["internet", "web", "online"]

    priority = 3
    args_schema = WebRetrieverArgs

    MAX_URLS = 4
    PER_SOURCE_CHARS = 1200
    TOTAL_CHARS = 4000

    def __init__(self, llm):
        self.fetcher = WebFetcher()
        self.extractor = TextExtractor()
        self.llm = llm

    # =========================
    # 🧠 CLEAN QUERY
    # =========================
    def _clean_query(self, query: str):
        q = query.lower().strip()

        fillers = [
            "please", "can you", "could you",
            "tell me", "give me", "i want to know"
        ]

        for f in fillers:
            if q.startswith(f):
                q = q[len(f):].strip()

        return " ".join(q.split())

    # =========================
    # 🥇 WIKIPEDIA FAST PATH
    # =========================
    def _wiki_summary(self, query):
        try:
            summary = wikipedia.summary(query, sentences=3)

            page = wikipedia.page(query)
            print("DEBUG WIKI SUCCESS")

            return [{
                "url": page.url,
                "domain": "wikipedia",
                "text": summary
            }]

        except Exception as e:
            print("DEBUG WIKI FAILED:", e)
            return []

    # =========================
    # 🥈 DUCKDUCKGO SEARCH
    # =========================
    def _search_urls(self, query):
        urls = []

        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=self.MAX_URLS)

                for r in results:
                    href = r.get("href")
                    if href:
                        urls.append(href)

        except Exception as e:
            print("DEBUG SEARCH ERROR:", e)

        print(f"DEBUG URLS FOUND: {len(urls)}")
        return urls

    # =========================
    # 🧹 TEXT FILTER
    # =========================
    def _is_valid_text(self, text):
        return text and len(text.split()) > 40

    # =========================
    # 🚀 RUN
    # =========================
    def run(self, **kwargs):
        raw_query = kwargs.get("query", "")

        if not raw_query:
            return "⚠️ No query provided"

        query = self._clean_query(raw_query)
        print(f"DEBUG QUERY: {query}")

        sources = []

        # =========================
        # 🥇 WIKIPEDIA FIRST
        # =========================
        sources.extend(self._wiki_summary(query))

        # =========================
        # 🥈 WEB SEARCH
        # =========================
        urls = self._search_urls(query)

        for url in urls:
            html = self.fetcher.fetch(url)

            if not html:
                continue

            text = self.extractor.extract(html)

            if not self._is_valid_text(text):
                continue

            domain = urlparse(url).netloc

            sources.append({
                "url": url,
                "domain": domain,
                "text": text[:self.PER_SOURCE_CHARS]
            })

        if not sources:
            return "⚠️ Could not retrieve useful content."

        # =========================
        # 🧠 MERGE
        # =========================
        context_parts = []

        for i, src in enumerate(sources[:self.MAX_URLS], 1):
            context_parts.append(
                f"[Source {i}: {src['domain']}]\n{src['text']}"
            )

        merged = "\n\n---\n\n".join(context_parts)

        print(f"DEBUG FINAL SOURCES: {len(context_parts)}")

        return merged[:self.TOTAL_CHARS]
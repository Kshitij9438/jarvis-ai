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

    BLOCKED_DOMAINS = {
        "youtube.com", "facebook.com", "instagram.com",
        "twitter.com", "tiktok.com", "pinterest.com"
    }

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
    # 🥇 WIKIPEDIA (ROBUST)
    # =========================
    def _wiki_summary(self, query):
        try:
            # Try direct
            try:
                summary = wikipedia.summary(query, sentences=3)
                page = wikipedia.page(query)
                print("DEBUG WIKI DIRECT SUCCESS")
                return [{
                    "url": page.url,
                    "domain": "wikipedia",
                    "text": summary
                }]
            except:
                pass

            # Fallback → search best match
            results = wikipedia.search(query)

            if results:
                best = results[0]
                summary = wikipedia.summary(best, sentences=3)
                page = wikipedia.page(best)

                print(f"DEBUG WIKI SEARCH SUCCESS: {best}")

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
        seen = set()

        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=self.MAX_URLS * 2)

                for r in results:
                    href = r.get("href")

                    if not href:
                        continue

                    domain = urlparse(href).netloc.lower()

                    # filter junk domains
                    if any(b in domain for b in self.BLOCKED_DOMAINS):
                        continue

                    if domain in seen:
                        continue

                    seen.add(domain)
                    urls.append(href)

                    if len(urls) >= self.MAX_URLS:
                        break

        except Exception as e:
            print("DEBUG SEARCH ERROR:", e)

        print(f"DEBUG URLS FOUND: {len(urls)}")
        return urls

    # =========================
    # 🧹 TEXT FILTER
    # =========================
    def _is_valid_text(self, text):
        if not text:
            return False

        words = text.split()

        if len(words) < 40:
            return False

        avg_len = sum(len(w) for w in words) / len(words)

        if avg_len < 3:
            return False

        return True

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
        wiki_sources = self._wiki_summary(query)
        sources.extend(wiki_sources)

        # =========================
        # 🥈 WEB SEARCH
        # =========================
        urls = self._search_urls(query)

        for url in urls:
            html = self.fetcher.fetch(url)

            if not html:
                print(f"DEBUG FETCH FAIL: {url}")
                continue

            text = self.extractor.extract(html)

            if not self._is_valid_text(text):
                print(f"DEBUG LOW QUALITY: {url}")
                continue

            domain = urlparse(url).netloc

            sources.append({
                "url": url,
                "domain": domain,
                "text": text[:self.PER_SOURCE_CHARS]
            })

        # =========================
        # ❌ NO DATA
        # =========================
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
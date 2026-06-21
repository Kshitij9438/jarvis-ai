from tools.base import BaseTool
from pydantic import BaseModel

from retriever.web_fetcher import WebFetcher
from retriever.text_extractor import TextExtractor
from retriever.reranker import Reranker

from ddgs import DDGS
import wikipedia
from urllib.parse import urlparse


class WebRetrieverArgs(BaseModel):
    query: str


# =========================
# 🧠 QUERY ENGINE (FIXED)
# =========================
class QueryEngine:
    def __init__(self, llm):
        self.llm = llm

    def expand(self, query: str):
        prompt = f"""
Generate 3 search queries.

STRICT RULES:
- MUST include MAIN concept
- DO NOT change topic
- ONLY keyword phrases
- MAX 5 words
- NO questions
- NO explanations

Example:
Input: What is gradient descent

Output:
gradient descent machine learning
gradient descent example
gradient descent vs stochastic gradient

Query:
{query}
"""

        response = self.llm.generate_text(
            prompt,
            system_prompt="Generate strict keyword search queries."
        )

        if not response:
            return [query]

        queries = [
            q.strip("- ").strip().lower()
            for q in response.split("\n")
            if q.strip()
        ]

        # 🔥 HARD ANCHOR ENFORCEMENT
        anchor_words = query.lower().split()[:2]
        anchor = anchor_words[0] if anchor_words else ""

        filtered = []
        for q in queries:
            if anchor and anchor not in q:
                continue

            words = q.split()

            # remove garbage queries
            if len(words) > 6:
                continue

            if len(words) <= 2 and any(w in q for w in ["algorithm", "method", "technique"]):
                continue

            filtered.append(q)

        return filtered[:3] if filtered else [query]


# =========================
# 🌐 WEB RETRIEVER TOOL
# =========================
class WebRetrieverTool(BaseTool):
    name = "web_retriever"
    description = "Retrieve relevant information from the internet"

    intents = ["learn", "explain", "understand", "what is", "who is", "concept"]
    entities = ["internet", "web", "online"]

    priority = 3
    args_schema = WebRetrieverArgs

    requires_context = []
    produces_context = ["web"]

    MAX_URLS = 5
    FINAL_TOP_K = 4
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
        self.reranker = Reranker()
        self.query_engine = QueryEngine(llm)

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
    # 🥇 WIKIPEDIA
    # =========================
    def _wiki_summary(self, query):
        try:
            summary = wikipedia.summary(query, sentences=3)
            page = wikipedia.page(query)
            return [{
                "url": page.url,
                "domain": "wikipedia",
                "text": summary
            }]
        except:
            return []

    # =========================
    # 🔎 SEARCH
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

        return urls

    # =========================
    # 🧹 TEXT FILTER
    # =========================
    def _is_valid_text(self, text):
        if not text:
            return False

        words = text.split()
        return len(words) >= 40

    # =========================
    # 🌐 MULTI RETRIEVE
    # =========================
    def _retrieve_multi(self, queries):
        sources = []

        for q in queries:
            print(f"[Multi-Search] → {q}")

            sources.extend(self._wiki_summary(q))

            urls = self._search_urls(q)

            for url in urls:
                html = self.fetcher.fetch(url)
                if not html:
                    continue

                text = self.extractor.extract(html)

                if not self._is_valid_text(text):
                    continue

                sources.append({
                    "url": url,
                    "domain": urlparse(url).netloc,
                    "text": text[:self.PER_SOURCE_CHARS]
                })

        return sources

    # =========================
    # 🧠 DEDUP (IMPROVED)
    # =========================
    def _deduplicate(self, sources):
        seen = set()
        unique = []

        for s in sources:
            key = (s["domain"], s["text"][:150])

            if key in seen:
                continue

            seen.add(key)
            unique.append(s)

        return unique

    # =========================
    # 🚀 RUN
    # =========================
    def run(self, **kwargs):
        raw_query = kwargs.get("query", "")

        if not raw_query:
            return "⚠️ No query provided"

        query = self._clean_query(raw_query)
        print(f"DEBUG QUERY: {query}")

        # 1️⃣ EXPAND
        queries = self.query_engine.expand(query)
        print("DEBUG EXPANDED:", queries)

        # 2️⃣ RETRIEVE
        sources = self._retrieve_multi(queries)

        if not sources:
            return "⚠️ Could not retrieve useful content."

        print(f"DEBUG BEFORE DEDUP: {len(sources)}")

        # 3️⃣ DEDUP
        sources = self._deduplicate(sources)
        print(f"DEBUG AFTER DEDUP: {len(sources)}")

        # 4️⃣ RERANK (SAFE MAPPING)
        texts = [s["text"] for s in sources]
        ranked_texts = self.reranker.rerank(query, texts, self.FINAL_TOP_K)

        ranked_sources = []
        for rt in ranked_texts:
            for s in sources:
                if s["text"] == rt:
                    ranked_sources.append(s)
                    break

        sources = ranked_sources[:self.FINAL_TOP_K]
        print(f"DEBUG AFTER RERANK: {len(sources)}")

        # 5️⃣ MERGE (NO GENERATION)
        context_parts = []

        for i, src in enumerate(sources, 1):
            context_parts.append(
                f"[Source {i}: {src['domain']}]\n{src['text']}"
            )

        merged = "\n\n---\n\n".join(context_parts)

        return merged[:self.TOTAL_CHARS]
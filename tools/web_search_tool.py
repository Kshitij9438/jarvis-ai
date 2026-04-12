from tools.base import BaseTool
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, parse_qs, unquote
import time


class WebSearchArgs(BaseModel):
    query: str


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web and return structured results with URLs"

    intents = ["latest", "news", "current", "recent", "today", "update"]
    entities = ["internet", "web", "online", "news"]

    priority = 3
    args_schema = WebSearchArgs

    def __init__(self, llm=None):
        self.llm = llm

    # =========================
    # 🔍 FETCH
    # =========================
    def _fetch(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        for _ in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                return response.text
            except:
                time.sleep(1)

        return None

    # =========================
    # 🔧 EXTRACT REAL URL (CRITICAL FIX)
    # =========================
    def _extract_url(self, href):
        try:
            if "uddg=" in href:
                parsed = urlparse(href)
                query = parse_qs(parsed.query)
                real_url = query.get("uddg", [None])[0]
                if real_url:
                    return unquote(real_url)
            return href
        except:
            return None

    # =========================
    # 🔍 SEARCH (FIXED)
    # =========================
    def _search(self, query: str):
        url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
        html = self._fetch(url)

        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        results = []

        # ✅ PRIMARY: DuckDuckGo result links
        for link in soup.select("a.result__a"):
            href = link.get("href")
            title = link.get_text(strip=True)

            real_url = self._extract_url(href)

            if not real_url or not title:
                continue

            results.append({
                "title": title,
                "url": real_url
            })

            if len(results) >= 5:
                return results

        # 🔁 FALLBACK: generic parsing
        for link in soup.find_all("a", href=True):
            href = link["href"]
            title = link.get_text(strip=True)

            real_url = self._extract_url(href)

            if not real_url:
                continue

            if not title or len(title) < 25:
                continue

            if "duckduckgo.com" in real_url:
                continue

            results.append({
                "title": title,
                "url": real_url
            })

            if len(results) >= 5:
                break

        return results

    # =========================
    # 🚀 RUN
    # =========================
    def run(self, **kwargs):
        query = kwargs.get("query", "")

        if not query:
            return "⚠️ No query provided"

        try:
            results = self._search(query)

            if not results:
                return "⚠️ No useful results found."

            return {
                "query": query,
                "results": results
            }

        except Exception as e:
            return f"⚠️ Web search error: {str(e)}"
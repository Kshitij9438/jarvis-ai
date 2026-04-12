import requests


class WebFetcher:
    def fetch(self, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml"
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10,
                allow_redirects=True
            )

            # 🔥 FORCE proper encoding
            response.encoding = "utf-8"

            if response.status_code == 200 and len(response.text) > 1000:
                return response.text

            return ""

        except Exception as e:
            print("FETCH ERROR:", e)
            return ""
import requests
import time


class WebFetcher:

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "DNT": "1",
    }

    def fetch(self, url: str, retries: int = 2) -> str:
        for attempt in range(retries):
            try:
                response = requests.get(
                    url,
                    headers=self.HEADERS,
                    timeout=10,
                    allow_redirects=True
                )

                # ✅ Accept any 2xx (DDG returns 202 sometimes)
                if 200 <= response.status_code < 300:
                    response.encoding = response.apparent_encoding  # 🔥 FIX
                    text = response.text

                    # 🔥 Reject useless pages early
                    if len(text) < 500:
                        print(f"DEBUG SHORT HTML: {url}")
                        return ""

                    return text

                print(f"DEBUG FETCH STATUS {response.status_code}: {url}")

                # 🔁 Retry logic
                if response.status_code == 429:
                    print("DEBUG: Rate limited — waiting 2s")
                    time.sleep(2)

                elif response.status_code >= 500:
                    time.sleep(1)

            except requests.exceptions.Timeout:
                print(f"DEBUG FETCH TIMEOUT (attempt {attempt + 1}): {url}")

            except requests.exceptions.ConnectionError:
                print(f"DEBUG FETCH CONNECTION ERROR (attempt {attempt + 1}): {url}")

            except Exception as e:
                print(f"DEBUG FETCH ERROR (attempt {attempt + 1}): {e}")

        return ""
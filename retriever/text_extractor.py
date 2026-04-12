from bs4 import BeautifulSoup


class TextExtractor:
    def extract(self, html: str) -> str:
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")

        # remove noise
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        extracted = []

        # =========================
        # 🔥 1. INFOBOX (CRITICAL FIX)
        # =========================
        infobox = soup.find("table", {"class": "infobox"})
        if infobox:
            rows = infobox.find_all("tr")
            for row in rows:
                header = row.find("th")
                value = row.find("td")

                if header and value:
                    key = header.get_text(" ", strip=True)
                    val = value.get_text(" ", strip=True)

                    extracted.append(f"{key}: {val}")

        # =========================
        # 🔥 2. PARAGRAPHS
        # =========================
        paragraphs = [
            p.get_text(strip=True)
            for p in soup.find_all("p")
        ]

        paragraphs = [p for p in paragraphs if len(p) > 50]

        extracted.extend(paragraphs[:20])

        return "\n".join(extracted)
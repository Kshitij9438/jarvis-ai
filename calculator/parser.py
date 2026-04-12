import re
from typing import Optional


class CalculatorParser:
    def parse(self, text: str) -> Optional[str]:
        text = self._normalize(text)

        return (
            self._parse_percent(text)
            or self._parse_power(text)
            or self._parse_sqrt(text)
            or self._parse_binary(text)
        )

    # =========================
    # 🧠 NORMALIZATION
    # =========================
    def _normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\b(what is|calculate|compute|evaluate|please)\b", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # =========================
    # 🔥 PERCENT
    # =========================
    def _parse_percent(self, text: str) -> Optional[str]:
        match = re.search(r"(\d+(?:\.\d+)?)\s*(percent|%)\s*(of)?\s*(\d+(?:\.\d+)?)", text)
        if match:
            return f"({match.group(1)}/100)*{match.group(4)}"
        return None

    # =========================
    # 🔥 POWER
    # =========================
    def _parse_power(self, text: str) -> Optional[str]:
        nums = re.findall(r"\d+(?:\.\d+)?", text)
        if not nums:
            return None

        if "square" in text:
            return f"{nums[0]}**2"
        if "cube" in text:
            return f"{nums[0]}**3"

        return None

    # =========================
    # 🔥 SQRT
    # =========================
    def _parse_sqrt(self, text: str) -> Optional[str]:
        if "sqrt" in text or "square root" in text:
            nums = re.findall(r"\d+(?:\.\d+)?", text)
            if nums:
                return f"{nums[0]}**0.5"
        return None

    # =========================
    # 🔥 BINARY ENGINE (UPGRADED)
    # =========================
    def _parse_binary(self, text: str) -> Optional[str]:

        # operator definitions
        operations = [
            {
                "name": "divide",
                "symbols": ["divided by", "divide"],
                "operator": "/"
            },
            {
                "name": "multiply",
                "symbols": ["multiplied by", "multiply"],
                "operator": "*"
            },
            {
                "name": "add",
                "symbols": ["plus", "add"],
                "operator": "+"
            },
            {
                "name": "subtract",
                "symbols": ["minus", "subtract"],
                "operator": "-"
            }
        ]

        for op in operations:
            for phrase in op["symbols"]:

                # =========================
                # Case 1: "A op B"
                # =========================
                pattern1 = rf"(\d+(?:\.\d+)?)\s*{phrase}\s*(\d+(?:\.\d+)?)"
                match1 = re.search(pattern1, text)
                if match1:
                    a, b = match1.group(1), match1.group(2)
                    return f"{a}{op['operator']}{b}"

                # =========================
                # Case 2: "op A by B"
                # =========================
                pattern2 = rf"{phrase}\s*(\d+(?:\.\d+)?)\s*(by|and)?\s*(\d+(?:\.\d+)?)"
                match2 = re.search(pattern2, text)
                if match2:
                    a, b = match2.group(1), match2.group(3)
                    return f"{a}{op['operator']}{b}"

        return None
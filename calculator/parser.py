import re
from typing import Optional


class CalculatorParser:
    def parse(self, text: str) -> Optional[str]:
        text = self._normalize(text)

        # 🔥 1. DIRECT EXPRESSION (NEW — CRITICAL)
        direct = self._parse_direct_expression(text)
        if direct:
            return direct

        # 🔁 fallback pipeline
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

        # remove common filler phrases
        text = re.sub(
            r"\b(what is|calculate|compute|evaluate|please|tell me|give me)\b",
            "",
            text
        )

        # remove chaining words
        text = re.sub(r"\b(and|then)\b", "", text)

        # normalize spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # =========================
    # 🔥 DIRECT EXPRESSION (NEW)
    # =========================
    def _parse_direct_expression(self, text: str) -> Optional[str]:
        """
        Handles:
        5*6
        (2+3)*4
        10/2 + 5
        2^3
        """

        if re.fullmatch(r"[\d\.\+\-\*/\^\(\)\s]+", text):
            expr = text.replace(" ", "")

            # convert ^ → ** (python format)
            expr = expr.replace("^", "**")

            return expr

        return None

    # =========================
    # 🔥 PERCENT
    # =========================
    def _parse_percent(self, text: str) -> Optional[str]:
        match = re.search(
            r"(\d+(?:\.\d+)?)\s*(percent|%)\s*(of)?\s*(\d+(?:\.\d+)?)",
            text
        )
        if match:
            return f"({match.group(1)}/100)*{match.group(4)}"
        return None

    # =========================
    # 🔥 POWER (UPGRADED)
    # =========================
    def _parse_power(self, text: str) -> Optional[str]:

        # "square of 5"
        match1 = re.search(r"square of (\d+(?:\.\d+)?)", text)
        if match1:
            return f"{match1.group(1)}**2"

        # "5 squared"
        match2 = re.search(r"(\d+(?:\.\d+)?)\s*squared", text)
        if match2:
            return f"{match2.group(1)}**2"

        # "cube of 5"
        match3 = re.search(r"cube of (\d+(?:\.\d+)?)", text)
        if match3:
            return f"{match3.group(1)}**3"

        # "5 cubed"
        match4 = re.search(r"(\d+(?:\.\d+)?)\s*cubed", text)
        if match4:
            return f"{match4.group(1)}**3"

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
    # 🔥 BINARY ENGINE
    # =========================
    def _parse_binary(self, text: str) -> Optional[str]:

        operations = [
            {"symbols": ["divided by", "divide"], "operator": "/"},
            {"symbols": ["multiplied by", "multiply"], "operator": "*"},
            {"symbols": ["plus", "add"], "operator": "+"},
            {"symbols": ["minus", "subtract"], "operator": "-"},
        ]

        for op in operations:
            for phrase in op["symbols"]:

                # Case 1: "A op B"
                pattern1 = rf"(\d+(?:\.\d+)?)\s*{phrase}\s*(\d+(?:\.\d+)?)"
                match1 = re.search(pattern1, text)
                if match1:
                    a, b = match1.group(1), match1.group(2)
                    return f"{a}{op['operator']}{b}"

                # Case 2: "op A by B"
                pattern2 = rf"{phrase}\s*(\d+(?:\.\d+)?)\s*(by|and)?\s*(\d+(?:\.\d+)?)"
                match2 = re.search(pattern2, text)
                if match2:
                    a, b = match2.group(1), match2.group(3)
                    return f"{a}{op['operator']}{b}"

        return None
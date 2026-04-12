from tools.base import BaseTool
from pydantic import BaseModel
import math
import re
import ast
import operator


# =========================
# 📦 ARG SCHEMA
# =========================
class CalculatorArgs(BaseModel):
    expression: str


# =========================
# 🧠 SAFE OPERATORS
# =========================
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


# =========================
# 🧠 SAFE FUNCTIONS
# =========================
SAFE_FUNCTIONS = {
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "abs": abs,
    "round": round,
}


# =========================
# 🔧 SAFE EVALUATOR
# =========================
class SafeEvaluator:
    def eval(self, expression: str):
        node = ast.parse(expression, mode="eval").body
        return self._eval(node)

    def _eval(self, node):
        if isinstance(node, ast.Num):  # numbers
            return node.n

        elif isinstance(node, ast.BinOp):  # binary ops
            return SAFE_OPERATORS[type(node.op)](
                self._eval(node.left),
                self._eval(node.right)
            )

        elif isinstance(node, ast.UnaryOp):  # -x
            return SAFE_OPERATORS[type(node.op)](
                self._eval(node.operand)
            )

        elif isinstance(node, ast.Call):  # functions
            func_name = node.func.id

            if func_name not in SAFE_FUNCTIONS:
                raise ValueError(f"Function '{func_name}' not allowed")

            args = [self._eval(arg) for arg in node.args]
            return SAFE_FUNCTIONS[func_name](*args)

        else:
            raise ValueError("Invalid expression")


# =========================
# 🧠 NORMALIZER (NL → MATH)
# =========================
class ExpressionNormalizer:
    def normalize(self, text: str) -> str:
        text = text.lower()

        # basic replacements
        replacements = {
            "plus": "+",
            "minus": "-",
            "times": "*",
            "multiplied by": "*",
            "x": "*",
            "divide by": "/",
            "divided by": "/",
            "mod": "%",
            "power of": "**",
        }

        for k, v in replacements.items():
            text = text.replace(k, v)

        # remove filler words
        text = re.sub(r"(what is|calculate|compute|evaluate)", "", text)

        return text.strip()
    def normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"divide (\d+(?:\.\d+)?) by (\d+(?:\.\d+)?)", r"\1 / \2", text)
        text = re.sub(r"multiply (\d+(?:\.\d+)?) by (\d+(?:\.\d+)?)", r"\1 * \2", text)
        text = re.sub(r"add (\d+(?:\.\d+)?) and (\d+(?:\.\d+)?)", r"\1 + \2", text)
        text = re.sub(r"subtract (\d+(?:\.\d+)?) from (\d+(?:\.\d+)?)", r"\2 - \1", text)
        replacements = {
        "plus": "+",
        "minus": "-",
        "times": "*",
        "multiplied by": "*",
        "x": "*",
        "divided by": "/",
        "mod": "%",
        "power of": "**",
    }

        for k, v in replacements.items():
            text = text.replace(k, v)
        text = re.sub(r"(what is|calculate|compute|evaluate)", "", text)
        return text.strip()


# =========================
# 🧮 TOOL
# =========================
class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Evaluate mathematical expressions safely"

    intents = [
        "calculate",
        "compute",
        "what is",
        "solve",
        "evaluate",
        "math"
    ]

    entities = [
        "number",
        "expression",
        "equation"
    ]

    args_schema = CalculatorArgs
    priority = 1

    def __init__(self):
        self.evaluator = SafeEvaluator()
        self.normalizer = ExpressionNormalizer()

    def run(self, **kwargs):
        expression = kwargs.get("expression", "")

        if not expression:
            return "⚠️ No expression provided"

        try:
            # normalize NL → math
            clean_expr = self.normalizer.normalize(expression)

            # evaluate safely
            result = self.evaluator.eval(clean_expr)

            return f"🧮 Result: {result}"

        except Exception as e:
            return f"⚠️ Calculation error: {str(e)}"
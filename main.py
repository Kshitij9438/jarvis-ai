from planner.planner import Planner
from executor.executor import Executor
from tools.registry import ToolRegistry
from tools.basic_tools import OpenWebsiteTool, EchoTool
from tools.rag_tool import RAGTool
from tools.load_doc_tool import LoadDocTool
from tools.explain_tool import ExplainTool

from rag.qa import RAGQA
from rag.embedder import Embedder
from rag.store import VectorStore
from rag.retriever import Retriever
from rag.ingestor import Ingestor

from tools.calculator_tool import CalculatorTool

from tools.web_retriever_tool import WebRetrieverTool

# 🔥 NEW
from execution.context import ExecutionContext


if __name__ == "__main__":
    # =========================
    # 🔧 RAG SETUP
    # =========================
    embedder = Embedder()
    store = VectorStore()

    ingestor = Ingestor(embedder, store)
    retriever = Retriever(embedder, store)
    rag = RAGQA(retriever, ingestor)

    # =========================
    # 🔧 TOOL REGISTRY
    # =========================
    registry = ToolRegistry()
    planner = Planner(registry)

    registry.register(OpenWebsiteTool())
    registry.register(EchoTool())
    registry.register(RAGTool(rag))
    registry.register(LoadDocTool(rag))
    registry.register(ExplainTool())
    registry.register(CalculatorTool())
    #registry.register(WebSearchTool(llm=planner.llm))
    registry.register(WebRetrieverTool(planner.llm))

    # =========================
    # 🧠 CORE SYSTEM
    # =========================
    executor = Executor(registry)

    print("JARVIS started. Type 'exit' to quit.")

    while True:
        user_input = input("You: ").strip()

        if any(word in user_input.lower() for word in ["exit", "quit", "bye", "goodbye"]):
            print("JARVIS: Goodbye 👋")
            break

        # =========================
        # 🧠 CREATE CONTEXT (NEW)
        # =========================
        context = ExecutionContext(user_input)

        # =========================
        # 🧠 PLAN
        # =========================
        plan = planner.plan(user_input,context)

        if plan is None or not plan.steps:
            print("⚠️ No valid plan generated.")
            continue

        # 🔥 REMOVE NOISY ECHO STEPS
        plan.steps = [
            step for step in plan.steps
            if not (step.action == "echo" and "open" in str(step.args).lower())
        ]

        print("PLAN:", plan)

        # =========================
        # ⚙️ EXECUTE (CONTEXT-AWARE)
        # =========================
        results = executor.execute(plan, context)

        for result in results:
            print("RESULT:", result)

        # =========================
        # 🧠 DEBUG CONTEXT (OPTIONAL BUT VERY USEFUL)
        # =========================
        print("\n🧠 CONTEXT STATE:")
        print("History:", context.history)
        print("Stored Outputs:", context.tool_outputs)
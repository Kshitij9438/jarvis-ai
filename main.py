from planner.planner import Planner
from executor.executor import Executor
from tools.registry import ToolRegistry
from tools.basic_tools import OpenWebsiteTool, EchoTool
from tools.rag_tool import RAGTool
from tools.load_doc_tool import LoadDocTool  # 🔥 NEW

# 🔥 RAG imports
from rag.qa import RAGQA
from rag.embedder import Embedder
from rag.store import VectorStore
from rag.retriever import Retriever
from rag.ingestor import Ingestor  # 🔥 NEW


if __name__ == "__main__":
    # =========================
    # 🧠 RAG SYSTEM SETUP
    # =========================
    embedder = Embedder()
    store = VectorStore()

    # 🔥 NEW: ingestion system
    ingestor = Ingestor(embedder, store)

    retriever = Retriever(embedder, store)
    rag = RAGQA(retriever)

    # =========================
    # 🧱 TOOL SYSTEM SETUP
    # =========================
    registry = ToolRegistry()
    registry.register(OpenWebsiteTool())
    registry.register(EchoTool())
    registry.register(RAGTool(rag))             # 🔥 RAG tool
    registry.register(LoadDocTool(ingestor))    # 🔥 NEW ingestion tool

    planner = Planner(registry)
    executor = Executor(registry)

    print("JARVIS started. Type 'exit' to quit.")

    # =========================
    # 🔁 MAIN LOOP
    # =========================
    while True:
        user_input = input("You: ").strip()

        if any(word in user_input.lower() for word in ["exit", "quit", "bye", "goodbye"]):
            print("JARVIS: Goodbye 👋")
            break

        plan = planner.plan(user_input)

        if plan is None:
            print("⚠️ Failed to generate plan.")
            continue

        print("PLAN:", plan)

        results = executor.execute(plan)

        for result in results:
            print("RESULT:", result)
from planner.planner import Planner
from executor.executor import Executor
from tools.registry import ToolRegistry

from tools.basic_tools import OpenWebsiteTool, EchoTool
from tools.rag_tool import RAGTool
from tools.load_doc_tool import LoadDocTool
from tools.explain_tool import ExplainTool
from tools.calculator_tool import CalculatorTool
from tools.web_retriever_tool import WebRetrieverTool

from rag.qa import RAGQA
from rag.embedder import Embedder
from rag.store import VectorStore
from rag.retriever import Retriever
from rag.ingestor import Ingestor

from execution.context import ExecutionContext
from control.execution_loop import ExecutionLoop
from app.events import JarvisEvent


class JarvisRuntime:
    """
    Reusable JARVIS application runtime.

    Owns the construction and wiring of the core JARVIS system,
    while keeping clients such as the CLI and GUI independent
    from the internal planner/executor architecture.
    """

    def __init__(self):
        # =========================
        # RAG SETUP
        # =========================
        embedder = Embedder()
        store = VectorStore()

        ingestor = Ingestor(embedder, store)
        retriever = Retriever(embedder, store)
        rag = RAGQA(retriever, ingestor)

        # =========================
        # TOOL REGISTRY
        # =========================
        self.registry = ToolRegistry()
        self.planner = Planner(self.registry)

        self.registry.register(OpenWebsiteTool())
        self.registry.register(EchoTool())
        self.registry.register(RAGTool(rag))
        self.registry.register(LoadDocTool(rag))
        self.registry.register(ExplainTool())
        self.registry.register(CalculatorTool())
        self.registry.register(WebRetrieverTool(self.planner.llm))

        # =========================
        # EXECUTION
        # =========================
        self.executor = Executor(self.registry)
        self.execution_loop = ExecutionLoop(self.executor)

    def run(self, user_input: str, event_callback=None):
        """
        Execute one complete JARVIS request.

        Returns the structured execution results produced by
        ExecutionLoop.
        """
        user_input = user_input.strip()

        if not user_input:
            return {
                "plan": None,
                "results": [],
                "context": None,
            }

        context = ExecutionContext(user_input)

        # =========================
        # PLAN
        # =========================
        plan = self.planner.plan(user_input, context)

        if plan is None or not plan.steps:
            return {
                "plan": None,
                "results": [],
                "context": context,
            }

        # =========================
        # REMOVE NOISY ECHO STEPS
        # =========================
        plan.steps = [
            step
            for step in plan.steps
            if not (
                step.action == "echo"
                and "open" in str(step.args).lower()
            )
        ]

        if not plan.steps:
            return {
                "plan": plan,
                "results": [],
                "context": context,
            }

        # =========================
        # EXECUTE
        # =========================
        results = self.execution_loop.run(
            plan,
            context,
            event_callback=event_callback,
        )

        return {
            "plan": plan,
            "results": results,
            "context": context,
        }

    def run_with_events(self, user_input: str):
        """
        Execute one complete JARVIS request with events.

        Returns the structured execution results produced by
        ExecutionLoop together with events generated during this request.
        """
        events = []

        def emit(event_type, data=None):
            events.append(
                JarvisEvent(
                    type=event_type,
                    data=data or {},
                )
            )

        events.append(
            JarvisEvent(
                type="request started",
                data={"message": user_input},
            )
        )

        response = self.run(
            user_input,
            event_callback=emit,
        )

        events.append(
            JarvisEvent(
                type="request.completed",
                data={
                    "success": bool(response["results"]),
                },
            )
        )

        return response, events
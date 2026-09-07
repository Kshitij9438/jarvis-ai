from uuid import UUID

from planner.planner import Planner
from planner.entity_extractor import EntityExtractor
from planner.decision import DecisionType, PlannerDecision
from planner.request_understanding_adapter import RequestUnderstandingAdapter

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
from control.decision_layer import decision_type_from_user_input
from control.clarification import clarify_question

from app.events import JarvisEvent

from conversation.context import (
    ActiveTopic,
    ConversationEntry,
    IntentModel,
    PendingClarification,
    PendingRequest,
)
from conversation.manager import ConversationManager
from conversation.reference_detector import extract_reference
from conversation.reference_resolver import (
    ReferenceResolutionDecision,
    ReferenceResolver,
)


class JarvisRuntime:
    """
    Reusable JARVIS application runtime.

    Owns the construction and wiring of the core JARVIS system,
    while keeping clients such as the CLI and GUI independent
    from the internal planner/executor architecture.

    Conversation state is owned by ConversationManager.
    Request-scoped execution state remains owned by ExecutionContext.

    EntityExtractor extracts explicit topics/entities from the current
    request. ReferenceResolver resolves conversational references against
    persistent conversation state.
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

        # =========================
        # CONVERSATION STATE
        # =========================
        self.conversation_manager = ConversationManager()

        # =========================
        # REQUEST UNDERSTANDING
        # =========================
        self.entity_extractor = EntityExtractor()
        self.request_understanding_adapter = RequestUnderstandingAdapter(
            self.entity_extractor
        )

    # =========================
    # PUBLIC REQUEST API
    # =========================

    def run(
        self,
        user_input: str,
        conversation_id: UUID | None = None,
        event_callback=None,
    ):
        """
        Execute one complete JARVIS request.

        `conversation_id` identifies the persistent conversation
        associated with this request.

        If no conversation_id is supplied, a new conversation is created.

        ExecutionContext remains request-scoped while ConversationContext
        persists across multiple requests belonging to the same conversation.
        """
        user_input = user_input.strip()
        original_user_input = user_input

        # =========================
        # EMPTY INPUT
        # =========================
        if not user_input:
            return {
                "conversation_id": conversation_id,
                "plan": None,
                "results": [],
                "context": None,
            }

        # =========================
        # CONVERSATION STATE
        # =========================
        conversation = (
            self.conversation_manager.get_or_create_conversation(
                conversation_id
            )
        )

        conversation_id = conversation.conversation_id

        # =========================
        # REQUEST-SCOPED EXECUTION
        # =========================
        context = ExecutionContext(user_input)

        # =========================
        # M5: REFERENCE RESOLUTION
        # =========================
        reference = extract_reference(user_input)

        if reference:
            reference_resolver = ReferenceResolver(conversation)

            resolved_entity, resolution = (
                reference_resolver.resolve_reference(reference)
            )

            # ---------------------------------
            # AMBIGUOUS / UNRESOLVED
            # ---------------------------------
            if resolution in {
                ReferenceResolutionDecision.AMBIGUOUS,
                ReferenceResolutionDecision.UNRESOLVED,
            }:
                clarification = clarify_question(
                    self.planner.llm,
                    user_input,
                )

                conversation.pending_clarification = PendingClarification(
                    clarification_question=clarification.question
                )

                conversation.pending_request = PendingRequest(
                    intent=self.planner.llm.generate_structured(
                        prompt=user_input,
                        schema=IntentModel,
                        system_prompt=(
                            "You are an assistant that receives a user query. "
                            "Extract the intent of the query and return it as a "
                            "structured JSON object. Do not provide any additional "
                            "context or explanation."
                        ),
                    ),
                    missing_information=["reference"],
                    clarification_answer=None,
                )

                self._record_conversation_entry(
                    conversation_id=conversation_id,
                    user_input=original_user_input,
                    assistant_response=clarification.question,
                )

                # Reference ambiguity/unresolvability is already a
                # request-understanding decision. Do not ask the
                # Decision Layer to reinterpret the same request.
                return {
                    "conversation_id": conversation_id,
                    "plan": None,
                    "results": [clarification],
                    "context": context,
                    "decision": PlannerDecision(
                        type=DecisionType.CLARIFY
                    ),
                }

            # ---------------------------------
            # RESOLVED
            # ---------------------------------
            if (
                resolution == ReferenceResolutionDecision.RESOLVED
                and resolved_entity is not None
            ):
                user_input = user_input.replace(
                    reference,
                    resolved_entity,
                )

                reference_resolver.update_context_with_resolution(
                    reference,
                    resolved_entity,
                    resolution,
                )


        # =========================
        # DECISION LAYER
        # =========================
        decision = decision_type_from_user_input(user_input)

        if decision.type == "clarify":
            clarification = clarify_question(
                self.planner.llm,
                user_input,
            )

            conversation.pending_clarification = PendingClarification(
                clarification_question=clarification.question
            )

            conversation.pending_request = PendingRequest(
                intent=self.planner.llm.generate_structured(
                    prompt=user_input,
                    schema=IntentModel,
                    system_prompt=(
                        "You are an assistant that receives a user query. "
                        "Extract the intent of the query and return it as a "
                        "structured JSON object. Do not provide any additional "
                        "context or explanation."
                    ),
                ),
                missing_information=["topic"],
                clarification_answer=None,
            )

            self._record_conversation_entry(
                conversation_id=conversation_id,
                user_input=original_user_input,
                assistant_response=clarification.question,
            )

            return {
                "conversation_id": conversation_id,
                "plan": None,
                "results": [clarification],
                "context": context,
                "decision": decision,
            }

        if decision.type == "reject":
            self._record_conversation_entry(
                conversation_id=conversation_id,
                user_input=original_user_input,
                assistant_response="Request rejected.",
            )

            return {
                "conversation_id": conversation_id,
                "plan": None,
                "results": [],
                "context": context,
                "decision": decision,
            }

        if decision.type == "respond":
            self._record_conversation_entry(
                conversation_id=conversation_id,
                user_input=original_user_input,
                assistant_response="Request responded to without execution.",
            )

            return {
                "conversation_id": conversation_id,
                "plan": None,
                "results": [],
                "context": context,
                "decision": decision,
            }

        # =========================
        # REQUEST UNDERSTANDING
        # =========================
        request_understanding = self.request_understanding_adapter.understand(
            user_input,
            decision,
        )

        # Do not overwrite existing conversational topics when this request
        # is a reference-based follow-up.
        if reference is None:
            topics = []

            for understanding in request_understanding:
                extracted_topics = understanding.entities.get("topics", [])

                for topic in extracted_topics:
                    if topic not in topics:
                        topics.append(topic)

            if topics:
                conversation.active_topic = [
                    ActiveTopic(entity=topic)
                    for topic in topics
                ]

        # EXECUTE -> proceed to planning and execution

        # =========================
        # PLAN
        # =========================
        plan = self.planner.plan(user_input, context)

        if plan is None or not plan.steps:
            self._record_conversation_entry(
                conversation_id=conversation_id,
                user_input=original_user_input,
                assistant_response=None,
            )

            return {
                "conversation_id": conversation_id,
                "plan": None,
                "results": [],
                "context": context,
                "decision": decision,
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
            self._record_conversation_entry(
                conversation_id=conversation_id,
                user_input=original_user_input,
                assistant_response=None,
            )

            return {
                "conversation_id": conversation_id,
                "plan": plan,
                "results": [],
                "context": context,
                "decision": decision,
            }

        # =========================
        # EXECUTE
        # =========================
        results = self.execution_loop.run(
            plan,
            context,
            event_callback=event_callback,
        )

        # =========================
        # UPDATE CONVERSATION STATE
        # =========================
        self._record_conversation_entry(
            conversation_id=conversation_id,
            user_input=original_user_input,
            assistant_response=str(results) if results else None,
        )

        return {
            "conversation_id": conversation_id,
            "plan": plan,
            "results": results,
            "context": context,
            "decision": decision,
        }

    # =========================
    # CONVERSATION RECORDING
    # =========================

    def _record_conversation_entry(
        self,
        conversation_id: UUID,
        user_input: str,
        assistant_response: str | None,
    ) -> None:
        """
        Record one completed request in the persistent conversation.

        Intent and confidence are intentionally left unset for now.
        They belong to the later understanding/decision stages.
        """
        entry = ConversationEntry(
            user_input=user_input,
            assistant_response=assistant_response,
        )

        self.conversation_manager.add_conversation_entry(
            conversation_id,
            entry,
        )

    # =========================
    # EVENT API
    # =========================

    def run_with_events(
        self,
        user_input: str,
        conversation_id: UUID | None = None,
    ):
        """
        Execute one complete JARVIS request with events.

        Returns the structured execution response together with
        events generated during this request.
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
                data={
                    "message": user_input,
                    "conversation_id": conversation_id,
                },
            )
        )

        response = self.run(
            user_input,
            conversation_id=conversation_id,
            event_callback=emit,
        )

        events.append(
            JarvisEvent(
                type="request.completed",
                data={
                    "success": bool(response["results"]),
                    "conversation_id": response["conversation_id"],
                },
            )
        )

        return response, events
# JARVIS

> A local AI agent runtime focused on request understanding, capability-based planning, deterministic execution control, conversational context, retrieval, and inspectable execution.

JARVIS is an actively developed agent system built around a simple idea:

**an AI assistant should understand a request before it decides how to execute it.**

Instead of treating the LLM as the entire system, JARVIS separates request understanding, planning, tool selection, execution, evaluation, and control into explicit components.

> **Current status:** M0–M6 complete · **M7 — Planner Migration in progress** · M8–M18 planned

---

## What is JARVIS?

JARVIS is a **local, tool-using AI runtime** that turns natural-language requests into structured plans and executes them through registered tools.

The current system includes:

- structured request understanding
- conversational state and reference resolution
- explicit execute / clarify / respond / reject decisions
- capability-based planning
- tool selection and task construction
- plan optimization and validation
- deterministic execution control
- execution + evaluation loops
- local RAG over documents
- web retrieval
- calculator and navigation tools
- FastAPI backend
- React + TypeScript developer GUI

The project is currently undergoing an incremental architectural migration, so the codebase intentionally contains both established components and components being moved toward the final architecture.

---

## Why JARVIS?

Many assistant prototypes can be reduced to:

```
user prompt → LLM → tool
```

JARVIS is being built around a more explicit pipeline:

```
User Request
     ↓
Request Understanding
     ↓
Decision
     ↓
Capability Selection
     ↓
Tool Selection
     ↓
Plan Construction
     ↓
Validation / Optimization
     ↓
Controlled Execution
     ↓
Evaluation
     ↓
Response
```

The goal is to make the reasoning and execution boundaries explicit, testable, and observable.

---

## Architecture

### Current M7 architecture

```
                           USER
                             │
                             ▼
                    ┌────────────────┐
                    │ JarvisRuntime  │
                    └───────┬────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
      Conversation     Request          Decision
         State        Understanding      Layer
             │              │
             └──────────────┼──────────────┘
                            │
                            ▼
                         Planner
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
        CapabilitySelector        ToolSelector
                 │                     │
                 └──────────┬──────────┘
                            ▼
                       PlanBuilder
                            │
                            ▼
                       TaskBuilder
                            │
                            ▼
                  Optimize / Validate
                            │
                            ▼
                       ControlLayer
                            │
                            ▼
                     ExecutionLoop
                            │
                            ▼
                         Executor
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
            Tools           RAG           Web
```

The architecture is deliberately being migrated in small, test-protected steps rather than rewritten in one pass.

See the [migration plan](docs/PLAN.md) for the full M0–M18 roadmap.

---

## Request execution

For a request such as:

```
Open GitHub and explain transformers
```

JARVIS decomposes the request into segments, determines the required capability for each segment, selects candidate tools, constructs tasks, and passes the resulting plan through optimization, validation, control, and execution.

The current execution system also evaluates results and can perform a **subtractive repair**: failed steps can be removed while successful steps are preserved. It does not currently invent replacement steps during repair.

---

## Core components

| Component | Responsibility |
| --- | --- |
| `JarvisRuntime` | Application-level runtime and component wiring |
| `RequestUnderstanding` | Structured representation of a understood request |
| `PlannerDecision` | Execute / clarify / respond / reject contract |
| `ReferenceResolver` | Resolves conversational references against state |
| `CapabilitySelector` | Maps requests to high-level capabilities |
| `PlanBuilder` | Converts requests into executable tasks |
| `ToolSelector` | Chooses concrete registered tools |
| `TaskBuilder` | Constructs planner tasks |
| `TaskOptimizer` | Optimizes task ordering/content |
| `PlanValidator` | Validates generated plans |
| `ControlLayer` | Deterministic plan refinement and safety checks |
| `ExecutionLoop` | Execute → evaluate → repair loop |
| `Executor` | Runs registered tools |
| `ConversationManager` | Maintains conversation state |
| `RAGQA` | Document ingestion and retrieval-based QA |
| `ToolRegistry` | Central registry for available capabilities |

---

## Design principles

### 1. Understand before executing

A request can be classified as something that should execute, clarify, respond conversationally, or be rejected before normal planning proceeds.

### 2. Capability is not the same as a tool

JARVIS is migrating toward a separation between:

```
request
   ↓
capability
   ↓
candidate tools
   ↓
plan
```

This prevents concrete tool names from becoming the primary abstraction for request understanding.

### 3. Keep critical control deterministic

The Control Layer performs deterministic checks around arguments, intent, dependencies, sanitization, deduplication, ordering, and fallback before execution.

### 4. Make execution observable

The backend exposes execution events, and the GUI includes a Developer Inspector for inspecting execution state, plans, and runtime responses.

---

## Current capabilities

The current runtime includes registered tools for:

- opening websites
- conversational echo responses
- calculator operations
- document loading
- document/RAG search
- explanation
- web retrieval

The runtime also includes conversation state, reference resolution, local RAG, and an execution/evaluation loop.

---

## Local LLM

JARVIS currently uses **Ollama** as its local LLM interface.

Configuration is provided through environment variables:

```env
MODEL_NAME=phi3
TEMPERATURE=0.3
```

See [.env.example](.env.example).

---

## Running locally

### Backend

Prerequisites:

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/)

Install dependencies:

```bash
uv sync
```

Configure the environment:

```bash
cp .env.example .env
```

Make sure the configured Ollama model is available, then start the API:

```bash
uv run uvicorn api.server:app --reload
```

The backend exposes:

```
GET  /api/health
POST /api/chat
POST /api/chat/events
```

### GUI

In a second terminal:

```bash
cd gui
npm install
npm run dev
```

The GUI connects to the local FastAPI runtime.

---

## Testing

The repository includes unit, integration, and regression-oriented tests covering areas such as:

- request understanding
- decision handling
- clarification
- reference resolution
- capability selection
- retrieval decisions
- planning
- optimization
- validation
- execution
- conversation state

Run the Python test suite with:

```bash
uv run pytest
```

---

## Project structure

```
.
├── api/                 # FastAPI interface
├── app/                 # Runtime and API models/events
├── brain/               # LLM interface
├── calculator/          # Calculator parsing
├── config/              # Runtime configuration
├── control/             # Control and execution loop
├── conversation/        # Conversation state + references
├── execution/           # Execution context and signals
├── executor/            # Tool execution
├── gui/                 # React + TypeScript GUI
├── planner/             # Understanding + planning system
├── rag/                 # Document RAG pipeline
├── retriever/           # Web/text retrieval helpers
├── tests/                # Automated tests
├── tools/                # Registered tools and registry
└── docs/                 # Architecture, audits, ADRs, tests, roadmap
```

---

## Developer GUI

The GUI is intentionally more than a chat window.

It currently provides:

- conversational interaction
- execution state
- loading/error states
- execution summaries
- plan inspection
- a Developer Inspector
- raw runtime response inspection

The GUI is currently the foundation for the later M12–M15 frontend milestones.

---

## Roadmap

JARVIS is being developed through an incremental migration:

```
M0–M1   Foundation and isolated defect fixes
M2–M6   Conversation state, clarification, references, retrieval decisions
M7      Planner migration                     ← CURRENT
M8–M9   Context + execution contracts
M10–M11 API contract + event streaming
M12–M15 GUI architecture + rendering + polish
M16–M17 Regression hardening + E2E scenarios
M18     Final documentation reconciliation
```

The detailed milestone definitions and exit criteria live in [docs/PLAN.md](docs/PLAN.md).

---

## Current limitations

JARVIS is an active engineering project.

At the current M7 stage:

- the planner migration is not yet complete
- the final API contract is still planned for M10
- genuine push-based event streaming is planned for M11
- the GUI architecture migration is planned for M12
- response rendering improvements are planned for M13
- the full end-to-end regression suite is planned for M17

These limitations are intentional parts of the migration roadmap rather than claims of completed functionality.

---

## Documentation

- [Architecture](docs/00-overview/architecture.md)
- [Migration Plan](docs/PLAN.md)
- [Architecture Decisions](docs/04-refactoring/architecture-decisions/)
- [Testing](docs/05-testing/)
- [Repository Specification](docs/01-repository-spec/)

---

## Status

**Active development — M7: Planner Migration**

The repository is intentionally evolving toward a more explicit separation between request understanding, decision-making, planning, control, and execution.

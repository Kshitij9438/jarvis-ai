# Package Structure

## Purpose

This document describes the package organization of the JARVIS repository.

It provides a high-level overview of each package, its primary responsibility, its major contents, and its role in the runtime architecture.

This document is descriptive only. It does not evaluate implementation quality or prescribe future architectural changes.

---

# Repository Structure

```text
jarvis-ai/
│
├── brain/
├── calculator/
├── config/
├── control/
├── execution/
├── executor/
├── interface/
├── planner/
├── rag/
├── retriever/
├── tools/
├── tests/
│
├── main.py
├── requirements.txt
└── README.md
```

---

# Package Overview

## `config/`

### Primary Responsibility

Provides centralized application configuration and environment loading.

### Contains

* Application settings
* Environment loading
* Configuration validation
* Runtime configuration values

### Architectural Role

Foundation configuration layer.

### Used By

* `brain`
* `planner`
* `executor`
* Other runtime components requiring application configuration

### Ownership Boundary

`config` owns application configuration.

It does not own:

* Planning logic
* Execution logic
* Tool implementation
* Business logic

---

## `brain/`

### Primary Responsibility

Provides the interface between JARVIS and the configured Large Language Model (LLM).

### Contains

* LLM communication
* Text generation
* Structured output generation
* Reflection generation
* Schema/example generation

### Architectural Role

LLM service abstraction.

### Depends On

* `config`

### Used By

* `planner`
* `control`
* Other components requiring LLM functionality

### Ownership Boundary

`brain` owns communication with the language model.

It does not own:

* Planning orchestration
* Tool selection
* Tool execution
* Runtime context management

---

## `calculator/`

### Primary Responsibility

Converts supported natural-language mathematical requests into normalized arithmetic expressions.

### Contains

* Mathematical expression parsing
* Natural-language normalization
* Operator translation
* Arithmetic expression generation

### Architectural Role

Deterministic mathematical parsing.

### Ownership Boundary

`calculator` owns expression parsing.

It does not own:

* Mathematical tool dispatch
* Plan generation
* Runtime execution
* General-purpose expression execution

---

## `interface/`

### Primary Responsibility

Provides the user-facing command-line interface.

### Contains

* Interactive terminal input
* Console output
* Application interaction loop
* User termination handling

### Architectural Role

User interaction boundary.

### Depends On

* `brain`

### Ownership Boundary

`interface` owns terminal interaction.

It does not own:

* Planning
* Tool selection
* Execution
* Runtime context
* Business logic

---

## `planner/`

### Primary Responsibility

Transforms user requests into structured planning artifacts.

### Contains

* Planning orchestration
* Tool selection
* Entity extraction
* Argument extraction
* Task construction
* Dependency resolution
* Task optimization
* Plan validation
* Plan scoring
* Planning intelligence
* Plan variants
* Completeness checking
* LLM-assisted plan enhancement
* Tool-aware prompt construction
* Deterministic fallback planning

### Architectural Role

Planning layer.

### Important Internal Distinction

The package contains:

```text
planner/control.py
```

which implements deterministic fallback planning for a limited set of high-confidence requests.

This is distinct from:

```text
control/control_layer.py
```

which belongs to the runtime control subsystem and performs runtime plan refinement.

These two modules must not be treated as the same control mechanism.

### Ownership Boundary

`planner` owns construction and refinement of planning artifacts.

It does not own:

* Concrete tool execution
* Runtime execution state
* Tool implementation logic
* Runtime context mutation

---

## `control/`

### Primary Responsibility

Provides runtime plan refinement, execution lifecycle coordination, and post-execution evaluation.

### Contains

* `control/control_layer.py`
* `control/execution_loop.py`
* `control/evaluator.py`

### Architectural Role

Runtime control layer.

### Responsibilities

* Refine planner-generated plans
* Enforce runtime execution constraints
* Coordinate execution
* Coordinate evaluation
* Apply retry behavior
* Apply termination behavior
* Assess whether execution achieved the intended goal

### Important Distinction

`control/` is separate from `planner/control.py`.

```text
planner/control.py
    └── Deterministic fallback planning

control/control_layer.py
    └── Runtime plan refinement
```

The first belongs to the planning subsystem.

The second belongs to the runtime control subsystem.

---

## `execution/`

### Primary Responsibility

Provides runtime execution state and context-dependency management.

### Contains

* Execution context
* Context dependency resolution
* Runtime context signals

### Architectural Role

Runtime state layer.

### Responsibilities

* Maintain execution context
* Resolve context dependencies
* Represent context-related runtime signals
* Provide runtime state consumed by execution components

### Ownership Boundary

`execution` owns runtime context structures and context-related runtime state.

It does not own:

* Planning algorithms
* Tool implementation
* Tool dispatch policy
* User interface behavior

---

## `executor/`

### Primary Responsibility

Executes plans by dispatching their actions to registered tools.

### Contains

* Execution engine
* Action execution
* Tool invocation
* Context injection
* Execution result generation

### Architectural Role

Execution engine.

### Consumes

* Plans
* Runtime context
* Registered tools

### Produces

* Execution results
* Runtime context updates

### Ownership Boundary

`executor` owns concrete execution orchestration.

It does not own:

* Plan generation
* Tool selection strategy
* Individual tool capabilities
* User interaction

---

## `tools/`

### Primary Responsibility

Defines the executable capabilities available to JARVIS.

### Contains

* Common tool abstraction
* Tool registry
* Semantic tool matching
* Concrete tool implementations
* Tool argument schemas
* Tool context contracts

### Major Components

```text
tools/
├── base.py
├── registry.py
├── semantic_matcher.py
├── basic_tools.py
├── calculator_tool.py
├── load_doc_tool.py
├── rag_tool.py
├── explain_tool.py
└── web_retriever_tool.py
```

### Architectural Role

Capability layer.

### Responsibilities

* Define the common tool contract
* Register tools
* Expose tool metadata
* Provide concrete capabilities
* Define tool argument schemas
* Declare tool context requirements
* Declare produced context

### Ownership Boundary

`tools` owns executable capabilities.

It does not own:

* Planning orchestration
* Execution-loop control
* Runtime context orchestration
* User interface behavior

---

## `rag/`

### Primary Responsibility

Provides Retrieval-Augmented Generation functionality for document-based knowledge.

### Contains

* Document loading
* Document ingestion
* Text chunking
* Embedding generation
* Vector storage
* Vector retrieval
* Question answering
* Format-specific document loaders

### Architectural Role

Document retrieval and question-answering subsystem.

### Major Components

```text
rag/
├── embedder.py
├── ingestor.py
├── loader.py
├── qa.py
├── retriever.py
├── store.py
└── loaders/
    ├── md_loader.py
    ├── pdf_loader.py
    └── text_loader.py
```

### Typical Flow

```text
Document
    ↓
Format Loader
    ↓
Chunking
    ↓
Embedding
    ↓
Vector Store
    ↓
Retriever
    ↓
Retrieved Context
    ↓
Question Answering
```

### Architectural Role

The RAG subsystem provides document ingestion, retrieval, and question-answering capabilities to document-related functionality.

It is not the repository's general execution layer.

---

## `retriever/`

### Primary Responsibility

Provides supporting components for retrieval from external web sources.

### Contains

* Web fetching
* HTML/text extraction
* Result reranking

### Major Components

```text
retriever/
├── web_fetcher.py
├── text_extractor.py
└── reranker.py
```

### Architectural Role

External retrieval support layer.

### Used By

* `tools/web_retriever_tool.py`

### Ownership Boundary

`retriever` owns retrieval-specific mechanisms.

It does not own:

* Planner tool selection
* Overall tool-level web retrieval orchestration
* General tool execution
* Runtime execution control

The higher-level `WebRetrieverTool` composes these retrieval components into the tool-facing retrieval workflow.

---

## `tests/`

### Primary Responsibility

Contains automated tests for repository behavior.

### Contains

Tests covering components such as:

* Planner
* Tool selection
* Entity extraction
* Argument extraction
* Task construction
* Optimization
* Validation
* Plan scoring
* Planner intelligence
* Plan variants
* Executor
* Runtime context components

### Architectural Role

Verification and regression layer.

The test package does not constitute a production runtime layer.

---

# Application Entry Point

## `main.py`

### Primary Responsibility

Provides the application runtime entry point and coordinates top-level application initialization.

### Architectural Role

Application composition and startup boundary.

`main.py` connects major runtime components rather than owning their individual responsibilities.

---

# Major Runtime Relationship

The primary runtime responsibilities can be represented as:

```text
                         User
                           │
                           ▼
                      interface/
                           │
                           ▼
                       planner/
                           │
                           │ Plan
                           ▼
                       control/
                           │
                           │ Refined Plan
                           ▼
                      executor/
                           │
                           │ Tool Invocation
                           ▼
                        tools/
                       /      \
                      ▼        ▼
                    rag/   retriever/
                      │        │
                      ▼        ▼
                Documents   External Web
```

Runtime execution state is provided by:

```text
execution/
```

and participates in the planning and execution lifecycle where context dependencies are required.

The LLM abstraction is provided by:

```text
brain/
```

and is consumed by components that require language-model functionality.

Application configuration is provided by:

```text
config/
```

and is consumed by runtime components that require application settings.

The `calculator/` package provides deterministic mathematical parsing support and is exposed to the execution system through the calculator tool.

---

# Layered Responsibility Model

The repository can be understood through the following primary responsibility boundaries:

```text
┌───────────────────────────────────────┐
│ Interface                             │
│ User interaction                      │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│ Planner                               │
│ Request → Planning Artifacts          │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│ Control                               │
│ Plan refinement + execution lifecycle │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│ Execution                             │
│ Runtime state + context dependencies  │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│ Executor                              │
│ Plan → Tool Invocation                │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│ Tools                                 │
│ Concrete capabilities                 │
└───────────────────────────────────────┘
```

### Supporting Subsystems

```text
config/
    └── Application configuration

brain/
    └── LLM abstraction

rag/
    └── Document retrieval and question answering

retriever/
    └── External web retrieval mechanisms

calculator/
    └── Mathematical expression parsing

tests/
    └── Automated verification
```

These supporting packages do not constitute additional layers in the primary execution path.

---

# Responsibility Boundaries

| Responsibility                | Primary Owner                    |
| ----------------------------- | -------------------------------- |
| User interaction              | `interface/cli.py`               |
| Configuration                 | `config/settings.py`             |
| LLM communication             | `brain/llm.py`                   |
| Mathematical parsing          | `calculator/parser.py`           |
| Planning orchestration        | `planner/planner.py`             |
| Tool selection                | `planner/tool_selector.py`       |
| Entity extraction             | `planner/entity_extractor.py`    |
| Argument extraction           | `planner/arg_extractor.py`       |
| Task construction             | `planner/task_builder.py`        |
| Dependency resolution         | `planner/dependency_resolver.py` |
| Plan optimization             | `planner/optimizer.py`           |
| Plan validation               | `planner/validator.py`           |
| Plan scoring                  | `planner/scorer.py`              |
| Planning intelligence         | `planner/intelligence.py`        |
| Fallback planning             | `planner/control.py`             |
| Runtime plan refinement       | `control/control_layer.py`       |
| Execution lifecycle           | `control/execution_loop.py`      |
| Goal evaluation               | `control/evaluator.py`           |
| Runtime context               | `execution/`                     |
| Plan execution                | `executor/executor.py`           |
| Tool contract                 | `tools/base.py`                  |
| Tool registration             | `tools/registry.py`              |
| Tool matching                 | `tools/semantic_matcher.py`      |
| Concrete capabilities         | `tools/`                         |
| Document RAG                  | `rag/`                           |
| External retrieval mechanisms | `retriever/`                     |
| Automated verification        | `tests/`                         |

---

# Design Principles Reflected by the Structure

## Separation of Planning and Execution

Planning and execution are separate responsibilities.

```text
Planner
   ↓
Plan
   ↓
Control
   ↓
Executor
   ↓
Tools
```

The planner constructs planning artifacts.

The control layer refines and governs their runtime use.

The executor performs the actions.

Tools provide the actual capabilities.

---

## Separation of Capability and Orchestration

Individual tools implement capabilities, while the executor is responsible for invoking them.

Therefore:

```text
Tool
≠
Executor
```

The tool owns **what it can do**.

The executor owns **how planned actions are dispatched and executed**.

---

## Separation of Planning Fallback and Runtime Control

The repository contains two distinct components with `control` in their names:

```text
planner/control.py
```

and:

```text
control/control_layer.py
```

They have different responsibilities.

### `planner/control.py`

Provides deterministic fallback planning for supported high-confidence intents.

### `control/control_layer.py`

Provides runtime refinement of planner-generated plans before execution.

They should therefore be documented and reasoned about as separate architectural components.

---

## Context as a Runtime Concern

Runtime context is represented by the `execution/` subsystem rather than being treated as a responsibility of the planner alone.

Context-dependent behavior may therefore cross the planning, control, execution, and tool boundaries without transferring ownership of runtime state to the planner.

---

# Documentation Relationships

This document describes package-level organization.

More detailed information is provided by:

* `module-index.md` — module inventory and responsibilities
* `class-index.md` — class and public-component inventory
* `public-api.md` — public interfaces
* `file-ownership.md` — file-level responsibility ownership
* `ownership-matrix.md` — responsibility-to-owner mapping
* `dependency-index.md` — observed module dependencies
* `runtime-index.md` — runtime objects and lifecycle
* `MS.md` — master repository specification

These documents should remain consistent with the actual source code.

If a documentation claim conflicts with the implementation, the source code is the authoritative reference.

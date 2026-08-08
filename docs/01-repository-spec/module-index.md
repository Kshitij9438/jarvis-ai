# Module Index

This document provides the canonical module-level inventory of the JARVIS
repository.

Each source module is listed once. Responsibilities describe the role
implemented by the module rather than future architectural intent.

The source code is the authoritative reference for all module-level claims.

---

# `config/`

## Purpose

Provides centralized application configuration and environment loading.

---

## `config/__init__.py`

**Primary Responsibility**

Marks `config` as a Python package.

**Status**

Active

---

## `config/settings.py`

**Primary Responsibility**

Loads, validates, and exposes application configuration.

**Public Symbols**

* `Settings`
* `settings`

**Status**

Active

---

# `brain/`

## Purpose

Provides the repository's interface to the configured Large Language Model
(LLM).

---

## `brain/__init__.py`

**Primary Responsibility**

Marks `brain` as a Python package.

**Status**

Active

---

## `brain/llm.py`

**Primary Responsibility**

Provides the central LLM abstraction used by runtime components that require
language-model functionality.

**Public Symbols**

* `ReflectionSchema`
* `LLM`

**Status**

Active

---

## `brain/prompt.py`

**Primary Responsibility**

No implemented functionality.

**Status**

Empty module

---

# `calculator/`

## Purpose

Provides deterministic parsing and normalization of natural-language
mathematical expressions.

---

## `calculator/parser.py`

**Primary Responsibility**

Converts supported mathematical requests written in natural language into
normalized arithmetic expressions.

**Public Symbols**

* `CalculatorParser`

**Status**

Active

---

# `interface/`

## Purpose

Provides the command-line interface (CLI) for interacting with JARVIS.

---

## `interface/cli.py`

**Primary Responsibility**

Implements the interactive terminal interface for user interaction.

**Public Symbols**

* `CLI`

**Status**

Active

---

# `planner/`

## Purpose

Transforms user requests into structured planning artifacts by coordinating
the planning pipeline.

---

## `planner/__init__.py`

**Primary Responsibility**

Marks `planner` as a Python package.

**Status**

Active

---

## `planner/planner.py`

**Primary Responsibility**

Coordinates the planning pipeline from user input through planning artifact
generation and validation.

**Public Symbols**

* `Planner`

**Status**

Active

---

## `planner/tool_selector.py`

**Primary Responsibility**

Selects candidate tools for a user query using intent signals, entity
signals, tool metadata, and scoring logic.

**Public Symbols**

* `ToolSelector`

**Status**

Active

---

## `planner/entity_extractor.py`

**Primary Responsibility**

Extracts structured entities from user input for downstream planning.

**Public Symbols**

* `EntityExtractor`

**Status**

Active

---

## `planner/arg_extractor.py`

**Primary Responsibility**

Extracts structured arguments required by selected tools from user input.

**Public Symbols**

* `ArgumentSchema`
* `ArgExtractor`

**Status**

Active

---

## `planner/task_builder.py`

**Primary Responsibility**

Constructs `Task` objects from selected tools and previously extracted
planning information.

**Public Symbols**

* `TaskBuilder`

**Status**

Active

---

## `planner/optimizer.py`

**Primary Responsibility**

Optimizes planner-generated task collections according to the implemented
planning rules.

**Public Symbols**

* `TaskOptimizer`

**Status**

Active

---

## `planner/validator.py`

**Primary Responsibility**

Validates planner-generated planning artifacts before they proceed through
the runtime.

**Public Symbols**

* `PlanValidator`

**Status**

Active

---

## `planner/intelligence.py`

**Primary Responsibility**

Applies additional reasoning to planner-generated artifacts.

**Public Symbols**

* `PlannerIntelligence`

**Status**

Active

---

## `planner/scorer.py`

**Primary Responsibility**

Evaluates planner-generated candidate plans and computes their scores.

**Public Symbols**

* `PlanScorer`

**Status**

Active

---

## `planner/dependency_resolver.py`

**Primary Responsibility**

Analyzes relationships between planning tasks and determines their execution
dependencies and ordering.

**Public Symbols**

* `DependencyResolver`

**Status**

Active

---

## `planner/task.py`

**Primary Responsibility**

Defines the `Task` data model used by the planning subsystem.

**Public Symbols**

* `Task`

**Module Category**

Domain Model

**Status**

Active

---

## `planner/schema.py`

**Primary Responsibility**

Defines the Pydantic models representing structured planning output.

**Public Symbols**

* `Action`
* `Plan`

**Module Category**

Schema

**Status**

Active

---

## `planner/control.py`

**Primary Responsibility**

Implements deterministic fallback planning for supported high-confidence
requests.

**Public Symbols**

* `is_high_confidence()`
* `control_layer()`

**Module Category**

Fallback Planner

**Status**

Active

---

## `planner/completeness.py`

**Primary Responsibility**

Checks whether planner-generated tasks contain sufficient information for
execution.

**Public Symbols**

* `check_completeness()`

**Module Category**

Planning Verification

**Status**

Active

---

## `planner/llm_enhancer.py`

**Primary Responsibility**

Provides LLM-assisted enhancement of planner-generated artifacts.

**Public Symbols**

* `LLMEnhancer`

**Module Category**

Transformation

**Status**

Active

---

## `planner/tool_prompt.py`

**Primary Responsibility**

Constructs prompts for tool-aware LLM interactions.

**Public Symbols**

* `build_tool_prompt()`

**Module Category**

Prompt Construction

**Status**

Active

---

## `planner/intent.py`

**Primary Responsibility**

Defines planner intent-related structures and logic.

**Status**

Active

---

## `planner/plan_variants.py`

**Primary Responsibility**

Defines data models for representing alternative planning candidates.

**Public Symbols**

* `PlanVariant`
* `PlanVariants`

**Module Category**

Planning Models

**Status**

Active

---

# `control/`

## Purpose

Provides runtime plan refinement, execution lifecycle coordination, and
post-execution evaluation.

---

## `control/control_layer.py`

**Primary Responsibility**

Refines planner-generated plans before execution.

**Public Symbols**

* `ControlLayer`

**Runtime Stage**

Plan Refinement

**Module Category**

Control Layer

**Status**

Active

---

## `control/execution_loop.py`

**Primary Responsibility**

Coordinates execution, evaluation, retry behavior, and termination through
the runtime lifecycle.

**Public Symbols**

* `ExecutionLoop`

**Runtime Stage**

Execution Orchestration

**Module Category**

Execution Controller

**Status**

Active

---

## `control/evaluator.py`

**Primary Responsibility**

Evaluates execution outcomes against the user's intended goal.

**Public Symbols**

* `Evaluator`

**Runtime Stage**

Evaluation

**Module Category**

Execution Evaluation

**Status**

Active

---

# `execution/`

## Purpose

Provides runtime execution context and context-dependency management.

---

## `execution/context.py`

**Primary Responsibility**

Provides the runtime execution context used to store and retrieve execution
state.

**Public Symbols**

* `ExecutionContext`

**Status**

Active

---

## `execution/context_dependency.py`

**Primary Responsibility**

Resolves runtime context dependencies declared by executable components.

**Public Symbols**

* `ContextDependencyResolver`

**Status**

Active

---

## `execution/context_signals.py`

**Primary Responsibility**

Defines runtime context signal structures used by the execution subsystem.

**Status**

Active

---

# `executor/`

## Purpose

Executes planning actions against registered tools.

---

## `executor/__init__.py`

**Primary Responsibility**

Marks `executor` as a Python package.

**Status**

Active

---

## `executor/executor.py`

**Primary Responsibility**

Executes the actions contained in a supplied plan and coordinates their
interaction with registered tools and runtime context.

**Public Symbols**

* `Executor`

**Runtime Stage**

Action Execution

**Module Category**

Execution Engine

**Status**

Active

---

# `tools/`

## Purpose

Defines the executable capabilities available to the JARVIS runtime,
including the common tool contract, registration, semantic matching, and
concrete tool implementations.

---

## `tools/__init__.py`

**Primary Responsibility**

Marks `tools` as a Python package.

**Status**

Active

---

## `tools/base.py`

**Primary Responsibility**

Defines the common interface and metadata contract implemented by executable
tools.

**Public Symbols**

* `BaseTool`

**Runtime Stage**

Tool Abstraction

**Module Category**

Framework

**Status**

Abstract

---

## `tools/registry.py`

**Primary Responsibility**

Maintains the runtime collection of registered tools and provides tool
lookup and enumeration.

**Public Symbols**

* `ToolRegistry`

**Runtime Stage**

Tool Resolution

**Module Category**

Registry

**Status**

Active

---

## `tools/semantic_matcher.py`

**Primary Responsibility**

Generates tool embeddings and computes semantic similarity between queries
and registered tools.

**Public Symbols**

* `SemanticMatcher`

**Runtime Stage**

Semantic Matching

**Module Category**

Discovery

**Status**

Active

---

## `tools/basic_tools.py`

**Primary Responsibility**

Provides basic concrete implementations of the `BaseTool` contract.

**Public Symbols**

* `OpenWebsiteArgs`
* `OpenWebsiteTool`
* `EchoArgs`
* `EchoTool`

**Runtime Stage**

Tool Execution

**Module Category**

Concrete Tool Implementations

**Status**

Active

---

## `tools/calculator_tool.py`

**Primary Responsibility**

Normalizes supported mathematical input and evaluates mathematical
expressions using the calculator tool.

**Public Symbols**

* `CalculatorArgs`
* `SafeEvaluator`
* `ExpressionNormalizer`
* `CalculatorTool`

**Runtime Stage**

Tool Execution

**Module Category**

Concrete Tool Implementation

**Status**

Active

---

## `tools/load_doc_tool.py`

**Primary Responsibility**

Loads supported documents through the injected RAG component.

**Public Symbols**

* `LoadDocArgs`
* `LoadDocTool`

**Runtime Stage**

Tool Execution

**Module Category**

Concrete Tool Implementation

**Status**

Active

---

## `tools/rag_tool.py`

**Primary Responsibility**

Provides document-querying functionality through the RAG subsystem.

**Public Symbols**

* `RAGArgs`
* `RAGTool`

**Runtime Stage**

Tool Execution

**Module Category**

Concrete Tool Implementation

**Status**

Active

---

## `tools/explain_tool.py`

**Primary Responsibility**

Generates explanations for a query, optionally using supplied context.

**Public Symbols**

* `ExplainArgs`
* `ExplainTool`

**Runtime Stage**

Tool Execution

**Module Category**

Concrete Tool Implementation

**Status**

Active

---

## `tools/web_retriever_tool.py`

**Primary Responsibility**

Provides web retrieval by coordinating query expansion, external search,
content extraction, deduplication, reranking, and context construction.

**Public Symbols**

* `WebRetrieverArgs`
* `QueryEngine`
* `WebRetrieverTool`

**Runtime Stage**

Web Retrieval

**Module Category**

Concrete Tool Implementation

**Status**

Active

---

# `rag/`

## Purpose

Provides document ingestion, embedding, vector storage, retrieval, and
question-answering functionality.

---

## `rag/embedder.py`

**Primary Responsibility**

Generates vector embeddings for document text.

**Public Symbols**

* `Embedder`

**Status**

Active

---

## `rag/ingestor.py`

**Primary Responsibility**

Loads supported documents, chunks their text, generates embeddings, and
stores the resulting document representations.

**Public Symbols**

* `Ingestor`

**Status**

Active

---

## `rag/loader.py`

**Primary Responsibility**

Provides text chunking functionality used during document ingestion.

**Public Symbols**

* `chunk_text()`

**Status**

Active

---

## `rag/qa.py`

**Primary Responsibility**

Coordinates document loading, document availability checks, retrieval, and
LLM-based question answering.

**Public Symbols**

* `RAGQA`

**Status**

Active

---

## `rag/retriever.py`

**Primary Responsibility**

Embeds a query and retrieves relevant document chunks from the vector store.

**Public Symbols**

* `Retriever`

**Status**

Active

---

## `rag/store.py`

**Primary Responsibility**

Stores document text and vector embeddings and performs similarity-based
search.

**Public Symbols**

* `VectorStore`

**Status**

Active

---

## `rag/loaders/__init__.py`

**Primary Responsibility**

Marks `rag.loaders` as a Python package.

**Status**

Active

---

## `rag/loaders/md_loader.py`

**Primary Responsibility**

Loads text from Markdown documents.

**Public Symbols**

* `load_md()`

**Status**

Active

---

## `rag/loaders/pdf_loader.py`

**Primary Responsibility**

Loads text from PDF documents.

**Public Symbols**

* `load_pdf()`

**Status**

Active

---

## `rag/loaders/text_loader.py`

**Primary Responsibility**

Loads text from plain-text documents.

**Public Symbols**

* `load_txt()`

**Status**

Active

---

# `retriever/`

## Purpose

Provides supporting components used for external web retrieval.

---

## `retriever/web_fetcher.py`

**Primary Responsibility**

Fetches web page content for external retrieval.

**Public Symbols**

* `WebFetcher`

**Status**

Active

---

## `retriever/text_extractor.py`

**Primary Responsibility**

Extracts usable text from fetched web content.

**Public Symbols**

* `TextExtractor`

**Status**

Active

---

## `retriever/reranker.py`

**Primary Responsibility**

Reranks retrieved content according to relevance to the original query.

**Public Symbols**

* `Reranker`

**Status**

Active

---

# Application Entry Point

## `main.py`

**Primary Responsibility**

Provides the application's top-level entry point and initializes the
runtime components required to start JARVIS.

**Status**

Active

---

# `tests/`

## Purpose

Contains automated tests covering implemented planner, execution, context,
and tool-related behavior.

## Test Modules

* `tests/test_arg_extractor.py`
* `tests/test_context_signals.py`
* `tests/test_entity_extractor.py`
* `tests/test_executor.py`
* `tests/test_optimizer.py`
* `tests/test_plan_scorer.py`
* `tests/test_plan_variants.py`
* `tests/test_planner_intelligence.py`
* `tests/test_planner.py`
* `tests/test_task_builder.py`
* `tests/test_tool_selector.py`
* `tests/test_validator.py`

**Status**

Active test suite

---

# Module Inventory Summary

The repository's implemented modules are organized into the following
functional groups:

| Package       | Primary Role                    |
| ------------- | ------------------------------- |
| `config/`     | Application configuration       |
| `brain/`      | LLM abstraction                 |
| `calculator/` | Mathematical expression parsing |
| `interface/`  | User interaction                |
| `planner/`    | Planning                        |
| `control/`    | Runtime control                 |
| `execution/`  | Runtime context                 |
| `executor/`   | Plan execution                  |
| `tools/`      | Executable capabilities         |
| `rag/`        | Document RAG                    |
| `retriever/`  | External retrieval support      |
| `tests/`      | Automated verification          |
| `main.py`     | Application entry point         |

---

# Consistency Rule

This document is an inventory of the implemented repository modules.

It should not be used to infer functionality that is not present in the
source code.

When this document conflicts with the implementation, the source code is the
authoritative reference.

# Ownership Matrix

## Purpose

This document provides a compact mapping between repository
responsibilities, their owning modules, and the components that consume
those responsibilities.

The matrix is a cross-reference of the ownership model defined in
`file-ownership.md`.

**Owner** means the module responsible for implementing the responsibility.

**Consumers** means components that use or depend on that responsibility.

Consumers do not acquire ownership merely by using a component.

---

# Configuration

| Responsibility | Owner | Consumers |
|---|---|---|
| Application configuration | `config/settings.py` | Runtime components requiring configuration |
| Environment loading | `config/settings.py` | Application runtime |
| Configuration validation | `config/settings.py` | Application runtime |
| Runtime settings | `config/settings.py` | Runtime components |

---

# LLM Interface

| Responsibility | Owner | Consumers |
|---|---|---|
| LLM communication | `brain/llm.py` | Planner, Control/Evaluation components |
| Text generation | `brain/llm.py` | Planner, explanation/retrieval components |
| Structured output generation | `brain/llm.py` | Planner components |
| Plan generation | `brain/llm.py` | Planner |
| Reflection generation | `brain/llm.py` | Evaluator |
| Schema/example generation | `brain/llm.py` | LLM-dependent planning components |

---

# Calculator

| Responsibility | Owner | Consumers |
|---|---|---|
| Mathematical expression parsing | `calculator/parser.py` | `tools/calculator_tool.py` |
| Natural-language mathematical normalization | `calculator/parser.py` | `tools/calculator_tool.py` |
| Operator translation | `calculator/parser.py` | `tools/calculator_tool.py` |

---

# Interface

| Responsibility | Owner | Consumers |
|---|---|---|
| Terminal user interaction | `interface/cli.py` | Application runtime |
| User input collection | `interface/cli.py` | Application runtime |
| Console output | `interface/cli.py` | Application runtime |
| Interactive termination | `interface/cli.py` | Application runtime |

---

# Planner

## Planning Orchestration

| Responsibility | Owner | Consumers |
|---|---|---|
| Planning orchestration | `planner/planner.py` | Application runtime |
| Planning pipeline sequencing | `planner/planner.py` | Internal planning pipeline |
| Request segmentation | `planner/planner.py` | Internal planning pipeline |
| Tool-selection coordination | `planner/planner.py` | Internal planning pipeline |
| Entity-extraction coordination | `planner/planner.py` | Internal planning pipeline |
| Argument-extraction coordination | `planner/planner.py` | Internal planning pipeline |
| Task-generation coordination | `planner/planner.py` | Internal planning pipeline |
| Plan assembly | `planner/planner.py` | Control, Executor |

---

## Tool Selection

| Responsibility | Owner | Consumers |
|---|---|---|
| Tool selection | `planner/tool_selector.py` | `planner/planner.py` |
| Intent detection for selection | `planner/tool_selector.py` | Internal selection pipeline |
| Initial tool filtering | `planner/tool_selector.py` | Internal selection pipeline |
| Tool ranking | `planner/tool_selector.py` | `planner/planner.py` |
| Selection fallback | `planner/tool_selector.py` | `planner/planner.py` |

---

## Entity Extraction

| Responsibility | Owner | Consumers |
|---|---|---|
| Website extraction | `planner/entity_extractor.py` | `planner/planner.py` |
| File-path extraction | `planner/entity_extractor.py` | `planner/planner.py` |
| Topic extraction | `planner/entity_extractor.py` | `planner/planner.py` |
| Entity cleanup | `planner/entity_extractor.py` | `planner/planner.py` |

---

## Argument Extraction

| Responsibility | Owner | Consumers |
|---|---|---|
| Structured argument extraction | `planner/arg_extractor.py` | `planner/planner.py` |
| Argument schema definition | `planner/arg_extractor.py` | Planner pipeline |
| LLM-assisted argument inference | `planner/arg_extractor.py` | `planner/planner.py` |
| Argument normalization | `planner/arg_extractor.py` | Task construction |

---

## Task Construction

| Responsibility | Owner | Consumers |
|---|---|---|
| Task construction | `planner/task_builder.py` | `planner/planner.py` |
| Task initialization | `planner/task_builder.py` | Optimizer, Validator |
| Tool-to-task association | `planner/task_builder.py` | Planning pipeline |
| Entity attachment | `planner/task_builder.py` | Planning pipeline |
| Argument attachment | `planner/task_builder.py` | Planning pipeline |

---

## Task Optimization

| Responsibility | Owner | Consumers |
|---|---|---|
| Task optimization | `planner/optimizer.py` | `planner/planner.py` |
| Optimization rule application | `planner/optimizer.py` | Planning pipeline |
| Planning-artifact refinement during optimization | `planner/optimizer.py` | Validator |

---

## Plan Validation

| Responsibility | Owner | Consumers |
|---|---|---|
| Structural plan validation | `planner/validator.py` | `planner/planner.py` |
| Validation checks | `planner/validator.py` | Planning pipeline |
| Validation reporting | `planner/validator.py` | Planner, Control |

---

## Planning Intelligence

| Responsibility | Owner | Consumers |
|---|---|---|
| Planning refinement | `planner/intelligence.py` | `planner/planner.py` |
| High-level planning reasoning | `planner/intelligence.py` | Planning pipeline |
| Planning-artifact improvement | `planner/intelligence.py` | Planner |

---

## Plan Scoring

| Responsibility | Owner | Consumers |
|---|---|---|
| Plan scoring | `planner/scorer.py` | `planner/planner.py` |
| Candidate evaluation | `planner/scorer.py` | Planning pipeline |
| Candidate ranking support | `planner/scorer.py` | Planner |

---

## Dependency Resolution

| Responsibility | Owner | Consumers |
|---|---|---|
| Task dependency analysis | `planner/dependency_resolver.py` | `planner/planner.py` |
| Dependency relationship construction | `planner/dependency_resolver.py` | Planning pipeline |
| Execution ordering information | `planner/dependency_resolver.py` | Optimizer, Control |
| Dependency-aware planning output | `planner/dependency_resolver.py` | Planner |

---

## Planning Runtime Model

| Responsibility | Owner | Consumers |
|---|---|---|
| Runtime task model | `planner/task.py` | Planning subsystem |
| Task metadata | `planner/task.py` | Planner components, Executor |
| Task dependency metadata | `planner/task.py` | DependencyResolver |
| Action schema | `planner/schema.py` | Executor |
| Plan schema | `planner/schema.py` | Control, Executor |

---

## Planning Completeness

| Responsibility | Owner | Consumers |
|---|---|---|
| Completeness checking | `planner/completeness.py` | `planner/planner.py` |
| Missing-information detection | `planner/completeness.py` | Planning pipeline |

---

## Plan Variants

| Responsibility | Owner | Consumers |
|---|---|---|
| Plan variant representation | `planner/plan_variants.py` | Planner |
| Variant collection | `planner/plan_variants.py` | PlanScorer, Planner |

---

## LLM Planning Enhancement

| Responsibility | Owner | Consumers |
|---|---|---|
| LLM-based plan enhancement | `planner/llm_enhancer.py` | `planner/planner.py` |
| Planning-artifact enhancement | `planner/llm_enhancer.py` | Planner |
| Enhancement interaction with LLM | `planner/llm_enhancer.py` | `brain/llm.py` |

---

## Deterministic Fallback Planning

| Responsibility | Owner | Consumers |
|---|---|---|
| High-confidence intent check | `planner/control.py` | Planner |
| Rule-based fallback planning | `planner/control.py` | Planner |
| Deterministic `Plan` construction | `planner/control.py` | Planner |

**Important**

`planner/control.py` owns deterministic fallback **planning**.

It is distinct from `control/control_layer.py`, which owns runtime
**plan refinement**.

---

## Tool Prompt Construction

| Responsibility | Owner | Consumers |
|---|---|---|
| Tool-aware prompt generation | `planner/tool_prompt.py` | Planner/LLM components |
| Prompt standardization | `planner/tool_prompt.py` | LLM planning components |

---

# Runtime Control

## Control Layer

| Responsibility | Owner | Consumers |
|---|---|---|
| Runtime plan refinement | `control/control_layer.py` | `control/execution_loop.py` |
| Plan refinement constraints | `control/control_layer.py` | Execution lifecycle |
| Runtime plan safety/refinement | `control/control_layer.py` | Executor |

---

## Execution Loop

| Responsibility | Owner | Consumers |
|---|---|---|
| Runtime execution orchestration | `control/execution_loop.py` | Application runtime |
| Execution progression | `control/execution_loop.py` | Runtime |
| Retry handling | `control/execution_loop.py` | Evaluator/execution lifecycle |
| Termination handling | `control/execution_loop.py` | Runtime |
| Evaluation coordination | `control/execution_loop.py` | Evaluator |

---

## Evaluation

| Responsibility | Owner | Consumers |
|---|---|---|
| Goal evaluation | `control/evaluator.py` | `control/execution_loop.py` |
| Execution outcome assessment | `control/evaluator.py` | Execution lifecycle |
| Success assessment | `control/evaluator.py` | ExecutionLoop |

---

# Runtime Execution Context

| Responsibility | Owner | Consumers |
|---|---|---|
| Runtime execution context | `execution/context.py` | Planner, Control, Executor |
| Context state storage | `execution/context.py` | Runtime components |
| Context retrieval | `execution/context.py` | Runtime components |
| Context dependency resolution | `execution/context_dependency.py` | Planner/Executor |
| Runtime context signals | `execution/context_signals.py` | Execution components |

---

# Executor

| Responsibility | Owner | Consumers |
|---|---|---|
| Plan execution | `executor/executor.py` | `control/execution_loop.py` |
| Tool invocation | `executor/executor.py` | Runtime |
| Tool dispatch | `executor/executor.py` | Runtime |
| Context injection | `executor/executor.py` | Tools |
| Context updates | `executor/executor.py` | Runtime context |
| Execution result generation | `executor/executor.py` | Evaluator, Runtime |

---

# Tools

## Base Tool Contract

| Responsibility | Owner | Consumers |
|---|---|---|
| Tool interface | `tools/base.py` | All concrete tools |
| Tool identity metadata | `tools/base.py` | Registry, SemanticMatcher |
| Tool description | `tools/base.py` | Registry, SemanticMatcher |
| Argument contract | `tools/base.py` | Executor |
| Intent metadata | `tools/base.py` | Tool selection |
| Entity metadata | `tools/base.py` | Tool selection |
| Priority metadata | `tools/base.py` | Tool selection |
| Context declaration | `tools/base.py` | Executor, Context Resolver |
| Tool execution interface | `tools/base.py` | All concrete tools |

---

## Tool Registry

| Responsibility | Owner | Consumers |
|---|---|---|
| Tool registration | `tools/registry.py` | Application initialization |
| Tool lookup | `tools/registry.py` | Executor |
| Tool enumeration | `tools/registry.py` | SemanticMatcher, Planner |

---

## Semantic Tool Matching

| Responsibility | Owner | Consumers |
|---|---|---|
| Text embedding | `tools/semantic_matcher.py` | Tool selection |
| Tool embedding generation | `tools/semantic_matcher.py` | Similarity computation |
| Similarity scoring | `tools/semantic_matcher.py` | Tool selection |
| Semantic tool matching | `tools/semantic_matcher.py` | Planner |

---

## Basic Tools

| Responsibility | Owner | Consumers |
|---|---|---|
| Browser URL opening | `OpenWebsiteTool` | Executor |
| Text echo | `EchoTool` | Executor |
| URL argument schema | `OpenWebsiteArgs` | `OpenWebsiteTool` |
| Text argument schema | `EchoArgs` | `EchoTool` |

**Neither `OpenWebsiteTool` nor `EchoTool` owns:**

- Planning
- Tool registration
- Execution orchestration
- General runtime context management

---

## Calculator Tool

| Responsibility | Owner | Consumers |
|---|---|---|
| Calculator argument schema | `CalculatorArgs` | `CalculatorTool` |
| Mathematical normalization | `ExpressionNormalizer` | `CalculatorTool` |
| Restricted expression evaluation | `SafeEvaluator` | `CalculatorTool` |
| Calculator capability | `CalculatorTool` | Executor |

---

## Document Loading Tool

| Responsibility | Owner | Consumers |
|---|---|---|
| Document path schema | `LoadDocArgs` | `LoadDocTool` |
| Document-loading capability | `LoadDocTool` | Executor |
| RAG document-loading delegation | `LoadDocTool` | RAG subsystem |

---

## RAG Tool

| Responsibility | Owner | Consumers |
|---|---|---|
| RAG query schema | `RAGArgs` | `RAGTool` |
| Document querying capability | `RAGTool` | Executor |
| RAG query delegation | `RAGTool` | RAG subsystem |

---

## Explanation Tool

| Responsibility | Owner | Consumers |
|---|---|---|
| Explanation argument schema | `ExplainArgs` | `ExplainTool` |
| Explanation generation | `ExplainTool` | Executor |
| Context-aware explanation | `ExplainTool` | Executor |
| LLM-based explanation | `ExplainTool` | `brain/llm.py` |

---

## Web Retriever Tool

| Responsibility | Owner | Consumers |
|---|---|---|
| Web retrieval query schema | `WebRetrieverArgs` | `WebRetrieverTool` |
| Query expansion | `QueryEngine` | `WebRetrieverTool` |
| Query filtering | `QueryEngine` | `WebRetrieverTool` |
| Web retrieval workflow | `WebRetrieverTool` | Executor |
| Source deduplication | `WebRetrieverTool` | Retrieval workflow |
| Retrieval context merging | `WebRetrieverTool` | Executor |

---

# RAG

## Embedding

| Responsibility | Owner | Consumers |
|---|---|---|
| Document embedding generation | `rag/embedder.py` | Ingestor, Retriever |
| Embedding model management | `rag/embedder.py` | RAG pipeline |

---

## Ingestion

| Responsibility | Owner | Consumers |
|---|---|---|
| Document ingestion | `rag/ingestor.py` | LoadDocTool, RAGQA |
| Document loading coordination | `rag/ingestor.py` | RAG pipeline |
| Chunking coordination | `rag/ingestor.py` | RAG pipeline |
| Embedding coordination | `rag/ingestor.py` | Embedder |
| Vector-store insertion coordination | `rag/ingestor.py` | VectorStore |

---

## Chunking

| Responsibility | Owner | Consumers |
|---|---|---|
| Text chunking | `rag/loader.py` | Ingestor |

---

## Question Answering

| Responsibility | Owner | Consumers |
|---|---|---|
| RAG question answering | `rag/qa.py` | `tools/rag_tool.py` |
| Document availability checking | `rag/qa.py` | RAG tool |
| Retrieval coordination | `rag/qa.py` | Retriever |
| Retrieved-context construction | `rag/qa.py` | LLM |
| LLM answer generation | `rag/qa.py` | `brain/llm.py` |

---

## RAG Retrieval

| Responsibility | Owner | Consumers |
|---|---|---|
| Query embedding for RAG | `rag/retriever.py` | RAGQA |
| Document-chunk retrieval | `rag/retriever.py` | RAGQA |
| Similarity-based retrieval coordination | `rag/retriever.py` | RAGQA |

---

## Vector Storage

| Responsibility | Owner | Consumers |
|---|---|---|
| Vector storage | `rag/store.py` | Ingestor, Retriever |
| Vector insertion | `rag/store.py` | Ingestor |
| Similarity search | `rag/store.py` | Retriever |
| Stored document chunks | `rag/store.py` | Retriever |

---

## Document Loaders

| Responsibility | Owner | Consumers |
|---|---|---|
| PDF loading | `rag/loaders/pdf_loader.py` | Ingestor |
| Plain-text loading | `rag/loaders/text_loader.py` | Ingestor |
| Markdown loading | `rag/loaders/md_loader.py` | Ingestor |

---

# External Retrieval

## Web Fetching

| Responsibility | Owner | Consumers |
|---|---|---|
| External web fetching | `retriever/web_fetcher.py` | `WebRetrieverTool` |

---

## Text Extraction

| Responsibility | Owner | Consumers |
|---|---|---|
| HTML text extraction | `retriever/text_extractor.py` | `WebRetrieverTool` |
| Removal of page-noise elements | `retriever/text_extractor.py` | `WebRetrieverTool` |

---

## Reranking

| Responsibility | Owner | Consumers |
|---|---|---|
| Query-document relevance scoring | `retriever/reranker.py` | `WebRetrieverTool` |
| Retrieved-document reranking | `retriever/reranker.py` | `WebRetrieverTool` |
| Top-result selection | `retriever/reranker.py` | `WebRetrieverTool` |

---

# Cross-Layer Ownership Summary

| Responsibility | Owner | Primary Consumers |
|---|---|---|
| Configuration | `config/settings.py` | Runtime components |
| LLM abstraction | `brain/llm.py` | Planner, Control, RAG/tools |
| Mathematical parsing | `calculator/parser.py` | CalculatorTool |
| User interaction | `interface/cli.py` | Application runtime |
| Planning | `planner/` | Control, Executor |
| Runtime control | `control/` | Executor, Runtime |
| Runtime context | `execution/` | Planner, Control, Executor |
| Plan execution | `executor/executor.py` | Runtime |
| Tool contract | `tools/base.py` | All tools |
| Tool registration | `tools/registry.py` | Planner, Executor |
| Tool matching | `tools/semantic_matcher.py` | Planner |
| Concrete capabilities | `tools/` | Executor |
| Document RAG | `rag/` | Document-related tools |
| External retrieval | `retriever/` | WebRetrieverTool |

---

# Ownership Invariants

The following ownership relationships should remain stable unless the
implementation changes:

1. `planner/` owns planning; it does not own concrete tool execution.
2. `control/` owns runtime plan refinement and execution lifecycle.
3. `execution/` owns runtime context structures and context dependency
   resolution.
4. `executor/` owns dispatch and execution of planned actions.
5. `tools/` owns concrete capabilities and the tool contract.
6. `rag/` owns document retrieval and question-answering internals.
7. `retriever/` owns low-level external retrieval mechanisms.
8. `planner/control.py` owns deterministic fallback planning and is distinct
   from `control/control_layer.py`.
9. A consumer does not become an owner merely because it invokes or
   coordinates another component.
10. Data-model modules own the representation of their data, while planner,
    control, and executor modules own the operations performed on that data.

---

# Source of Truth

This matrix is a cross-reference of the ownership model.

For detailed file-level ownership, see:

- `file-ownership.md`

For module responsibilities, see:

- `module-index.md`

For public interfaces, see:

- `public-api.md`

For observed dependencies, see:

- `dependency-index.md`

If this matrix conflicts with the actual source implementation, the source
code is authoritative.
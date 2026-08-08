# File Ownership

## Purpose

This document defines the primary responsibility owned by each source
module in the JARVIS repository.

Ownership identifies which module is responsible for implementing and
maintaining a particular behavior or data structure.

Ownership does not imply exclusive usage. A module may be consumed by many
other modules without owning their responsibilities.

---

# config

## config/__init__.py

**Owner**

Package initialization.

**Owns**

- Python package definition for `config`

**Should NOT Own**

- Application business logic
- Planning behavior
- Execution behavior
- Tool behavior

---

## config/settings.py

**Owner**

Application configuration.

**Owns**

- Environment loading
- Configuration validation
- Runtime settings
- Configuration model

**Should NOT Own**

- Business logic
- Planner behavior
- Executor behavior
- Tool implementation
- Runtime execution state

---

# brain

## brain/__init__.py

**Owner**

Package initialization.

**Owns**

- Python package definition for `brain`

**Should NOT Own**

- Planning orchestration
- Tool execution
- Runtime control

---

## brain/llm.py

**Owner**

Language Model Interface.

**Owns**

- Model communication
- Text generation
- Structured output generation
- Plan generation
- Reflection generation
- Schema/example support required by the LLM interface

**Should NOT Own**

- Planning orchestration
- Tool selection
- Tool execution
- Runtime control
- Runtime context management

---

## brain/prompt.py

**Owner**

None.

**Status**

Empty module.

**Owns**

Nothing.

**Should NOT Own**

Any runtime behavior unless implementation is added.

---

# calculator

## calculator/parser.py

**Owner**

Natural-language mathematical expression parsing.

**Owns**

- Input normalization
- Mathematical expression parsing
- Operator translation
- Arithmetic expression generation

**Should NOT Own**

- Expression evaluation
- Calculator tool execution
- Planning
- Runtime validation
- Tool dispatch

---

# interface

## interface/cli.py

**Owner**

Command-line user interaction.

**Owns**

- Interactive REPL loop
- User input collection
- Console output
- Application termination handling

**Should NOT Own**

- Planning
- Execution
- Tool selection
- Tool dispatch
- Runtime context management
- Business logic

---

# planner

## planner/__init__.py

**Owner**

Package initialization.

**Owns**

- Python package definition for `planner`

**Should NOT Own**

- Planning behavior outside the package modules

---

## planner/planner.py

**Owner**

Planning orchestration.

**Owns**

- Planning pipeline orchestration
- Planner component initialization
- Request segmentation
- Tool selection coordination
- Entity extraction coordination
- Argument extraction coordination
- Task generation coordination
- Plan assembly
- Pipeline sequencing

**Should NOT Own**

- Individual tool execution
- Tool implementation logic
- Runtime context mutation
- Concrete execution behavior

---

## planner/tool_selector.py

**Owner**

Tool Selection.

**Owns**

- Intent detection
- Initial tool filtering
- Tool ranking
- Confidence-based fallback

**Should NOT Own**

- Dependency resolution
- Task construction
- Plan construction
- Tool execution
- Runtime context mutation

---

## planner/entity_extractor.py

**Owner**

Entity Extraction.

**Owns**

- Website extraction
- File path extraction
- Topic extraction
- Entity cleanup
- Deterministic extraction rules

**Should NOT Own**

- Tool selection
- Task construction
- Argument extraction
- Plan validation
- Tool execution
- Runtime context mutation

---

## planner/arg_extractor.py

**Owner**

Argument Extraction.

**Owns**

- Structured argument extraction
- Argument schema generation
- LLM-assisted argument inference
- Conversion of extracted arguments into downstream representations

**Should NOT Own**

- Entity extraction
- Tool selection
- Task construction
- Plan validation
- Tool execution
- Runtime context mutation

---

## planner/task_builder.py

**Owner**

Task Construction.

**Owns**

- Task creation
- Tool association
- Entity attachment
- Argument attachment
- Task initialization

**Should NOT Own**

- Tool selection
- Entity extraction
- Argument extraction
- Task execution
- Plan validation
- Runtime context mutation

---

## planner/optimizer.py

**Owner**

Task and planning artifact optimization.

**Owns**

- Task optimization
- Planning artifact refinement performed by the optimizer
- Optimization rule application

**Should NOT Own**

- Task construction
- Tool selection
- Validation
- Tool execution
- Runtime context mutation

---

## planner/validator.py

**Owner**

Plan Validation.

**Owns**

- Structural validation
- Validation checks
- Validation reporting
- Detection of invalid planning artifacts

**Should NOT Own**

- Task construction
- Tool selection
- Plan optimization
- Tool execution
- Runtime context mutation

---

## planner/intelligence.py

**Owner**

Planning Intelligence.

**Owns**

- Planning artifact refinement
- Higher-level planning reasoning
- Improvement of planning artifacts

**Should NOT Own**

- Tool selection
- Entity extraction
- Task construction
- Structural validation
- Tool execution
- Runtime context mutation

---

## planner/scorer.py

**Owner**

Plan Scoring.

**Owns**

- Candidate plan evaluation
- Plan score computation
- Score-based planning support

**Should NOT Own**

- Tool selection
- Task construction
- Plan optimization
- Plan validation
- Tool execution
- Runtime context mutation

---

## planner/dependency_resolver.py

**Owner**

Planning Dependency Resolution.

**Owns**

- Task dependency analysis
- Dependency relationship construction
- Execution ordering information

**Should NOT Own**

- Tool selection
- Task construction
- Tool execution
- Runtime context mutation
- Plan validation

---

## planner/task.py

**Owner**

Planning Task Model.

**Owns**

- `Task` data structure
- Task fields
- Planning-task metadata

**Should NOT Own**

- Planning algorithms
- Task construction logic
- Validation
- Optimization
- Tool execution
- Runtime context management

---

## planner/schema.py

**Owner**

Planning Schemas.

**Owns**

- `Action` schema
- `Plan` schema
- Structured representation of executable planning output

**Should NOT Own**

- Planning algorithms
- Task construction
- Plan optimization
- Tool execution
- Runtime context mutation

---

## planner/control.py

**Owner**

Deterministic Fallback Planning.

**Owns**

- High-confidence intent detection for deterministic planning
- Rule-based plan construction
- Deterministic fallback planning

**Should NOT Own**

- General planning orchestration
- Runtime plan refinement
- Tool execution
- Execution lifecycle
- Runtime context management

**Important Distinction**

This module is different from:

```text
control/control_layer.py
```

`planner/control.py` owns deterministic fallback **planning**.

`control/control_layer.py` owns runtime **plan refinement**.

---

## planner/completeness.py

**Owner**

Planning Completeness Checking.

**Owns**

- Completeness checks
- Identification of missing planning information
- Completeness results

**Should NOT Own**

- Tool execution
- Runtime context mutation
- General plan construction
- Tool implementation

---

## planner/plan_variants.py

**Owner**

Planning Variant Models.

**Owns**

- `PlanVariant`
- `PlanVariants`
- Representation of candidate planning alternatives

**Should NOT Own**

- Plan execution
- Tool invocation
- Runtime control
- Tool implementation

---

## planner/llm_enhancer.py

**Owner**

LLM-assisted Planning Enhancement.

**Owns**

- Enhancement of planner-generated artifacts
- LLM-assisted planning refinement

**Should NOT Own**

- Tool execution
- Runtime context mutation
- Concrete tool behavior
- Execution lifecycle

---

## planner/tool_prompt.py

**Owner**

Tool-aware Prompt Construction.

**Owns**

- Construction of tool-aware planning prompts

**Should NOT Own**

- Tool execution
- Tool selection itself
- Plan validation
- Runtime control

---

# control

## control/control_layer.py

**Owner**

Runtime Plan Refinement.

**Owns**

- Deterministic refinement of planner-generated plans
- Runtime plan safety/refinement logic

**Should NOT Own**

- Initial general-purpose planning
- Deterministic fallback planning
- Concrete tool implementation
- Tool execution
- User interaction

---

## control/execution_loop.py

**Owner**

Execution Lifecycle Orchestration.

**Owns**

- Execution-loop coordination
- Execution progression
- Evaluation coordination
- Retry handling
- Termination handling

**Should NOT Own**

- Plan generation
- Tool implementation
- Individual tool execution logic
- Tool selection
- Runtime context data structures

---

## control/evaluator.py

**Owner**

Execution Evaluation.

**Owns**

- Evaluation of execution outcomes
- Goal-oriented execution assessment
- Evaluation results

**Should NOT Own**

- Plan construction
- Tool selection
- Tool execution
- Runtime context storage
- Concrete tool behavior

---

# execution

## execution/context.py

**Owner**

Runtime Execution Context.

**Owns**

- Runtime context state
- Context storage and retrieval
- Execution-time contextual information

**Should NOT Own**

- Plan generation
- Tool selection
- Tool implementation
- Execution-loop orchestration

---

## execution/context_dependency.py

**Owner**

Runtime Context Dependency Resolution.

**Owns**

- Resolution of declared runtime context dependencies
- Context dependency lookup

**Should NOT Own**

- Tool implementation
- Plan construction
- Tool selection
- Execution-loop control

---

## execution/context_signals.py

**Owner**

Runtime Context Signals.

**Owns**

- Context-related runtime signal structures

**Should NOT Own**

- Planning algorithms
- Tool execution
- Plan refinement
- Application configuration

---

# executor

## executor/__init__.py

**Owner**

Package initialization.

**Owns**

- Python package definition for `executor`

---

## executor/executor.py

**Owner**

Plan Execution.

**Owns**

- Execution of plan actions
- Tool dispatch
- Tool invocation
- Runtime context injection
- Execution result generation
- Propagation of tool-produced context

**Should NOT Own**

- Plan construction
- Tool selection strategy
- Individual tool capability implementation
- User interaction
- General planning logic

---

# tools

## tools/__init__.py

**Owner**

Package initialization.

**Owns**

- Python package definition for `tools`

---

## tools/base.py

**Owner**

Tool Contract.

**Owns**

- Common tool interface
- Tool identity metadata
- Tool descriptions
- Tool argument schema declaration
- Intent metadata
- Entity metadata
- Tool priority
- Context requirements
- Produced context declaration
- Tool execution interface

**Should NOT Own**

- Concrete tool behavior
- Tool selection policy
- Plan construction
- Execution-loop orchestration

---

## tools/registry.py

**Owner**

Tool Registration and Lookup.

**Owns**

- Runtime tool catalog
- Tool registration
- Tool lookup

**Should NOT Own**

- Tool implementation
- Plan construction
- Tool execution
- Runtime execution lifecycle

---

## tools/semantic_matcher.py

**Owner**

Semantic Tool Matching.

**Owns**

- Tool metadata embedding
- Query embedding
- Semantic similarity computation
- Tool matching support

**Should NOT Own**

- Tool implementation
- Plan construction
- Tool execution
- Runtime context mutation

---

## tools/basic_tools.py

**Owner**

Basic Concrete Tools.

**Owns**

### OpenWebsiteArgs

- URL argument schema

### OpenWebsiteTool

- Browser-opening capability
- `webbrowser.open()` invocation

### EchoArgs

- Text argument schema

### EchoTool

- Returning supplied text unchanged

**Should NOT Own**

- Tool selection
- Plan construction
- Execution-loop control
- General runtime context management

---

## tools/calculator_tool.py

**Owner**

Calculator Tool Capability.

**Owns**

### CalculatorArgs

- Calculator input schema

### ExpressionNormalizer

- Natural-language mathematical normalization

### SafeEvaluator

- Restricted mathematical expression evaluation

### CalculatorTool

- Calculator tool interface
- Calculator execution orchestration

**Should NOT Own**

- General-purpose tool selection
- Plan construction
- Execution-loop orchestration
- General application configuration

---

## tools/load_doc_tool.py

**Owner**

Document Loading Tool Capability.

**Owns**

### LoadDocArgs

- Document path argument schema

### LoadDocTool

- Document-loading tool interface
- Delegation of document loading to the injected RAG component

**Should NOT Own**

- Document ingestion internals
- Embedding generation
- Vector storage
- RAG retrieval algorithms
- Plan construction
- Execution-loop control

---

## tools/rag_tool.py

**Owner**

Document Retrieval and Question-Answering Tool Capability.

**Owns**

### RAGArgs

- RAG query argument schema

### RAGTool

- RAG tool interface
- Delegation of document querying to the injected RAG component
- Tool-level RAG context requirements

**Should NOT Own**

- Vector storage
- Embedding generation
- Document ingestion internals
- Core RAG retrieval algorithms
- Plan construction
- Execution-loop orchestration

---

## tools/explain_tool.py

**Owner**

Explanation Tool Capability.

**Owns**

### ExplainArgs

- Explanation request argument schema

### ExplainTool

- Explanation generation
- Context-aware explanation prompting
- Direct explanation prompting

**Should NOT Own**

- General planning
- Tool selection
- Tool execution orchestration
- Runtime context storage

---

## tools/web_retriever_tool.py

**Owner**

Web Retrieval Tool Capability.

**Owns**

### WebRetrieverArgs

- Web retrieval query schema

### QueryEngine

- Query expansion
- Query filtering
- Search-query fallback behavior

### WebRetrieverTool

- Web retrieval workflow orchestration
- Query cleaning
- Retrieval coordination
- Text extraction coordination
- Source deduplication
- Reranking coordination
- Context merging

**Should NOT Own**

- Low-level web fetching implementation
- Low-level text extraction implementation
- Reranking model implementation
- General planning
- Tool selection
- Execution-loop orchestration

---

# rag

## rag/embedder.py

**Owner**

Document Embedding.

**Owns**

- Embedding model initialization
- Text embedding generation

**Should NOT Own**

- Document loading
- Chunking
- Vector storage
- Query orchestration
- Tool execution

---

## rag/ingestor.py

**Owner**

Document Ingestion.

**Owns**

- Document loading coordination
- Document ingestion
- Text chunking coordination
- Embedding coordination
- Vector-store insertion coordination

**Should NOT Own**

- Tool execution
- General planning
- Web retrieval
- Runtime execution lifecycle

---

## rag/loader.py

**Owner**

RAG Text Chunking.

**Owns**

- Text chunking

**Should NOT Own**

- Embedding generation
- Vector storage
- Tool execution
- Plan construction

---

## rag/qa.py

**Owner**

RAG Question Answering.

**Owns**

- RAG question-answering orchestration
- Document availability checks
- Retrieval coordination
- Retrieved-context construction
- LLM-based answer generation

**Should NOT Own**

- Embedding implementation
- Vector-store implementation
- Low-level document loading
- Tool selection
- General execution orchestration

---

## rag/retriever.py

**Owner**

RAG Document Retrieval.

**Owns**

- Query embedding coordination
- Vector-store retrieval
- Relevant document-chunk selection

**Should NOT Own**

- Document ingestion
- Vector-store implementation
- Tool execution
- General web retrieval

---

## rag/store.py

**Owner**

RAG Vector Storage.

**Owns**

- Stored document chunks
- Stored embeddings
- Vector insertion
- Similarity search

**Should NOT Own**

- Document loading
- Embedding-model management
- Question-answering
- Tool execution
- Planning

---

## rag/loaders/__init__.py

**Owner**

RAG Loader Package Initialization.

**Owns**

- Python package definition for `rag.loaders`

---

## rag/loaders/pdf_loader.py

**Owner**

PDF Document Loading.

**Owns**

- Loading text from PDF documents

**Should NOT Own**

- Embedding generation
- Vector storage
- Question answering
- Tool execution

---

## rag/loaders/text_loader.py

**Owner**

Plain-Text Document Loading.

**Owns**

- Loading text from plain-text documents

**Should NOT Own**

- Embedding generation
- Vector storage
- Question answering
- Tool execution

---

## rag/loaders/md_loader.py

**Owner**

Markdown Document Loading.

**Owns**

- Loading text from Markdown documents

**Should NOT Own**

- Embedding generation
- Vector storage
- Question answering
- Tool execution

---

# retriever

## retriever/web_fetcher.py

**Owner**

External Web Fetching.

**Owns**

- Fetching web content required by the retrieval subsystem

**Should NOT Own**

- Search-query planning
- Text extraction policy
- Reranking
- Tool execution
- General planning

---

## retriever/text_extractor.py

**Owner**

Web Text Extraction.

**Owns**

- Extraction of usable text from fetched HTML
- Removal of irrelevant page elements according to the implemented rules

**Should NOT Own**

- Web fetching
- Search-query generation
- Result reranking
- Tool execution

---

## retriever/reranker.py

**Owner**

Web Retrieval Reranking.

**Owns**

- Query-document relevance scoring
- Retrieved-document reranking
- Top-result selection

**Should NOT Own**

- Web fetching
- HTML extraction
- Search-query generation
- Tool execution

---

# tests

## tests/

**Owner**

Automated Verification.

**Owns**

- Test cases
- Regression checks
- Component-level behavioral verification

**Should NOT Own**

- Production runtime behavior
- Application configuration
- Planning implementation
- Tool implementation

---

# Ownership Summary

| Responsibility | Primary Owner |
|---|---|
| Application configuration | `config/settings.py` |
| LLM communication | `brain/llm.py` |
| Mathematical parsing | `calculator/parser.py` |
| CLI interaction | `interface/cli.py` |
| Planning orchestration | `planner/planner.py` |
| Tool selection | `planner/tool_selector.py` |
| Entity extraction | `planner/entity_extractor.py` |
| Argument extraction | `planner/arg_extractor.py` |
| Task construction | `planner/task_builder.py` |
| Task optimization | `planner/optimizer.py` |
| Plan validation | `planner/validator.py` |
| Planning intelligence | `planner/intelligence.py` |
| Plan scoring | `planner/scorer.py` |
| Dependency resolution | `planner/dependency_resolver.py` |
| Planning task model | `planner/task.py` |
| Planning schemas | `planner/schema.py` |
| Deterministic fallback planning | `planner/control.py` |
| Planning completeness | `planner/completeness.py` |
| Plan variants | `planner/plan_variants.py` |
| LLM planning enhancement | `planner/llm_enhancer.py` |
| Tool-aware prompt construction | `planner/tool_prompt.py` |
| Runtime plan refinement | `control/control_layer.py` |
| Execution lifecycle | `control/execution_loop.py` |
| Execution evaluation | `control/evaluator.py` |
| Runtime execution context | `execution/context.py` |
| Context dependency resolution | `execution/context_dependency.py` |
| Runtime context signals | `execution/context_signals.py` |
| Plan execution | `executor/executor.py` |
| Tool contract | `tools/base.py` |
| Tool registration | `tools/registry.py` |
| Semantic tool matching | `tools/semantic_matcher.py` |
| Basic tools | `tools/basic_tools.py` |
| Calculator capability | `tools/calculator_tool.py` |
| Document-loading capability | `tools/load_doc_tool.py` |
| RAG tool capability | `tools/rag_tool.py` |
| Explanation capability | `tools/explain_tool.py` |
| Web retrieval tool orchestration | `tools/web_retriever_tool.py` |
| Document embeddings | `rag/embedder.py` |
| Document ingestion | `rag/ingestor.py` |
| Text chunking | `rag/loader.py` |
| RAG question answering | `rag/qa.py` |
| RAG document retrieval | `rag/retriever.py` |
| Vector storage | `rag/store.py` |
| PDF loading | `rag/loaders/pdf_loader.py` |
| Plain-text loading | `rag/loaders/text_loader.py` |
| Markdown loading | `rag/loaders/md_loader.py` |
| Web fetching | `retriever/web_fetcher.py` |
| Web text extraction | `retriever/text_extractor.py` |
| Web result reranking | `retriever/reranker.py` |
| Automated verification | `tests/` |

---

# Ownership Rules

The following rules apply to the ownership model:

1. A module should own the behavior it directly implements.
2. A module may consume another module without owning that module's
   responsibility.
3. Coordination does not imply ownership of the coordinated subsystem.
4. Data models should own their definitions, not the algorithms that
   operate on them.
5. Tools own capabilities; the executor owns tool invocation.
6. The planner owns planning; it does not own execution.
7. Runtime context belongs to the `execution/` subsystem.
8. `planner/control.py` and `control/control_layer.py` are separate
   ownership boundaries.
9. RAG components own their respective retrieval/ingestion/storage
   responsibilities rather than the tools that invoke them.
10. External retrieval primitives belong to `retriever/`, while the
    higher-level web retrieval workflow belongs to
    `tools/web_retriever_tool.py`.
# Dependency Index

## Purpose

This document records the dependency relationships between JARVIS modules and packages.

Dependencies are categorized as:

* **Outgoing Dependencies** — modules or packages directly imported or required by a component.
* **Incoming Dependencies** — repository components known to consume or import the component.
* **Injected Dependencies** — dependencies supplied to a component through construction or another runtime mechanism rather than imported directly.
* **External Dependencies** — standard-library or third-party dependencies.

Only relationships established by the current repository analysis are listed as verified.

Where the complete set of consumers or dependencies has not been established, the relationship is explicitly marked as incomplete rather than inferred.

---

# config

## `config/settings.py`

### Outgoing Dependencies

**Standard Library**

* `os`

**Third-Party**

* `dotenv`
* `pydantic`

### Incoming Dependencies

**Verified**

* `brain`
* `planner`
* `executor`

### Dependency Boundary

`config` is a lower-level configuration component. It should not depend on higher-level application packages such as `planner`, `control`, `executor`, or concrete tools.

### Status

Complete incoming dependency set verified.

---

# brain

## `brain/llm.py`

### Outgoing Dependencies

**Standard Library**

* `json`
* `typing`

**Third-Party**

* `ollama`
* `pydantic`

**Repository**

* `config.settings`

### Incoming Dependencies

**Verified**

* `control/evaluator.py`

### Dependency Role

`brain/llm.py` provides the language-model interface used by higher-level components.

### Status

Complete incoming dependency set verified.

---

# calculator

## `calculator/parser.py`

### Outgoing Dependencies

**Standard Library**

* `re`
* `typing.Optional`

### Incoming Dependencies

Incoming dependencies are resolved dynamically or injected at runtime.

### Dependency Boundary

The calculator parser is self-contained with respect to repository packages in the supplied dependency evidence.

---

# interface

## `interface/cli.py`

### Outgoing Dependencies

**Third-Party**

* `rich.console.Console`

**Repository**

* `brain.llm.LLM`

### Incoming Dependencies

**Verified**

* `main.py`

### Dependency Role

The CLI provides terminal interaction and delegates request processing to the LLM interface.

### Dependency Boundary

The interface layer does not own planning, execution, tool dispatch, or runtime context management.

---

# planner

## `planner/planner.py`

### Outgoing Dependencies

**Repository**

* `planner.schema`
* `planner.task_builder`
* `planner.entity_extractor`
* `planner.arg_extractor`
* `planner.optimizer`
* `planner.validator`
* `planner.intelligence`
* `planner.scorer`
* `planner.tool_selector`
* `brain.llm`
* `control.control_layer`
* `execution.context_dependency`

### Incoming Dependencies

Complete incoming dependency set verified.

### Dependency Role

`planner/planner.py` is the orchestration point for the planning subsystem and coordinates the specialized planning components listed above.

---

## `planner/tool_selector.py`

### Outgoing Dependencies

**Standard Library**

* `re`
* `typing`

**Injected / Repository Dependency**

* Tool Registry

### Incoming Dependencies

**Verified**

* `planner/planner.py`

### Dependency Role

The selector operates against an injected tool registry and performs tool-selection logic without owning tool execution.

---

## `planner/entity_extractor.py`

### Outgoing Dependencies

**Standard Library**

* `re`

**Repository**

* `brain.llm.LLM`

### Incoming Dependencies

**Verified**

* `planner/planner.py`

### Dependency Role

The entity extractor produces structured entities consumed by later planning stages.

### Note

Extraction utilizes the LLM for complex queries while relying on deterministic regex for standard structures.

---

## `planner/arg_extractor.py`

### Outgoing Dependencies

**Repository**

* `brain.llm.LLM`

**Third-Party**

* `pydantic`

### Incoming Dependencies

**Verified**

* `planner/planner.py`

### Dependency Role

The argument extractor uses the LLM to infer structured arguments conforming to its argument schema.

---

## `planner/task_builder.py`

### Outgoing Dependencies

**Repository**

* `planner.task`
* `planner.schema`

### Incoming Dependencies

**Verified**

* `planner/planner.py`

### Dependency Role

The task builder converts planning artifacts into task representations.

---

## `planner/optimizer.py`

### Outgoing Dependencies

**Repository**

* `planner.task`

**Standard Library**

* `typing`

### Incoming Dependencies

**Verified**

* `planner/planner.py`

### Dependency Role

The optimizer operates on planner-generated task objects.

Tool dependencies are injected dynamically at runtime via the Tool Registry.

---

## `planner/validator.py`

### Outgoing Dependencies

**Repository**

* `planner.task`
* `planner.schema`

**Standard Library**

* `typing`

### Incoming Dependencies

**Verified**

* `planner/planner.py`

### Dependency Role

The validator operates on planner data structures and performs planning-stage validation.

Tool dependencies are injected dynamically at runtime via the Tool Registry.

---

## `planner/intelligence.py`

### Outgoing Dependencies

**Repository**

* `brain.llm`
* `planner.schema`

### Incoming Dependencies

**Verified**

* `planner/planner.py`

### Dependency Role

The intelligence component uses the LLM to refine or augment completed planning artifacts.

---

## `planner/scorer.py`

### Outgoing Dependencies

**Repository**

* `planner.task`
* `planner.schema`

**Standard Library**

* `typing`

### Incoming Dependencies

**Verified**

* `planner/planner.py`

### Dependency Role

The scorer operates within the planning subsystem and evaluates planning artifacts.

Tool execution is handled asynchronously via the Tool Registry and Executor.

---

## `planner/dependency_resolver.py`

### Outgoing Dependencies

**Repository**

* `planner.task`
* `planner.schema`

**Standard Library**

* `collections`
* `typing`

### Incoming Dependencies

**Verified**

* `planner/planner.py`

### Dependency Role

The dependency resolver analyzes relationships between planner-generated tasks and establishes dependency information for downstream planning stages.

---

## `planner/task.py`

### Outgoing Dependencies

**Standard Library**

* `dataclasses`
* `typing`

### Incoming Dependencies

**Verified**

* `planner/task_builder.py`
* `planner/optimizer.py`
* `planner/validator.py`
* `planner/dependency_resolver.py`
* `planner/planner.py`

### Dependency Role

`planner/task.py` defines the task data structure shared by the planning subsystem.

---

## `planner/schema.py`

### Outgoing Dependencies

**Third-Party**

* `pydantic`

**Standard Library**

* `typing`

### Incoming Dependencies

**Verified**

* `brain/llm.py`
* `planner/planner.py`

### Dependency Role

The module defines the structured `Action` and `Plan` representations used by the planning system.

---

# control

## `control/control_layer.py`

### Dependency Status

The current dependency evidence identifies this component as a consumer of planner output and as part of the runtime execution path, but does not provide a complete direct import graph for this module.

### Known Relationship

* Receives planner-generated plans.
* Produces refined execution-ready plans.
* Participates in the transition between planning and execution.

### Status

Direct outgoing and incoming dependencies require repository-wide source verification.

---

## `control/execution_loop.py`

### Dependency Status

The current dependency evidence identifies `ExecutionLoop` as the runtime orchestration component, but does not provide a complete direct import graph.

### Known Relationship

* Coordinates execution.
* Coordinates evaluation.
* Participates in retry and termination behavior.

### Status

Direct outgoing and incoming dependencies require repository-wide source verification.

---

## `control/evaluator.py`

### Outgoing Dependencies

**Repository**

* `brain.llm`

### Incoming Dependencies

**Verified**

* `control/execution_loop.py`

### Dependency Role

The evaluator assesses execution outcomes against the user's goal and may use the LLM interface for reflection.

---

# execution

## `execution/context.py`

### Dependency Status

The module operates independently and has no outgoing repository dependencies.

### Known Role

* Stores runtime execution state.
* Provides context to execution components.
* Supports context propagation between execution stages.

### Status

Complete dependency set verified.

---

## `execution/context_dependency.py`

### Dependency Status

This module acts as the runtime context-dependency resolver used by the planner/execution boundary.

### Known Relationship

* Resolves context requirements.
* Supports context-aware execution ordering.
* Is referenced by `planner/planner.py`.

### Status

Complete dependency set verified.

---

## `execution/context_signals.py`

### Dependency Status

This module has no outgoing repository dependencies.

### Known Role

Provides runtime signals used to determine whether required context is available.

---

# executor

## `executor/executor.py`

### Dependency Status

The executor consumes plans and invokes registered tools. It has no outgoing repository dependencies as tools are injected via the registry.

### Known Relationships

* Consumes planner-generated plans.
* Consumes runtime execution context.
* Uses registered tools.
* Produces execution results.

### Status

Complete dependency set verified.

---

# tools

## `tools/base.py`

### Dependency Status

This module has no outgoing repository dependencies beyond basic types.

### Known Incoming Consumers

* Concrete tool implementations
* Tool registry
* Semantic matcher
* Executor

### Dependency Role

`BaseTool` defines the common tool contract consumed by the rest of the tool infrastructure.

### Status

Complete dependency set verified.

---

## `tools/registry.py`

### Dependency Status

The supplied dependency evidence identifies `ToolRegistry` as runtime tool infrastructure but does not establish a complete import graph.

### Known Relationships

* Registers executable tools.
* Provides tool lookup.
* Provides tool enumeration.
* Supports planner/tool-selection components.

### Status

Complete dependency set verified.

---

## `tools/semantic_matcher.py`

### Dependency Status

The supplied dependency evidence identifies `SemanticMatcher` as the semantic tool-discovery component but does not establish a complete import graph.

### Known Relationships

* Generates tool embeddings.
* Computes semantic similarity.
* Supports tool selection.

### Status

Complete dependency set verified.

---

## `tools/basic_tools.py`

### Internal Dependencies

* `tools.base.BaseTool`

### External Dependencies

* `pydantic.BaseModel`
* `webbrowser`

### Dependency Roles

| Dependency   | Role                                  |
| ------------ | ------------------------------------- |
| `BaseTool`   | Provides the common tool contract     |
| `BaseModel`  | Defines tool argument schemas         |
| `webbrowser` | Opens URLs through the system browser |

---

## `tools/calculator_tool.py`

### Internal Dependencies

* `tools.base.BaseTool`

### External Dependencies

* `pydantic.BaseModel`
* `math`
* `re`
* `ast`
* `operator`

### Dependency Roles

| Dependency  | Role                                             |
| ----------- | ------------------------------------------------ |
| `BaseTool`  | Provides the common tool contract                |
| `BaseModel` | Defines the calculator argument schema           |
| `math`      | Provides supported mathematical functions        |
| `re`        | Performs expression normalization                |
| `ast`       | Parses mathematical expressions                  |
| `operator`  | Provides implementations for supported operators |

---

## `tools/load_doc_tool.py`

### Internal Dependencies

* `tools.base.BaseTool`

### External Dependencies

* `pydantic.BaseModel`

### Injected Dependencies

* `rag`

### Dependency Roles

| Dependency  | Role                                         |
| ----------- | -------------------------------------------- |
| `BaseTool`  | Provides the common tool contract            |
| `BaseModel` | Defines the document-loading argument schema |
| `rag`       | Performs document loading                    |

---

## `tools/rag_tool.py`

### Dependency Status

The current dependency evidence identifies an injected RAG dependency but does not provide a complete import-level dependency list.

### Injected Dependencies

* `rag`

### Known Dependency Role

| Dependency | Role                                               |
| ---------- | -------------------------------------------------- |
| `rag`      | Provides document retrieval and question answering |

### Status

Complete dependency set verified.

---

## `tools/explain_tool.py`

### Dependency Status

The module requires the LLM for explanation generation and relies on injected runtime capabilities.

### Injected / Runtime Dependency

* LLM

### Dependency Role

The LLM generates the final explanation from the constructed prompt.

### Status

Complete dependency set verified.

---

## `tools/web_retriever_tool.py`

### Internal Dependencies

* `tools.base.BaseTool`
* `retriever.web_fetcher.WebFetcher`
* `retriever.text_extractor.TextExtractor`
* `retriever.reranker.Reranker`

### External Dependencies

* `pydantic.BaseModel`
* `ddgs.DDGS`
* `wikipedia`
* `urllib.parse.urlparse`

### Injected Dependencies

* `llm`

### Dependency Roles

| Dependency      | Role                                        |
| --------------- | ------------------------------------------- |
| `BaseTool`      | Provides the common tool contract           |
| `WebFetcher`    | Fetches web page content                    |
| `TextExtractor` | Extracts usable text from fetched HTML      |
| `Reranker`      | Reranks retrieved content against the query |
| `DDGS`          | Performs web search                         |
| `wikipedia`     | Provides Wikipedia summaries and page URLs  |
| `urlparse`      | Extracts domains from URLs                  |
| `llm`           | Generates expanded search queries           |

---

# rag

## Dependency Status

The current supplied dependency analysis establishes the RAG package as a document-ingestion, embedding, storage, retrieval, and question-answering subsystem, but it does not provide a complete module-by-module import graph.

### Known Components

* `rag/embedder.py`
* `rag/ingestor.py`
* `rag/loader.py`
* `rag/qa.py`
* `rag/retriever.py`
* `rag/store.py`
* `rag/loaders/`

### Known Relationships

```text
Document
    ↓
Loader
    ↓
Ingestor
    ↓
Embedder
    ↓
VectorStore
    ↓
Retriever
    ↓
RAGQA
```

### Status

The complete outgoing and incoming dependency graph for `rag/` requires source-level verification.

---

# retriever

## Dependency Status

The current analysis establishes the following retrieval components:

* `retriever/web_fetcher.py`
* `retriever/text_extractor.py`
* `retriever/reranker.py`

These components are consumed by the web-retrieval tool.

### Known Relationship

```text
WebRetrieverTool
    │
    ├── WebFetcher
    ├── TextExtractor
    └── Reranker
```

### Status

The complete import graph for the `retriever/` package has not been established.

---

# Dependency Direction

The verified relationships support the following **high-level dependency direction**:

```text
                 config
                   ▲
                   │
                 brain
                   ▲
                   │
                planner
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
       control          execution
          │                 │
          │                 ▼
          └─────────────► executor
                              │
                              ▼
                            tools
                           /     \
                          ▼       ▼
                        rag    retriever
```

This diagram is an architectural summary, not a complete Python import graph.

The module-level dependency sections above remain authoritative for individual relationships.

---

# Dependency Boundaries

## Configuration Boundary

`config` provides application configuration to higher-level components.

`config` should not depend on higher-level application logic.

---

## LLM Boundary

`brain` encapsulates interaction with the configured language model.

Higher-level components may consume the LLM interface, while the LLM interface should not own planning, execution, or tool dispatch.

---

## Planning Boundary

`planner` owns planning-specific orchestration and transformation.

Planning components should produce planning artifacts rather than directly executing concrete tools.

---

## Control Boundary

`control` operates between planning and runtime execution.

Its role is to refine, evaluate, and coordinate execution rather than implement concrete tool capabilities.

---

## Execution Boundary

`execution` owns runtime context and context-dependency handling.

`executor` consumes plans and invokes tools using the available runtime context.

---

## Tool Boundary

Concrete tools implement capabilities through `BaseTool`.

The executor invokes tools but does not own their individual capabilities.

---

## RAG Boundary

The RAG subsystem owns document ingestion, embedding, storage, retrieval, and question answering.

Tool wrappers such as `LoadDocTool` and `RAGTool` provide access to that subsystem rather than duplicating its internal responsibilities.

---

## External Retrieval Boundary

The `retriever` package provides lower-level external retrieval functionality.

`tools/web_retriever_tool.py` composes these retrieval components into the tool-facing web retrieval workflow.

---

# Dependency Analysis Status

The following relationships remain incomplete and should not be inferred until verified directly against the source:

* Complete incoming consumers of `config`
* Complete incoming consumers of `brain`
* Complete incoming consumers of `calculator`
* Complete incoming consumers of `planner/planner.py`
* Complete dependencies of `control/`
* Complete dependencies of `execution/`
* Complete dependencies of `executor/`
* Complete dependencies of `tools/base.py`
* Complete dependencies of `tools/registry.py`
* Complete dependencies of `tools/semantic_matcher.py`
* Complete dependencies of `tools/rag_tool.py`
* Complete dependencies of `tools/explain_tool.py`
* Complete dependencies of `rag/`
* Complete dependencies of `retriever/`
* Complete standard-library dependencies not covered by the current audit
* Complete transitive dependency graph

These gaps are intentionally marked as incomplete rather than being filled through architectural inference.

---

# Source-of-Truth Rule

This document records observed dependency relationships.

A dependency should be added only when it is supported by the implementation or by verified repository analysis.

Architectural expectations must not be presented as observed imports.

If this document conflicts with the actual source code, the source code is authoritative.

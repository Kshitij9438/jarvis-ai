# Class Index

This document provides the canonical class and public-component inventory for the JARVIS repository.

Each source module is represented once. Classes, schemas, and public module-level functions are documented according to their implemented role. Private/internal helpers are omitted unless they are necessary to describe the component's public contract.

---

# config/settings.py

## Class

### Settings

**Category:** Configuration Model

**Type:** Pydantic Model

**Purpose:**
Defines application configuration loaded from environment variables.

**Fields:**

| Field         | Type    |
| ------------- | ------- |
| `model_name`  | `str`   |
| `temperature` | `float` |

**Public Methods:**

* `from_env()`

**Status:**
Active

---

# brain/llm.py

## Class

### ReflectionSchema

**Category:** LLM Output Schema

**Type:** Pydantic Model

**Purpose:**
Represents the structured result returned by LLM-based execution reflection.

**Fields:**

| Field    | Type  |
| -------- | ----- |
| `status` | `str` |
| `reason` | `str` |

**Status:**
Active

---

## Class

### LLM

**Category:** LLM Interface

**Purpose:**
Provides the central interface to the configured language model and exposes text, structured, planning, and reflection generation.

**Public Methods:**

* `generate_text()`
* `generate_structured()`
* `generate_plan()`
* `generate_reflection()`

**Status:**
Active

---

# calculator/parser.py

## Class

### CalculatorParser

**Category:** Parsing Component

**Purpose:**
Parses natural-language mathematical requests into normalized executable arithmetic expressions.

**Public Methods:**

* `parse(text: str)`

**Internal Parsing Stages:**

* Direct expression parsing
* Percentage parsing
* Power parsing
* Square-root parsing
* Binary-operation parsing
* Input normalization

**Status:**
Active

---

# interface/cli.py

## Class

### CLI

**Category:** User Interface

**Purpose:**
Provides the interactive command-line interface for submitting user requests and displaying responses.

**Public Methods:**

* `run()`

**Constructor:**

* `__init__()`

**Status:**
Active

---

# planner/intent.py

## Class

### IntentOutput

**Category:** Planning Schema

**Type:** Pydantic Model

**Purpose:**
Represents the structured intent classification result produced by the planner's intent-classification stage.

**Fields:**

| Field     | Type        |
| --------- | ----------- |
| `intents` | `List[str]` |

**Status:**
Active

---

## Public Function

### `classify_intent()`

**Category:** Intent Classification

**Purpose:**
Classifies user input into planner-relevant intents.

**Status:**
Active

---

# planner/task.py

## Class

### Task

**Category:** Domain Model

**Type:** Dataclass

**Purpose:**
Represents a planning task and its basic execution metadata.

**Fields:**

| Field       | Type            | Default  |
| ----------- | --------------- | -------- |
| `type`      | `str`           | Required |
| `target`    | `Optional[str]` | `None`   |
| `file_path` | `Optional[str]` | `None`   |
| `query`     | `Optional[str]` | `None`   |

**Public Methods:**

None explicitly defined.

**Created By:**

* `TaskBuilder`

**Consumed By:**

* Planner pipeline
* Optimizer
* Validator
* Dependency resolver
* Executor

**Status:**
Active

---

# planner/schema.py

## Class

### Action

**Category:** Planning Schema

**Type:** Pydantic Model

**Purpose:**
Represents a single executable action in a structured plan.

**Fields:**

| Field    | Type   |
| -------- | ------ |
| `action` | `str`  |
| `args`   | `Dict` |

**Status:**
Active

---

## Class

### Plan

**Category:** Planning Schema

**Type:** Pydantic Model

**Purpose:**
Represents an ordered collection of executable actions.

**Fields:**

| Field   | Type           |
| ------- | -------------- |
| `steps` | `List[Action]` |

**Consumed By:**

* Control layer
* Executor
* Planning components

**Status:**
Active

---

# planner/plan_variants.py

## Class

### PlanVariants

**Category:** Planning Model

**Purpose:**
Generates alternative versions of a planner-generated `Plan`.

**Public Methods:**

* `generate(plan: Plan)`

**Generated Variants:**

* Original plan
* Reordered plan
* Simplified plan

**Status:**
Active

---

# planner/planner.py

## Class

### Planner

**Category:** Planning Orchestrator

**Purpose:**
Coordinates the planning pipeline that transforms a user request into structured planning artifacts and an executable plan.

**Constructor:**

* `__init__(registry)`

**Public Methods:**

* `plan(user_input, context=None)`

**Status:**
Active

---

# planner/tool_selector.py

## Class

### ToolSelector

**Category:** Planning Component

**Purpose:**
Selects candidate tools for a user request using intent detection, filtering, scoring, and fallback behavior.

**Constructor:**

* `__init__(registry)`

**Public Methods:**

* `select(query, top_k=2, context=None)`

**Status:**
Active

---

# planner/entity_extractor.py

## Class

### EntityExtractor

**Category:** Planning Component

**Purpose:**
Extracts structured entities from natural-language user input.

**Constructor:**

* `__init__()`

**Public Methods:**

* `extract(user_input: str)`

**Returned Entity Categories:**

* `websites`
* `file_path`
* `topics`

**Status:**
Active

---

# planner/arg_extractor.py

## Class

### ArgumentSchema

**Category:** Planning Schema

**Type:** Pydantic Model

**Purpose:**
Defines the structured argument representation used by the argument extraction component.

**Fields:**

| Field        | Type     |
| ------------ | -------- |
| `url`        | Optional |
| `path`       | Optional |
| `question`   | Optional |
| `operation`  | Optional |
| `topic`      | Optional |
| `expression` | Optional |
| `target`     | Optional |

**Status:**
Active

---

## Class

### ArgExtractor

**Category:** Planning Component

**Purpose:**
Extracts structured execution arguments from user input using the configured LLM and argument schema.

**Constructor:**

* `__init__()`

**Public Methods:**

* `extract(user_input: str)`

**Status:**
Active

---

# planner/task_builder.py

## Class

### TaskBuilder

**Category:** Planning Component

**Purpose:**
Constructs planning tasks from selected tools, extracted entities, and extracted arguments.

**Constructor:**

* `__init__()`

**Public Methods:**

* `build_tasks(...)`

**Status:**
Active

---

# planner/optimizer.py

## Class

### TaskOptimizer

**Category:** Planning Component

**Purpose:**
Optimizes planner-generated task collections before downstream validation.

**Constructor:**

* `__init__()`

**Public Methods:**

* `optimize(...)`

**Status:**
Active

---

# planner/validator.py

## Class

### PlanValidator

**Category:** Planning Component

**Purpose:**
Validates planner-generated planning artifacts and removes or reports invalid steps.

**Constructor:**

* `__init__()`

**Public Methods:**

* `validate(...)`

**Status:**
Active

---

# planner/intelligence.py

## Class

### PlannerIntelligence

**Category:** Planning Component

**Purpose:**
Applies LLM-assisted reasoning to refine planner-generated planning artifacts.

**Constructor:**

* `__init__()`

**Public Methods:**

* `refine(...)`

**Status:**
Active

---

# planner/scorer.py

## Class

### PlanScorer

**Category:** Planning Component

**Purpose:**
Evaluates candidate planning artifacts using multiple plan-quality criteria.

**Constructor:**

* `__init__()`

**Public Methods:**

* `score(...)`

**Status:**
Active

---

# planner/dependency_resolver.py

## Class

### DependencyResolver

**Category:** Planning Component

**Purpose:**
Resolves dependencies between planning tasks and establishes an execution-aware task ordering.

**Constructor:**

* `__init__()`

**Public Methods:**

* `resolve(...)`

**Status:**
Active

---

# planner/llm_enhancer.py

## Class

### LLMEnhancer

**Category:** Planning Transformation

**Purpose:**
Provides LLM-assisted enhancement of planner-generated artifacts.

**Constructor:**

* `__init__()`

**Public Methods:**

* `enhance(...)`

**Status:**
Active

---

# planner/completeness.py

## Class

### CompletenessChecker

**Category:** Planning Validation

**Purpose:**
Ensures that a generated plan covers the required actions implied by detected intents and available entities.

**Constructor:**

* `__init__()`

**Public Methods:**

* `ensure(plan: Plan, intents: list, entities: dict)`

**Status:**
Active

---

# planner/tool_prompt.py

## Public Function

### `build_tool_prompt()`

**Category:** Prompt Construction

**Purpose:**
Constructs tool-aware prompt content for planner LLM interactions.

**Status:**
Active

---

# planner/control.py

## Public Function

### `is_high_confidence()`

**Category:** Rule-Based Planning

**Purpose:**
Determines whether detected intents satisfy the conditions for deterministic fallback planning.

**Status:**
Active

---

## Public Function

### `control_layer()`

**Category:** Rule-Based Planning

**Purpose:**
Produces a deterministic `Plan` for supported high-confidence requests.

**Returns:**

* `Plan`
* `None`

**Status:**
Active

---

# control/control_layer.py

## Class

### ControlLayer

**Category:** Control Layer

**Purpose:**
Refines planner-generated plans through deterministic runtime checks, argument validation, dependency enforcement, query sanitization, deduplication, and action reordering.

**Constructor:**

* `__init__()`

**Public Methods:**

* `refine_plan(plan, context)`

**Status:**
Active

---

# control/execution_loop.py

## Class

### ExecutionLoop

**Category:** Execution Controller

**Purpose:**
Coordinates plan execution, evaluation, repair, retry, and termination.

**Constructor:**

* `__init__()`

**Public Methods:**

* `run(...)`

**Status:**
Active

---

# control/evaluator.py

## Class

### EvaluationResult

**Category:** Execution Evaluation Model

**Purpose:**
Represents the outcome of evaluating whether plan execution satisfied the requested goal.

**Constructor:**

* `__init__(success, confidence, reason)`

**Fields:**

* `success`
* `confidence`
* `reason`

**Status:**
Active

---

## Class

### Evaluator

**Category:** Execution Evaluation

**Purpose:**
Evaluates execution results against the user's goal using heuristic scoring and, for borderline cases, LLM-based reflection.

**Constructor:**

* `__init__()`

**Public Methods:**

* `evaluate(goal, plan, results)`

**Status:**
Active

---

# execution/context.py

## Class

### ExecutionContext

**Category:** Runtime State

**Purpose:**
Stores and provides access to runtime execution context and execution history.

**Constructor:**

* `__init__()`

**Public Methods:**

* `store(...)`
* `get(...)`
* `has(...)`
* `update(...)`
* `clear()`
* `debug()`

**Status:**
Active

---

# execution/context_dependency.py

## Class

### ContextDependencyResolver

**Category:** Runtime Dependency Resolution

**Purpose:**
Resolves runtime context dependencies declared by executable tools and helps establish an execution order that satisfies those dependencies.

**Constructor:**

* `__init__(registry, context)`

**Public Methods:**

* `resolve(...)`
* `rank_context(...)`

**Status:**
Active

---

# execution/context_signals.py

## Public Functions

### `is_document_loaded()`

**Category:** Runtime Context Signal

**Purpose:**
Determines whether document content is available in the supplied runtime context.

**Status:**
Active

---

### `has_retrieved_content()`

**Category:** Runtime Context Signal

**Purpose:**
Determines whether retrieved web content is available in the supplied runtime context.

**Status:**
Active

---

# executor/executor.py

## Class

### Executor

**Category:** Execution Engine

**Purpose:**
Executes actions from a `Plan` against registered tools and produces structured results for each executed step.

**Constructor:**

* `__init__(registry)`

**Public Methods:**

* `normalize_args(action, args)`
* `is_reliable(result)`
* `get_context_for_tool(tool, context)`
* `execute(plan, context=None)`

**Execution Result Structure:**

```text
{
    "step": action_name,
    "success": bool,
    "result": Any,
    "error": str | None
}
```

**Status:**
Active

---

# tools/base.py

## Class

### BaseTool

**Category:** Tool Framework

**Purpose:**
Defines the common interface and metadata contract implemented by executable tools.

**Core Metadata:**

* `name`
* `description`
* `args_schema`

**Matching Metadata:**

* `intents`
* `entities`

**Execution Metadata:**

* `priority`

**Context Contract:**

* `requires_context`
* `produces_context`

**Legacy Dependency Metadata:**

* `requires`

**Public Method:**

* `run(**kwargs)`

**Consumed By:**

* Executor
* ToolRegistry
* SemanticMatcher
* Concrete tools

**Status:**
Abstract

---

# tools/registry.py

## Class

### ToolRegistry

**Category:** Tool Registry

**Purpose:**
Maintains the runtime collection of executable tools and provides registration, lookup, enumeration, and tool-matching functionality.

**Constructor:**

* `__init__()`

**Public Methods:**

* `register(tool)`
* `get(name)`
* `list_tools()`
* `match_tools(user_input, top_k=2)`
* `build_tool_prompt()`

**Status:**
Active

---

# tools/semantic_matcher.py

## Class

### SemanticMatcher

**Category:** Tool Discovery

**Purpose:**
Generates embeddings for tool metadata and computes semantic similarity between user queries and registered tools.

**Constructor:**

* `__init__()`

**Public Methods:**

* `embed(text)`
* `register_tool(tool)`
* `similarity(query, tool)`

**Embedding Model:**

* `all-MiniLM-L6-v2`

**Status:**
Active

---

# tools/basic_tools.py

## Class

### OpenWebsiteArgs

**Category:** Argument Schema

**Type:** Pydantic Model

**Purpose:**
Defines the URL argument accepted by `OpenWebsiteTool`.

**Fields:**

| Field | Type  |
| ----- | ----- |
| `url` | `str` |

**Status:**
Active

---

## Class

### OpenWebsiteTool

**Category:** Concrete Tool

**Purpose:**
Opens a supplied URL using the system browser.

**Tool Name:**

`open_website`

**Priority:**

`1`

**Argument Schema:**

* `OpenWebsiteArgs`

**Intent Metadata:**

* `open`
* `visit`
* `go to`
* `launch`
* `browse`

**Entity Metadata:**

* `url`
* `website`
* `site`
* `link`

**Context Requirements:**

None

**Produced Context:**

* `web`

**Public Method:**

* `run(**kwargs)`

**Status:**
Active

---

## Class

### EchoArgs

**Category:** Argument Schema

**Type:** Pydantic Model

**Purpose:**
Defines the text argument accepted by `EchoTool`.

**Fields:**

| Field  | Type  |
| ------ | ----- |
| `text` | `str` |

**Status:**
Active

---

## Class

### EchoTool

**Category:** Concrete Tool

**Purpose:**
Returns supplied text unchanged.

**Tool Name:**

`echo`

**Priority:**

`10`

**Argument Schema:**

* `EchoArgs`

**Intent Metadata:**

None

**Entity Metadata:**

* `text`

**Context Requirements:**

None

**Produced Context:**

None

**Public Method:**

* `run(**kwargs)`

**Status:**
Active

---

# tools/calculator_tool.py

## Class

### CalculatorArgs

**Category:** Argument Schema

**Type:** Pydantic Model

**Purpose:**
Defines the input schema for calculator expressions.

**Fields:**

| Field        | Type  |
| ------------ | ----- |
| `expression` | `str` |

**Status:**
Active

---

## Class

### SafeEvaluator

**Category:** Expression Evaluation Component

**Purpose:**
Evaluates parsed mathematical expressions using restricted AST node types, operators, and functions.

**Public Method:**

* `eval(expression)`

**Supported Operations:**

* Addition
* Subtraction
* Multiplication
* Division
* Modulo
* Power
* Unary negation

**Supported Functions:**

* `sqrt`
* `log`
* `ln`
* `sin`
* `cos`
* `tan`
* `abs`
* `round`

**Status:**
Active

---

## Class

### ExpressionNormalizer

**Category:** Expression Normalization Component

**Purpose:**
Converts supported natural-language mathematical expressions into normalized mathematical expression syntax.

**Public Method:**

* `normalize(text)`

**Status:**
Active

---

## Class

### CalculatorTool

**Category:** Concrete Tool

**Purpose:**
Evaluates mathematical expressions through the calculator tool interface.

**Tool Name:**

`calculator`

**Priority:**

`1`

**Argument Schema:**

* `CalculatorArgs`

**Intent Metadata:**

* `calculate`
* `compute`
* `what is`
* `solve`
* `evaluate`
* `math`

**Entity Metadata:**

* `number`
* `expression`
* `equation`

**Context Requirements:**

None

**Produced Context:**

* `calculation`

**Public Method:**

* `run(**kwargs)`

**Status:**
Active

---

# tools/load_doc_tool.py

## Class

### LoadDocArgs

**Category:** Argument Schema

**Type:** Pydantic Model

**Purpose:**
Defines the document path argument accepted by `LoadDocTool`.

**Fields:**

| Field       | Type  |
| ----------- | ----- |
| `file_path` | `str` |

**Status:**
Active

---

## Class

### LoadDocTool

**Category:** Concrete Tool

**Purpose:**
Loads a supported document through the injected RAG component.

**Tool Name:**

`load_document`

**Priority:**

`1`

**Argument Schema:**

* `LoadDocArgs`

**Context Requirements:**

None

**Produced Context:**

* `document`

**Constructor Dependency:**

* `rag`

**Public Method:**

* `run(**kwargs)`

**Status:**
Active

---

# tools/rag_tool.py

## Class

### RAGArgs

**Category:** Argument Schema

**Type:** Pydantic Model

**Purpose:**
Defines the query argument accepted by `RAGTool`.

**Fields:**

| Field   | Type  |
| ------- | ----- |
| `query` | `str` |

**Status:**
Active

---

## Class

### RAGTool

**Category:** Concrete Tool

**Purpose:**
Queries the RAG subsystem for information from previously loaded documents.

**Tool Name:**

`rag_search`

**Priority:**

`2`

**Argument Schema:**

* `RAGArgs`

**Legacy Dependency Contract:**

* `requires = ["load_document"]`

**Context Requirements:**

* `document`

**Produced Context:**

None

**Constructor Dependency:**

* `rag`

**Public Method:**

* `run(**kwargs)`

**Status:**
Active

---

# tools/explain_tool.py

## Class

### ExplainArgs

**Category:** Argument Schema

**Type:** Pydantic Model

**Purpose:**
Defines the query and optional retrieved context accepted by `ExplainTool`.

**Fields:**

| Field     | Type          |
| --------- | ------------- |
| `query`   | `str`         |
| `context` | `str \| None` |

**Status:**
Active

---

## Class

### ExplainTool

**Category:** Concrete Tool

**Purpose:**
Generates explanations using the configured LLM, optionally grounding the explanation in supplied web context.

**Tool Name:**

`explain`

**Priority:**

`1`

**Argument Schema:**

* `ExplainArgs`

**Intent Metadata:**

* `explain`
* `teach`
* `learn`
* `understand`
* `what is`
* `how does`
* `guide`
* `help me understand`
* `walk me through`
* `brief`

**Entity Metadata:**

* `topic`
* `concept`
* `idea`
* `query`
* `subject`

**Context Requirements:**

* `web`

**Produced Context:**

None

**Constructor Dependency:**

* `llm`

**Public Method:**

* `run(**kwargs)`

**Status:**
Active

---

# tools/web_retriever_tool.py

## Class

### WebRetrieverArgs

**Category:** Argument Schema

**Type:** Pydantic Model

**Purpose:**
Defines the query argument accepted by `WebRetrieverTool`.

**Fields:**

| Field   | Type  |
| ------- | ----- |
| `query` | `str` |

**Status:**
Active

---

## Class

### QueryEngine

**Category:** Query Expansion Component

**Purpose:**
Generates and filters alternative search queries from an original user query.

**Constructor:**

* `__init__(llm)`

**Public Method:**

* `expand(query)`

**Status:**
Active

---

## Class

### WebRetrieverTool

**Category:** Concrete Tool

**Purpose:**
Retrieves relevant information from external web sources and produces bounded web context.

**Tool Name:**

`web_retriever`

**Priority:**

`3`

**Argument Schema:**

* `WebRetrieverArgs`

**Intent Metadata:**

* `learn`
* `explain`
* `understand`
* `what is`
* `who is`
* `concept`

**Entity Metadata:**

* `internet`
* `web`
* `online`

**Context Requirements:**

None

**Produced Context:**

* `web`

**Constructor Dependency:**

* `llm`

**Public Method:**

* `run(**kwargs)`

**Status:**
Active

---

# rag/embedder.py

## Class

### Embedder

**Category:** RAG Component

**Purpose:**
Generates vector embeddings for text using a Sentence Transformer model.

**Constructor:**

* Initializes `SentenceTransformer("all-MiniLM-L6-v2")`

**Public Method:**

* `embed(texts)`

**Status:**
Active

---

# rag/ingestor.py

## Class

### Ingestor

**Category:** RAG Component

**Purpose:**
Loads supported documents, chunks their text, generates embeddings, and stores the resulting text chunks and vectors.

**Constructor Dependencies:**

* `embedder`
* `store`

**Public Method:**

* `load_file(file_path: str)`

**Supported Extensions:**

* `.pdf`
* `.txt`
* `.md`

**Status:**
Active

---

# rag/loader.py

## Public Function

### `chunk_text(text, chunk_size=200)`

**Category:** RAG Utility

**Purpose:**
Splits document text into word-based chunks.

**Default Chunk Size:**

`200`

**Status:**
Active

---

# rag/qa.py

## Class

### RAGQA

**Category:** RAG Question Answering

**Purpose:**
Coordinates document loading, document availability checks, retrieval, context construction, and LLM-based question answering.

**Constructor Dependencies:**

* `retriever`
* `ingestor`

**Public Methods:**

* `load_file(file_path: str)`
* `has_documents()`
* `answer(query: str)`

**Status:**
Active

---

# rag/retriever.py

## Class

### Retriever

**Category:** RAG Retrieval

**Purpose:**
Embeds a query and retrieves the most similar stored document chunks.

**Constructor Dependencies:**

* `embedder`
* `store`

**Public Method:**

* `retrieve(query, top_k=3)`

**Status:**
Active

---

# rag/store.py

## Class

### VectorStore

**Category:** RAG Storage

**Purpose:**
Stores document text chunks and vector embeddings and performs similarity-based retrieval.

**State:**

* `vectors`
* `texts`

**Public Methods:**

* `add(texts, embeddings)`
* `search(query_embedding, top_k=3)`

**Similarity Method:**

Cosine similarity implemented through NumPy vector operations.

**Status:**
Active

---

# rag/loaders/pdf_loader.py

## Public Function

### `load_pdf()`

**Category:** Document Loader

**Purpose:**
Loads text content from PDF documents.

**Status:**
Active

---

# rag/loaders/text_loader.py

## Public Function

### `load_txt()`

**Category:** Document Loader

**Purpose:**
Loads text content from plain-text documents.

**Status:**
Active

---

# rag/loaders/md_loader.py

## Public Function

### `load_md()`

**Category:** Document Loader

**Purpose:**
Loads text content from Markdown documents.

**Status:**
Active

---

# retriever/reranker.py

## Class

### Reranker

**Category:** Retrieval Component

**Purpose:**
Reranks retrieved documents according to their relevance to a query.

**Constructor:**

* `__init__(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")`

**Public Method:**

* `rerank(query: str, documents: list[str], top_k: int = 3)`

**Implementation:**

Uses a Sentence Transformers `CrossEncoder` model to score query-document pairs.

**Status:**
Active

---

# retriever/text_extractor.py

## Class

### TextExtractor

**Category:** Retrieval Component

**Purpose:**
Extracts usable text from HTML content while removing common page-noise elements.

**Public Method:**

* `extract(html: str)`

**Extraction Behavior:**

* Removes `script`
* Removes `style`
* Removes `nav`
* Removes `footer`
* Extracts Wikipedia infobox content when present
* Extracts sufficiently long paragraph text

**Status:**
Active

---

# retriever/web_fetcher.py

## Class

### WebFetcher

**Category:** Retrieval Component

**Purpose:**
Fetches web page content for external information retrieval.

**Public Method:**

* `fetch(url)`

**Status:**
Active

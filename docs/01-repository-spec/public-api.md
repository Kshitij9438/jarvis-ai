# Public API

This document defines the public interfaces exposed by the JARVIS repository.

Public APIs include classes, public methods, public functions, public data
models, and concrete tool interfaces that are intended to be consumed by
other repository components.

Internal helper methods are documented only when they are useful for
understanding the behavior of a public interface. They are not considered
part of the primary public API.

The source code is the authoritative reference when this document conflicts
with implementation.

---

# `config`

## `config/settings.py`

### Public Class

#### `Settings`

**Purpose**

Central configuration model for the application.

**Public Method**

```text
from_env()
```

**Configuration Fields**

* `model_name`
* `temperature`

### Public Object

#### `settings`

**Purpose**

Shared configuration instance created during module initialization.

Runtime components consume this configuration object rather than creating
independent configuration instances.

---

# `brain`

## `brain/llm.py`

### Public Class

#### `ReflectionSchema`

**Type**

Pydantic model.

**Purpose**

Represents the structured result of an evaluation reflection.

**Fields**

* `status`
* `reason`

---

### Public Class

#### `LLM`

**Purpose**

Provides the primary abstraction over the configured language model.

**Public Methods**

```text
generate_text()
generate_structured()
generate_plan()
generate_reflection()
```

**Relevant Internal Methods**

```text
_call()
_clean_json()
```

**Relevant Internal Helpers**

```text
_placeholder_for_type()
_example_from_schema()
```

The internal methods above support the public LLM interface but are not
themselves considered primary external APIs.

---

# `calculator`

## `calculator/parser.py`

### Public Class

#### `CalculatorParser`

**Purpose**

Parses supported natural-language mathematical requests into normalized
mathematical expressions.

**Public Method**

```text
parse(text: str) -> Optional[str]
```

### Internal Parsing Methods

```text
_normalize()
_parse_direct_expression()
_parse_percent()
_parse_power()
_parse_sqrt()
_parse_binary()
```

`parse()` is the public entry point for the parser.

---

# `interface`

## `interface/cli.py`

### Public Class

#### `CLI`

**Purpose**

Provides the interactive command-line interface for user interaction.

**Constructor**

```text
__init__()
```

**Public Method**

```text
run()
```

**Responsibilities**

* Initialize the LLM interface.
* Read user input.
* Display model responses.
* Terminate on the `exit` command.

The CLI is the user-interaction boundary and does not constitute the
planning or execution API.

---

# `planner`

## `planner/planner.py`

### Public Class

#### `Planner`

**Purpose**

Coordinates the planning pipeline and produces structured planning output.

**Constructor**

```text
Planner(registry)
```

**Public Method**

```text
plan(user_input, context=None)
```

**Responsibilities**

* Initialize planning components.
* Select candidate tools.
* Extract entities and arguments.
* Construct planning tasks.
* Optimize planning artifacts.
* Validate planning artifacts.
* Score planning candidates.
* Apply planning refinement.
* Resolve planning dependencies.
* Produce a `Plan`.

### Relevant Internal Methods

```text
_should_use_retriever()
_is_trivial_input()
```

---

## `planner/intent.py`

### Public Class

#### `IntentOutput`

**Type**

Pydantic model.

**Purpose**

Represents the structured output of intent classification.

**Fields**

* `intents`

### Public Function

#### `classify_intent()`

**Purpose**

Classifies user input into planner-relevant intents.

---

## `planner/tool_selector.py`

### Public Class

#### `ToolSelector`

**Purpose**

Selects candidate tools for a user query using filtering, intent detection,
scoring, and fallback behavior.

**Public Method**

```text
select(query, top_k=2, context=None)
```

**Inputs**

* User query
* Tool registry
* Optional runtime context

**Output**

* Ranked candidate tools

### Relevant Internal Methods

```text
_hard_filter()
_detect_intents()
_score_tools()
_safe_fallback()
```

---

## `planner/entity_extractor.py`

### Public Class

#### `EntityExtractor`

**Purpose**

Extracts structured entities from natural-language input.

**Public Method**

```text
extract(user_input: str) -> dict
```

**Returned Entity Categories**

The extracted result may contain:

* `websites`
* `file_path`
* `topics`

### Internal Extraction State

* `STOPWORDS`
* `KNOWN_SITES`
* `LEARN_WORDS`
* `FILLER_WORDS`

---

## `planner/arg_extractor.py`

### Public Class

#### `ArgumentSchema`

**Type**

Pydantic model.

**Purpose**

Defines the structured argument representation used during argument
extraction.

**Fields**

* `url`
* `path`
* `question`
* `operation`
* `topic`
* `expression`
* `target`

### Public Class

#### `ArgExtractor`

**Purpose**

Extracts structured execution arguments from user input.

**Public Method**

```text
extract(user_input: str) -> dict
```

**Dependency**

* LLM instance

---

## `planner/task_builder.py`

### Public Class

#### `TaskBuilder`

**Purpose**

Constructs planning tasks from selected tools, extracted entities, and
extracted arguments.

**Public Construction Interface**

```text
build_tasks(...)
```

**Responsibilities**

* Create task objects.
* Associate tools with tasks.
* Attach extracted entities.
* Attach extracted arguments.
* Produce planning task collections.

---

## `planner/optimizer.py`

### Public Class

#### `TaskOptimizer`

**Purpose**

Optimizes task collections produced by the planning pipeline.

**Public Method**

```text
optimize(...)
```

**Responsibilities**

* Analyze task collections.
* Apply optimization rules.
* Return optimized planning artifacts.

---

## `planner/validator.py`

### Public Class

#### `PlanValidator`

**Purpose**

Performs structural validation of planner-generated artifacts.

**Public Method**

```text
validate(...)
```

**Responsibilities**

* Verify planning artifacts.
* Detect invalid planning output.
* Produce validation results.

---

## `planner/intelligence.py`

### Public Class

#### `PlannerIntelligence`

**Purpose**

Refines planner-generated artifacts using additional reasoning.

**Public Method**

```text
refine(...)
```

**Responsibilities**

* Analyze completed planning artifacts.
* Improve planning quality.
* Return refined planning artifacts.

---

## `planner/scorer.py`

### Public Class

#### `PlanScorer`

**Purpose**

Scores candidate planning artifacts.

**Public Method**

```text
score(...)
```

**Responsibilities**

* Evaluate candidate plans.
* Compute plan scores.
* Return scoring information used by the planning pipeline.

---

## `planner/dependency_resolver.py`

### Public Class

#### `DependencyResolver`

**Purpose**

Determines dependencies between planner-generated tasks and establishes
dependency-aware planning output.

**Public Method**

```text
resolve(...)
```

**Responsibilities**

* Analyze task relationships.
* Construct dependency information.
* Determine execution ordering.
* Return dependency-aware planning output.

---

## `planner/task.py`

### Public Class

#### `Task`

**Type**

Python dataclass.

**Purpose**

Represents a planning task.

**Fields**

* `type`
* `target`
* `file_path`
* `query`

**Public Methods**

None explicitly defined.

The constructor is generated by the dataclass implementation.

---

## `planner/schema.py`

### Public Class

#### `Action`

**Type**

Pydantic model.

**Purpose**

Represents an executable action in a structured plan.

**Fields**

* `action`
* `args`

### Public Class

#### `Plan`

**Type**

Pydantic model.

**Purpose**

Represents an ordered executable plan.

**Fields**

* `steps`

`steps` contains the ordered `Action` objects representing the plan.

---

## `planner/control.py`

### Public Function

#### `control_layer(user_input, intents)`

**Purpose**

Constructs a deterministic `Plan` for supported high-confidence requests.

**Returns**

* `Plan`
* `None`

### Public Function

#### `is_high_confidence(intents)`

**Purpose**

Determines whether deterministic rule-based planning should be used for the
supplied intents.

> This module belongs to the **planning subsystem**. It is distinct from
> `control/control_layer.py`, which performs runtime plan refinement.

---

## `planner/completeness.py`

### Public Function

#### `check_completeness(...)`

**Purpose**

Checks whether planner-generated tasks contain the information required for
execution.

**Returns**

* Completeness result
* Missing requirements

---

## `planner/plan_variants.py`

### Public Class

#### `PlanVariant`

**Purpose**

Represents an individual candidate planning alternative.

### Public Class

#### `PlanVariants`

**Purpose**

Represents a collection of candidate planning alternatives.

The concrete variant-management behavior is defined by the implementation in
`planner/plan_variants.py`.

---

## `planner/llm_enhancer.py`

### Public Class

#### `LLMEnhancer`

**Purpose**

Enhances planner-generated artifacts through LLM-assisted processing.

**Public Method**

```text
enhance(...)
```

---

## `planner/tool_prompt.py`

### Public Function

#### `build_tool_prompt(...)`

**Purpose**

Constructs prompts for tool-aware LLM planning.

**Returns**

* Prompt string

---

# `control`

## `control/control_layer.py`

### Public Class

#### `ControlLayer`

**Purpose**

Refines planner-generated plans into execution-ready plans through runtime
control logic.

**Public Method**

```text
refine_plan(plan, context)
```

**Input**

* `Plan`
* Runtime context

**Output**

* Refined `Plan`

This component belongs to the runtime `control/` subsystem and is distinct
from `planner/control.py`.

---

## `control/execution_loop.py`

### Public Class

#### `ExecutionLoop`

**Purpose**

Coordinates runtime execution until the request reaches a terminal state.

**Public Method**

```text
run(...)
```

**Consumes**

* Refined `Plan`
* Runtime context

**Produces**

* Execution results

---

## `control/evaluator.py`

### Public Class

#### `EvaluationResult`

**Purpose**

Represents the structured result of execution evaluation.

**Fields**

* `success`
* `confidence`
* `reason`

### Public Class

#### `Evaluator`

**Purpose**

Determines whether execution achieved the intended user goal.

**Public Method**

```text
evaluate(...)
```

**Consumes**

* Execution results
* User goal

**Produces**

* `EvaluationResult`

---

# `execution`

## `execution/context.py`

### Public Class

#### `ExecutionContext`

**Purpose**

Represents runtime execution context shared across execution stages and
tools.

The concrete context operations are defined by the implementation.

---

## `execution/context_dependency.py`

### Public Class

#### `ContextDependencyResolver`

**Purpose**

Resolves runtime context dependencies required by executable components.

The concrete public interface is defined by the implementation in
`execution/context_dependency.py`.

---

## `execution/context_signals.py`

### Public Functions

#### `is_document_loaded(...)`

**Purpose**

Determines whether document context is available in the runtime context.

#### `has_retrieved_content(...)`

**Purpose**

Determines whether retrieved web content is available in the runtime
context.

---

# `executor`

## `executor/executor.py`

### Public Class

#### `Executor`

**Purpose**

Executes actions from a `Plan` against registered tools and produces
structured execution results.

**Public Method**

```text
execute(plan, context=None)
```

**Consumes**

* `Plan`
* Runtime context

**Produces**

* Execution results

Each executed step produces structured execution information containing the
step identity, success state, result, and error information where applicable.

---

# `tools`

## `tools/base.py`

### Public Class

#### `BaseTool`

**Purpose**

Defines the common interface and metadata contract implemented by executable
tools.

### Public Attributes

**Core Identity**

* `name`
* `description`
* `args_schema`

**Matching Metadata**

* `intents`
* `entities`

**Execution Metadata**

* `priority`

**Context Contract**

* `requires_context`
* `produces_context`

**Legacy Dependency Metadata**

* `requires`

### Public Method

```text
run(**kwargs)
```

Concrete tools implement their capabilities through this method.

---

## `tools/registry.py`

### Public Class

#### `ToolRegistry`

**Purpose**

Maintains the runtime catalog of registered executable tools.

The registry provides the tool registration, lookup, enumeration, and related
operations implemented by `tools/registry.py`.

---

## `tools/semantic_matcher.py`

### Public Class

#### `SemanticMatcher`

**Purpose**

Produces embedding-based similarity information used for semantic tool
matching.

**Public Methods**

```text
embed(text)
register_tool(tool)
similarity(query, tool)
```

---

## `tools/basic_tools.py`

### Public Class

#### `OpenWebsiteArgs`

**Type**

Pydantic model.

**Fields**

```text
url: str
```

### Public Class

#### `OpenWebsiteTool`

**Tool Name**

```text
open_website
```

**Description**

Opens a supplied URL using the system browser.

**Argument Schema**

* `OpenWebsiteArgs`

**Priority**

```text
1
```

**Context Contract**

* Requires: none
* Produces: `web`

**Public Method**

```text
run(**kwargs)
```

### Public Class

#### `EchoArgs`

**Type**

Pydantic model.

**Fields**

```text
text: str
```

### Public Class

#### `EchoTool`

**Tool Name**

```text
echo
```

**Description**

Returns supplied text unchanged.

**Argument Schema**

* `EchoArgs`

**Priority**

```text
10
```

**Context Contract**

* Requires: none
* Produces: none

**Public Method**

```text
run(**kwargs)
```

---

## `tools/calculator_tool.py`

### Public Class

#### `CalculatorArgs`

**Type**

Pydantic model.

**Fields**

```text
expression: str
```

### Public Class

#### `SafeEvaluator`

**Purpose**

Evaluates mathematical expressions using a restricted set of supported AST
nodes, operators, and functions.

**Public Method**

```text
eval(expression)
```

### Public Class

#### `ExpressionNormalizer`

**Purpose**

Converts supported natural-language mathematical input into normalized
mathematical expression syntax.

**Public Method**

```text
normalize(text)
```

### Public Class

#### `CalculatorTool`

**Tool Name**

```text
calculator
```

**Description**

Evaluates mathematical expressions through the calculator tool interface.

**Argument Schema**

* `CalculatorArgs`

**Context Contract**

* Requires: none
* Produces: `calculation`

**Priority**

```text
1
```

**Public Method**

```text
run(**kwargs)
```

**Execution Flow**

```text
Expression
    ↓
ExpressionNormalizer.normalize()
    ↓
SafeEvaluator.eval()
    ↓
Formatted Result
```

**Failure Behavior**

Missing expression:

```text
⚠️ No expression provided
```

Evaluation failure:

```text
⚠️ Calculation error: ...
```

---

## `tools/load_doc_tool.py`

### Public Class

#### `LoadDocArgs`

**Type**

Pydantic model.

**Fields**

```text
file_path: str
```

### Public Class

#### `LoadDocTool`

**Tool Name**

```text
load_document
```

**Description**

Loads a supported document into the RAG subsystem.

**Argument Schema**

* `LoadDocArgs`

**Context Contract**

* Requires: none
* Produces: `document`

**Priority**

```text
1
```

**Constructor**

```text
LoadDocTool(rag)
```

**Public Method**

```text
run(**kwargs)
```

**Delegation**

```text
file_path
    ↓
self.rag.load_file(file_path)
    ↓
Return result
```

---

## `tools/rag_tool.py`

### Public Class

#### `RAGArgs`

**Type**

Pydantic model.

**Purpose**

Defines the input argument schema for the RAG tool.

**Field**

* `query`

### Public Class

#### `RAGTool`

**Purpose**

Provides document-based retrieval and question answering through the
injected RAG component.

**Tool Name**

```text
rag_search
```

**Constructor**

```text
RAGTool(rag)
```

**Argument Schema**

* `RAGArgs`

**Context Contract**

* Requires: `document`
* Produces: none

**Legacy Dependency Contract**

```text
requires = ["load_document"]
```

**Public Method**

```text
run(**kwargs)
```

---

## `tools/explain_tool.py`

### Public Class

#### `ExplainArgs`

**Type**

Pydantic model.

**Purpose**

Defines the arguments supplied to the explanation tool.

### Public Class

#### `ExplainTool`

**Purpose**

Generates an explanation for a query, optionally using supplied context.

**Constructor Dependency**

* LLM

**Public Method**

```text
run(**kwargs)
```

**Execution Behavior**

* With context, constructs a context-grounded explanation prompt.
* Without context, constructs a direct explanation prompt.
* Sends the resulting prompt to the LLM.

---

## `tools/web_retriever_tool.py`

### Public Class

#### `WebRetrieverArgs`

**Type**

Pydantic model.

**Fields**

```text
query: str
```

### Public Class

#### `QueryEngine`

**Purpose**

Generates and filters expanded search queries.

**Public Method**

```text
expand(query)
```

**Input**

* Original search query

**Output**

* Filtered expanded search queries

**Behavior**

* Uses the injected LLM to generate search queries.
* Filters generated queries using constraints derived from the original
  query.
* Removes queries exceeding the implemented word limit.
* Falls back to the original query when no generated query survives
  filtering.

### Public Class

#### `WebRetrieverTool`

**Tool Name**

```text
web_retriever
```

**Description**

Retrieves relevant information from external web sources.

**Argument Schema**

* `WebRetrieverArgs`

**Context Contract**

* Requires: none
* Produces: `web`

**Priority**

```text
3
```

**Constructor**

```text
WebRetrieverTool(llm)
```

**Public Method**

```text
run(**kwargs)
```

**Execution Flow**

```text
Query
    ↓
Clean Query
    ↓
Query Expansion
    ↓
Web / Wikipedia Retrieval
    ↓
Text Extraction
    ↓
Deduplication
    ↓
Reranking
    ↓
Context Merge
    ↓
Web Context
```

---

# `rag`

## `rag/embedder.py`

### Public Class

#### `Embedder`

**Purpose**

Generates vector embeddings for supplied text.

**Constructor**

```text
Embedder()
```

**Public Method**

```text
embed(texts)
```

**Implementation**

Uses a Sentence Transformer embedding model.

---

## `rag/ingestor.py`

### Public Class

#### `Ingestor`

**Purpose**

Loads supported documents, chunks their text, generates embeddings, and
stores the resulting chunks and vectors.

**Constructor**

```text
Ingestor(embedder, store)
```

**Public Method**

```text
load_file(file_path: str)
```

**Supported File Types**

* `.pdf`
* `.txt`
* `.md`

---

## `rag/loader.py`

### Public Function

#### `chunk_text(text, chunk_size=200)`

**Purpose**

Splits document text into word-based chunks.

**Default Chunk Size**

```text
200
```

**Returns**

* List of text chunks

---

## `rag/qa.py`

### Public Class

#### `RAGQA`

**Purpose**

Coordinates document loading, document availability checks, retrieval,
context construction, and LLM-based question answering.

**Constructor**

```text
RAGQA(retriever, ingestor)
```

**Public Methods**

```text
load_file(file_path: str)
has_documents()
answer(query: str)
```

---

## `rag/retriever.py`

### Public Class

#### `Retriever`

**Purpose**

Embeds a query and retrieves the most relevant stored document chunks.

**Constructor**

```text
Retriever(embedder, store)
```

**Public Method**

```text
retrieve(query, top_k=3)
```

---

## `rag/store.py`

### Public Class

#### `VectorStore`

**Purpose**

Stores document text and vector embeddings and performs similarity-based
retrieval.

**Public Methods**

```text
add(texts, embeddings)
search(query_embedding, top_k=3)
```

---

## `rag/loaders/pdf_loader.py`

### Public Function

#### `load_pdf(...)`

**Purpose**

Loads text from PDF documents.

---

## `rag/loaders/text_loader.py`

### Public Function

#### `load_txt(...)`

**Purpose**

Loads text from plain-text documents.

---

## `rag/loaders/md_loader.py`

### Public Function

#### `load_md(...)`

**Purpose**

Loads text from Markdown documents.

---

# `retriever`

## `retriever/web_fetcher.py`

### Public Class

#### `WebFetcher`

**Purpose**

Fetches web page content for external information retrieval.

---

## `retriever/text_extractor.py`

### Public Class

#### `TextExtractor`

**Purpose**

Extracts usable text from fetched HTML content.

**Public Method**

```text
extract(html: str)
```

---

## `retriever/reranker.py`

### Public Class

#### `Reranker`

**Purpose**

Scores and reranks retrieved documents according to query relevance.

**Constructor**

```text
Reranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
```

**Public Method**

```text
rerank(query: str, documents: list[str], top_k: int = 3)
```

---

# Public API Boundaries

The repository's public interfaces can be grouped into the following
categories:

| Category             | Primary Public Interface                                    |
| -------------------- | ----------------------------------------------------------- |
| Configuration        | `Settings`, `settings`                                      |
| LLM                  | `LLM`, `ReflectionSchema`                                   |
| Mathematical Parsing | `CalculatorParser`                                          |
| User Interface       | `CLI`                                                       |
| Planning             | `Planner` and planning components                           |
| Runtime Control      | `ControlLayer`, `ExecutionLoop`, `Evaluator`                |
| Runtime Context      | `ExecutionContext`, `ContextDependencyResolver`             |
| Execution            | `Executor`                                                  |
| Tool Framework       | `BaseTool`, `ToolRegistry`, `SemanticMatcher`               |
| Concrete Tools       | Tool classes under `tools/`                                 |
| Document RAG         | `Embedder`, `Ingestor`, `RAGQA`, `Retriever`, `VectorStore` |
| External Retrieval   | `WebFetcher`, `TextExtractor`, `Reranker`                   |

---

# Public API Rules

1. Public interfaces should remain consistent with their source
   implementations.
2. Internal helper methods should not be treated as stable external APIs.
3. Tool implementations expose their capability through the `BaseTool`
   contract.
4. Runtime execution should consume planning artifacts rather than
   reimplement planning logic.
5. `planner/control.py` and `control/control_layer.py` represent different
   responsibilities and must not be treated as the same public component.
6. Documentation should not claim a public method or signature that is not
   present in the implementation.
7. When the implementation changes, this document should be updated together
   with the corresponding module and class indexes.

---

# Source-of-Truth Rule

This document describes the public interfaces identified during repository
analysis.

The source code remains authoritative.

If a documented API conflicts with the implementation, the implementation
takes precedence and this document must be updated accordingly.

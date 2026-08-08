# Runtime Index

## Purpose

This document describes the principal runtime objects and intermediate
artifacts that move through the JARVIS execution lifecycle.

It focuses on:

- Runtime object ownership
- Object creation
- Object consumption
- Object lifetime
- Major transformations between runtime stages

This document does not redefine class ownership or public APIs.

The source implementation remains the authoritative source if a runtime
description conflicts with the code.

---

# Runtime Lifecycle

The principal application lifecycle is:

```text
User Input
    │
    ▼
CLI / Application Runtime
    │
    ▼
Planner
    │
    ├── Tool Selection
    ├── Entity Extraction
    ├── Argument Extraction
    ├── Task Construction
    ├── Dependency Resolution
    ├── Optimization
    ├── Validation
    ├── Scoring / Intelligence
    │
    ▼
Plan
    │
    ▼
Control Layer
    │
    ▼
Refined Plan
    │
    ▼
Execution Loop
    │
    ▼
Executor
    │
    ├── Tool 1
    ├── Tool 2
    └── ...
    │
    ▼
Execution Results
    │
    ▼
Evaluator
    │
    ▼
Evaluation Result
    │
    ▼
Execution Loop / Application
```

Runtime context may participate across the planning, control, and execution
stages where required.

---

# Configuration Runtime Objects

## Settings

**Type**

Configuration object.

**Created By**

```text
Settings.from_env()
```

**Owner**

```text
config/settings.py
```

**Read By**

Repository components requiring application configuration.

**Mutated By**

None observed after initialization.

**Lifetime**

```text
Application startup
        ↓
Process termination
```

**Purpose**

Provides the application's centralized runtime configuration.

---

# LLM Runtime Objects

## LLM

**Type**

Service object.

**Created By**

`LLM()`

**Owner**

```text
brain/llm.py
```

**Read By**

Components requiring language-model functionality, including planning and
evaluation components.

**Mutated By**

No externally visible runtime mutation established.

**Lifetime**

Created when required by consuming components.

**Purpose**

Provides the runtime interface to the configured language model.

---

# Interface Runtime Objects

## CLI

**Type**

Interactive service.

**Created By**

Application startup.

**Owner**

```text
interface/cli.py
```

**Creates / Uses**

- Console
- LLM interface

**Reads**

- User terminal input

**Produces**

- Console output

**Lifetime**

```text
Application startup
        ↓
Process termination
```

**Purpose**

Maintains the user-facing interactive terminal session.

---

# Planning Runtime Objects

## Planner

**Type**

Planning orchestrator.

**Created By**

Application initialization.

**Owner**

```text
planner/planner.py
```

**Creates / Coordinates**

- LLM interface
- `ArgExtractor`
- `TaskBuilder`
- `EntityExtractor`
- `TaskOptimizer`
- `PlanValidator`
- `PlannerIntelligence`
- `PlanScorer`
- `ToolSelector`
- `ControlLayer`
- `ContextDependencyResolver`

**Reads**

- User input
- Tool registry
- Optional runtime context

**Produces**

- Planning artifacts
- Final planning `Plan`

**Lifetime**

```text
Application startup
        ↓
Process termination
```

**Purpose**

Coordinates the planning pipeline.

---

## Candidate Tool List

**Type**

Ranked collection of candidate tools.

**Created By**

```text
ToolSelector.select()
```

**Owner**

```text
planner/tool_selector.py
```

**Reads**

- User query
- Tool registry metadata
- Optional semantic similarity information

**Produces**

- Ranked candidate tools

**Mutated By**

None observed.

**Lifetime**

```text
Tool-selection stage only
```

---

## Extracted Entities

**Type**

Dictionary.

**Created By**

```text
EntityExtractor.extract()
```

**Owner**

```text
planner/entity_extractor.py
```

**Fields**

- `websites`
- `file_path`
- `topics`

**Reads**

- User input

**Produces**

- Structured entity dictionary

**Mutated By**

Extraction and cleanup stages before being returned.

**Lifetime**

```text
Entity extraction
        ↓
Task construction
```

---

## Extracted Arguments

**Type**

Dictionary.

**Created By**

```text
ArgExtractor.extract()
```

**Owner**

```text
planner/arg_extractor.py
```

**Source Model**

`ArgumentSchema`

**Reads**

- User input

**Produces**

- Structured argument dictionary

**Mutated By**

No mutation observed after conversion from the schema representation.

**Lifetime**

```text
Argument extraction
        ↓
Task construction
```

---

# Task Runtime Objects

## Task

**Type**

Dataclass / planning domain object.

**Created By**

```text
TaskBuilder.build()
```

**Owner**

```text
planner/task.py
```

**Reads**

- Selected tools
- Extracted entities
- Extracted arguments

**Used By**

- Planner
- Optimizer
- Validator
- DependencyResolver
- Executor

**Mutated By**

Planning stages that operate on task collections.

**Lifetime**

```text
Task construction
        ↓
Dependency resolution
        ↓
Optimization
        ↓
Validation
        ↓
Execution
```

**Fields**

- `type`
- `target`
- `file_path`
- `query`

**Purpose**

Carries planning information through the planning pipeline.

---

# Dependency Runtime Artifacts

## Dependency Graph

**Type**

Directed task dependency structure.

**Created By**

```text
DependencyResolver.resolve()
```

**Owner**

```text
planner/dependency_resolver.py
```

**Reads**

- Task collection

**Produces**

- Dependency-aware ordering information

**Mutated By**

None observed after dependency resolution.

**Lifetime**

```text
Dependency resolution
        ↓
Downstream planning stages
```

**Purpose**

Represents relationships and ordering constraints between planner tasks.

---

# Optimization Runtime Artifacts

## Optimized Task Collection

**Type**

Task collection.

**Created By**

```text
TaskOptimizer.optimize()
```

**Owner**

```text
planner/optimizer.py
```

**Reads**

- Planner-generated tasks

**Produces**

- Optimized task collection

**Mutated By**

Subsequent planning stages may consume or transform the collection.

**Lifetime**

```text
Optimization
        ↓
Validation
```

---

# Validation Runtime Artifacts

## Validation Result

**Type**

Validation outcome.

**Created By**

```text
PlanValidator.validate()
```

**Owner**

```text
planner/validator.py
```

**Reads**

- Planner-generated planning artifacts

**Produces**

- Validation outcome

**Purpose**

Indicates whether the relevant planning artifacts satisfy the required
structural conditions.

**Mutated By**

None observed.

**Lifetime**

```text
Validation stage
```

---

# Scoring Runtime Artifacts

## Plan Score

**Type**

Numeric evaluation.

**Created By**

```text
PlanScorer.score()
```

**Owner**

```text
planner/scorer.py
```

**Reads**

- Candidate planning artifacts

**Produces**

- Score information associated with candidate plans

**Mutated By**

None observed.

**Lifetime**

```text
Scoring stage
```

---

# Planning Refinement Artifacts

## Refined Planning Artifact

**Type**

Plan or planning artifact.

**Created By**

```text
PlannerIntelligence.refine()
```

**Owner**

```text
planner/intelligence.py
```

**Reads**

- Validated planning artifacts

**Produces**

- Refined planning artifact

**Lifetime**

```text
Planning refinement
        ↓
Control / downstream planning stages
```

**Purpose**

Represents the output of planner-level reasoning/refinement.

---

## Enhanced Plan

**Type**

Plan.

**Created By**

```text
LLMEnhancer.enhance()
```

**Owner**

```text
planner/llm_enhancer.py
```

**Consumed By**

- Planner

**Lifetime**

```text
LLM enhancement stage
```

**Purpose**

Represents planning output enhanced through the LLM-assisted enhancement
component.

---

# Plan Schema Objects

## Action

**Type**

Pydantic model.

**Owner**

```text
planner/schema.py
```

**Fields**

- `action`
- `args`

**Produced By**

Planner planning pipeline.

**Consumed By**

Executor.

**Purpose**

Represents one executable action within a `Plan`.

---

## Plan

**Type**

Pydantic model.

**Owner**

```text
planner/schema.py
```

**Fields**

- `steps`

**Produced By**

Planning pipeline.

**Consumed By**

- Control layer
- Executor

**Purpose**

Represents an ordered collection of executable actions.

---

# Deterministic Fallback Planning

## Rule-Based Plan

**Type**

`Plan`

**Created By**

```text
planner/control.py
```

**Owner**

`planner/control.py` for the **construction logic**.

**Underlying Type Owner**

```text
planner/schema.py
```

**Condition**

Created only for supported high-confidence intents.

**Lifetime**

```text
Rule evaluation
        ↓
Plan construction
        ↓
Planner pipeline
```

**Important Distinction**

`planner/control.py` does not define the `Plan` schema.

It constructs a `Plan` object defined by `planner/schema.py`.

---

# Completeness Runtime Artifacts

## Completeness Assessment

**Type**

Verification result.

**Created By**

```text
check_completeness(...)
```

**Owner**

```text
planner/completeness.py
```

**Consumed By**

- Planner pipeline

**Purpose**

Represents whether required planning information is present and identifies
missing requirements where applicable.

**Lifetime**

```text
Planning phase
```

---

# Plan Variant Runtime Objects

## PlanVariant

**Type**

Planning model.

**Created By**

Planner pipeline.

**Owner**

```text
planner/plan_variants.py
```

**Consumed By**

- Plan scoring
- Planner

**Purpose**

Represents one candidate planning alternative.

---

## PlanVariants

**Type**

Collection model.

**Created By**

Planner pipeline.

**Owner**

```text
planner/plan_variants.py
```

**Consumed By**

- Planner
- PlanScorer

**Purpose**

Represents a collection of candidate planning alternatives.

---

# Prompt Runtime Artifacts

## Tool Prompt

**Type**

String.

**Created By**

```text
build_tool_prompt(...)
```

**Owner**

```text
planner/tool_prompt.py
```

**Consumed By**

- LLM-dependent planning components
- `brain/llm.py`

**Lifetime**

Single planning request / prompt construction stage.

**Purpose**

Provides tool-aware prompt content to the LLM planning pipeline.

---

# Runtime Control Objects

## Refined Plan

**Type**

`Plan`.

**Created By**

```text
ControlLayer.refine_plan()
```

**Owner**

```text
control/control_layer.py
```

**Consumes**

- Planner-generated plan
- Runtime context

**Consumed By**

- `ExecutionLoop`
- Executor

**Lifetime**

```text
Plan refinement
        ↓
Execution
```

**Purpose**

Represents the plan after runtime control-layer refinement.

---

# Execution Runtime Objects

## Execution Result

**Type**

Structured execution result.

**Created By**

```text
Executor.execute()
```

**Owner**

```text
executor/executor.py
```

**Consumed By**

- Evaluator
- ExecutionLoop
- Application runtime

**Typical Structure**

```text
{
    step,
    success,
    result,
    error
}
```

**Purpose**

Represents the outcome of an individual executed action.

---

## Execution Result Collection

**Type**

List of execution results.

**Created By**

```text
Executor.execute()
```

**Owner**

```text
executor/executor.py
```

**Contains**

- One execution result per executed action.

**Consumed By**

- `ExecutionLoop`
- `Evaluator`
- Application runtime

**Lifetime**

```text
Execution
        ↓
Evaluation
        ↓
Runtime completion
```

---

# Evaluation Runtime Objects

## Evaluation Result

**Type**

Evaluation outcome.

**Created By**

```text
Evaluator.evaluate()
```

**Owner**

```text
control/evaluator.py
```

**Reads**

- Execution results
- User goal / intended objective

**Consumed By**

- `ExecutionLoop`

**Purpose**

Represents the evaluator's assessment of whether execution achieved the
intended goal.

**Lifetime**

```text
Evaluation stage
        ↓
Execution-loop decision
```

---

# Tool Runtime Objects

## Tool Instance

**Type**

Concrete `BaseTool` implementation.

**Created By**

Application initialization / tool registry setup.

**Owner**

Concrete tool module.

**Consumed By**

- ToolRegistry
- ToolSelector
- Executor

**Purpose**

Represents an executable capability registered with the application.

---

## OpenWebsiteTool Result

**Created By**

```text
OpenWebsiteTool.run()
```

**Owner**

```text
tools/basic_tools.py
```

**Produces**

- Browser-opening confirmation string
- `web` context according to the tool contract

**Consumed By**

- Executor
- Runtime context where applicable

---

## EchoTool Result

**Created By**

```text
EchoTool.run()
```

**Owner**

```text
tools/basic_tools.py
```

**Produces**

- Echoed input text

**Consumed By**

- Executor

---

# Runtime Context

Runtime context is a cross-cutting execution concern.

It may be consumed by planning, control, execution, and tools according to
declared context dependencies.

The primary ownership boundary is:

```text
execution/
```

while the executor is responsible for applying context to individual tool
executions.

---

# Object Lifetime Summary

| Runtime Object | Created By | Primary Owner | Main Lifetime |
|---|---|---|---|
| `Settings` | `Settings.from_env()` | `config/settings.py` | Application lifetime |
| `LLM` | `LLM()` | `brain/llm.py` | Consumer-defined |
| `CLI` | Application startup | `interface/cli.py` | Application lifetime |
| `Planner` | Application initialization | `planner/planner.py` | Application lifetime |
| Candidate Tool List | `ToolSelector.select()` | `planner/tool_selector.py` | Selection stage |
| Extracted Entities | `EntityExtractor.extract()` | `planner/entity_extractor.py` | Planning stage |
| Extracted Arguments | `ArgExtractor.extract()` | `planner/arg_extractor.py` | Planning stage |
| `Task` | `TaskBuilder.build()` | `planner/task.py` | Planning → execution |
| Dependency Graph | `DependencyResolver.resolve()` | `planner/dependency_resolver.py` | Dependency stage |
| Optimized Task Collection | `TaskOptimizer.optimize()` | `planner/optimizer.py` | Optimization → validation |
| Validation Result | `PlanValidator.validate()` | `planner/validator.py` | Validation stage |
| Plan Score | `PlanScorer.score()` | `planner/scorer.py` | Scoring stage |
| Refined Planning Artifact | `PlannerIntelligence.refine()` | `planner/intelligence.py` | Planning refinement |
| Enhanced Plan | `LLMEnhancer.enhance()` | `planner/llm_enhancer.py` | Enhancement stage |
| `Action` | Planner pipeline | `planner/schema.py` | Plan lifetime |
| `Plan` | Planner pipeline | `planner/schema.py` | Planning → execution |
| Rule-Based Plan | `planner/control.py` | `planner/control.py` | Fallback planning |
| Completeness Assessment | `check_completeness()` | `planner/completeness.py` | Planning stage |
| `PlanVariant` | Planner | `planner/plan_variants.py` | Candidate planning |
| `PlanVariants` | Planner | `planner/plan_variants.py` | Candidate planning |
| Tool Prompt | `build_tool_prompt()` | `planner/tool_prompt.py` | Prompt construction |
| Refined Plan | `ControlLayer.refine_plan()` | `control/control_layer.py` | Refinement → execution |
| Execution Result | `Executor.execute()` | `executor/executor.py` | Execution → evaluation |
| Evaluation Result | `Evaluator.evaluate()` | `control/evaluator.py` | Evaluation → loop decision |

---

# Runtime Transformation Flow

The major planning transformation can be represented as:

```text
User Input
    │
    ▼
Candidate Tools
    │
    ├───────────────┐
    ▼               ▼
Entities        Arguments
    │               │
    └───────┬───────┘
            ▼
          Tasks
            │
            ▼
     Dependency Information
            │
            ▼
    Optimized Task Collection
            │
            ▼
      Validation Result
            │
            ▼
     Planning Refinement
            │
            ▼
           Plan
```

The runtime execution transformation is:

```text
Plan
    │
    ▼
ControlLayer.refine_plan()
    │
    ▼
Refined Plan
    │
    ▼
ExecutionLoop
    │
    ▼
Executor.execute()
    │
    ▼
Tool Invocation
    │
    ▼
Execution Results
    │
    ▼
Evaluator.evaluate()
    │
    ▼
Evaluation Result
    │
    ▼
ExecutionLoop Decision
```

---

# Context Flow

Context participates in the runtime lifecycle as a separate concern:

```text
Runtime Context
      │
      ├──────────────► Planner
      │
      ├──────────────► Control Layer
      │
      ├──────────────► Executor
      │                    │
      │                    ▼
      │                 Tools
      │                    │
      │                    ▼
      └────────────── Context Updates
```

The executor applies context requirements declared by tools and incorporates
tool-produced context into the runtime execution state where supported.

---

# Runtime Ownership Rules

The following rules govern the runtime-object model:

1. A runtime object's owner is the module responsible for defining or
   managing that object's behavior.
2. A producer creates an object but does not necessarily own its underlying
   type.
3. `planner/control.py` may construct a `Plan`, but `planner/schema.py`
   owns the `Plan` schema.
4. `control/control_layer.py` produces a refined `Plan`, but does not own
   the `Plan` type.
5. `executor/executor.py` owns execution-result generation.
6. `control/evaluator.py` owns evaluation-result generation.
7. `planner/task.py` owns the `Task` data structure.
8. Runtime context belongs to the `execution/` subsystem.
9. Consumers may transform or read runtime objects without acquiring
   ownership of their underlying data model.
10. Runtime-object descriptions must not be used to infer dependencies that
    are not established by the implementation.

---

# Documentation Boundary

This document describes runtime objects and their movement through the
system.

For related information:

- `module-index.md` — module responsibilities
- `class-index.md` — class inventory
- `public-api.md` — public interfaces
- `package-structure.md` — package organization
- `file-ownership.md` — file-level ownership
- `ownership-matrix.md` — responsibility ownership
- `dependency-index.md` — dependency relationships
- `MS.md` — master specification

The source implementation remains the final authority for runtime behavior.
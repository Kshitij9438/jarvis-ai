# Planner Execution Pipeline

## Overview

The planner transforms natural language into an executable plan through a staged pipeline.

Each stage has a single responsibility and delegates to specialized components.

---

## Pipeline

User Input
        │
        ▼
Planner
        │
        ├─────────────┐
        │             │
        ▼             ▼
ToolSelector      EntityExtractor
        │             │
        └──────┬──────┘
               ▼
        ArgExtractor
               ▼
        TaskBuilder
               ▼
    DependencyResolver
               ▼
        TaskOptimizer
               ▼
       PlanValidator
               ▼
     PlannerIntelligence
               ▼
        PlanScorer
               ▼
            Plan
               │
               ▼
         Control Layer
               │
               ▼
           Executor

---

## Responsibilities

| Stage | Responsibility |
|---------|----------------|
| ToolSelector | Select candidate tools |
| EntityExtractor | Extract entities |
| ArgExtractor | Infer structured arguments |
| TaskBuilder | Build runtime tasks |
| DependencyResolver | Resolve ordering |
| Optimizer | Improve task graph |
| Validator | Verify correctness |
| Intelligence | Refine plan |
| Scorer | Evaluate plan |

---

## Characteristics

- Sequential pipeline
- Delegation-based
- Planner owns orchestration
- Components own algorithms
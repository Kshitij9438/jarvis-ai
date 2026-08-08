# Context Flow

Current repository observations

Planner
        │
        ▼
ContextDependencyResolver
        │
        ▼
Control Layer
        │
        ▼
Executor
        │
        ▼
Tools

Context is propagated between stages rather than owned by the planner itself.

Planner

↓

ContextDependencyResolver

↓

Control Layer

↓

Executor

↓

Tools

## Basic Tools Context Flow

### OpenWebsiteTool

```text
OpenWebsiteTool
    │
    ├── requires_context: []
    │
    └── produces_context:
            └── web
```
### EchoTool
```text
EchoTool
    │
    ├── requires_context: []
    │
    └── produces_context: []
```

## Calculator Tool Context Flow

```text
CalculatorTool
    │
    ├── requires_context: []
    │
    └── produces_context:
            └── calculation

The calculator does not consume runtime context during execution.

Its declared output context is calculation.
```

:contentReference[oaicite:13]{index=13}

---

## Load Document Tool Context Flow

```text
LoadDocTool
    │
    ├── requires_context: []
    │
    └── produces_context:
            └── document
```

The tool does not require existing runtime context.

Its declared responsibility is to produce `document` context after loading
the supplied file.

## Web Retriever Context Flow

```text
WebRetrieverTool
    │
    ├── requires_context: []
    │
    └── produces_context:
            └── web
```

The tool does not require previously available runtime context.

Its declared output context is `web`.

The returned context consists of merged, ranked source content and is
bounded by `TOTAL_CHARS`.
User Text

↓

Entities

↓

Arguments

↓

Tasks

↓

Dependency Graph

↓

Optimized Tasks

↓

Validated Tasks

↓

Plan

↓

Actions

↓

Executor

## Basic Tools Data Flow

### OpenWebsiteTool

```text
Action
  ↓
Executor
  ↓
OpenWebsiteTool
  ↓
OpenWebsiteArgs
  ↓
webbrowser.open(url)
  ↓
Confirmation String

```

### EchoTool

```text
Action
  ↓
Executor
  ↓
EchoTool
  ↓
EchoArgs
  ↓
Input Text
  ↓
Returned Text

```

## Calculator Tool Data Flow

```text
User / Planner
      ↓
CalculatorTool
      ↓
CalculatorArgs
      ↓
Expression
      ↓
ExpressionNormalizer
      ↓
Normalized Expression
      ↓
SafeEvaluator
      ↓
AST Evaluation
      ↓
Formatted Result

```

### Normalization Flow

```text
Natural-Language Expression
      ↓
Lowercase
      ↓
Phrase Replacement
      ↓
Operator Replacement
      ↓
Remove Calculation Prefixes
      ↓
Normalized Expression
```
### Evaluation Flow
```text
Normalized Expression
      ↓
ast.parse(..., mode="eval")
      ↓
AST Node
      ↓
Supported Operator / Function
      ↓
Recursive Evaluation
      ↓
Numeric Result
```

:contentReference[oaicite:11]{index=11} :contentReference[oaicite:12]{index=12}

---

## Load Document Tool Data Flow

```text
Action
  ↓
LoadDocTool
  ↓
LoadDocArgs
  ↓
file_path
  ↓
RAG Component
  ↓
load_file(file_path)
  ↓
Loaded Document
```

### Runtime Execution

```text
Executor
  ↓
LoadDocTool
  ↓
self.rag.load_file(file_path)
  ↓
Result
```

## Web Retriever Data Flow

```text
User Query
    ↓
WebRetrieverTool
    ↓
Clean Query
    ↓
QueryEngine
    ↓
Expanded Queries
    ↓
┌──────────────────────────────┐
│ Wikipedia                    │
│ DDGS Web Search              │
└──────────────────────────────┘
    ↓
URLs / Summaries
    ↓
WebFetcher
    ↓
HTML
    ↓
TextExtractor
    ↓
Extracted Text
    ↓
Minimum Text Validation
    ↓
Deduplication
    ↓
Reranker
    ↓
Top-K Sources
    ↓
Context Merge
    ↓
Bounded Web Context
```

### Source Retrieval

```text
Query
  ↓
Wikipedia Summary
  +
DDGS Search
  ↓
Candidate Sources
```

### Web Page Processing

```text
URL
  ↓
WebFetcher.fetch()
  ↓
HTML
  ↓
TextExtractor.extract()
  ↓
Text
  ↓
Word Count Validation
  ↓
Truncated Source Text
```

### Final Ranking

```text
Retrieved Sources
  ↓
Extract Text Fields
  ↓
Reranker.rerank()
  ↓
Map Ranked Text Back To Sources
  ↓
FINAL_TOP_K
```
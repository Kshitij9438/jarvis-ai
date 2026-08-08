## Observation — tools/basic_tools.py

### FACT

`basic_tools.py` contains two concrete `BaseTool` implementations:

- `OpenWebsiteTool`
- `EchoTool`

### FACT

Both tools define Pydantic argument schemas independently of their execution methods.

### FACT

`OpenWebsiteTool` declares `produces_context = ["web"]`.

### FACT

`EchoTool` declares no produced context.

### FACT

The tools expose semantic metadata through `intents` and `entities`.

### FACT

Execution priority is encoded directly on the tool:

- `OpenWebsiteTool`: `1`
- `EchoTool`: `10`

### OBSERVATION

`basic_tools.py` provides simple concrete implementations of the `BaseTool` contract and can serve as a reference point for comparing the more complex tool implementations.

### STATUS

Documented. No architectural finding assigned yet.

## Observation — tools/calculator_tool.py

### FACT

`calculator_tool.py` contains three functional components around the
calculator capability:

- `ExpressionNormalizer`
- `SafeEvaluator`
- `CalculatorTool`

### FACT

`CalculatorTool` delegates natural-language normalization to
`ExpressionNormalizer`.

### FACT

`CalculatorTool` delegates expression evaluation to `SafeEvaluator`.

### FACT

`SafeEvaluator` uses Python AST parsing rather than direct unrestricted
expression evaluation.

### FACT

The evaluator exposes an explicit allowlist of mathematical operators.

### FACT

The evaluator exposes an explicit allowlist of mathematical functions.

### FACT

`CalculatorTool` declares:

- `requires_context = []`
- `produces_context = ["calculation"]`
- `priority = 1`

### FACT

Calculator execution catches exceptions and converts them into a formatted
calculation-error string.

### OBSERVATION

The calculator implementation separates normalization, expression evaluation,
and tool-level orchestration into distinct components.

### STATUS

Documented. No architectural finding assigned yet.

## Observation — tools/load_doc_tool.py

### FACT

`load_doc_tool.py` contains:

- `LoadDocArgs`
- `LoadDocTool`

### FACT

`LoadDocArgs` accepts a single `file_path: str` field.

### FACT

`LoadDocTool` delegates file loading to an injected `rag` object through
`self.rag.load_file(file_path)`.

### FACT

`LoadDocTool` declares:

- `requires_context = []`
- `produces_context = ["document"]`
- `priority = 1`

### FACT

The tool advertises document-related semantic matching metadata through
`intents` and `entities`.

### FACT

The tool supports the following declared file-related entities:

- `file`
- `document`
- `pdf`
- `txt`
- `md`
- `path`

### OBSERVATION

`LoadDocTool` acts as an adapter between the generic `BaseTool` execution
interface and the injected RAG component's document-loading capability.

### STATUS

Documented. No architectural finding assigned yet.

## Observation — tools/web_retriever_tool.py

### FACT

`web_retriever_tool.py` contains:

- `WebRetrieverArgs`
- `QueryEngine`
- `WebRetrieverTool`

### FACT

`QueryEngine` uses the injected LLM to generate expanded search queries.

### FACT

Generated queries are filtered using an anchor derived from the original
query.

### FACT

`WebRetrieverTool` retrieves from both Wikipedia and DDGS web search.

### FACT

Web search results are filtered by blocked domains:

- `youtube.com`
- `facebook.com`
- `instagram.com`
- `twitter.com`
- `tiktok.com`
- `pinterest.com`

### FACT

Search results are limited to `MAX_URLS = 5` unique domains.

### FACT

Extracted text must contain at least 40 words to be considered valid.

### FACT

Each source is truncated to `PER_SOURCE_CHARS = 1200`.

### FACT

Sources are deduplicated using domain and the first 150 characters of text.

### FACT

Sources are reranked using `Reranker`.

### FACT

The final result is limited to `FINAL_TOP_K = 4` sources.

### FACT

The merged result is bounded by `TOTAL_CHARS = 4000`.

### FACT

The final merge step is explicitly marked as having no generation.

### FACT

`WebRetrieverTool` declares:

- `requires_context = []`
- `produces_context = ["web"]`
- `priority = 3`

### OBSERVATION

`WebRetrieverTool` combines query expansion, search, retrieval, extraction,
deduplication, reranking, and context assembly within one concrete tool.

### STATUS

Documented. No architectural finding assigned yet.
# JARVIS Intent Resolution — Implementation TODO

## Objective

Implement a root-level `intent_resolution/` package that determines the user's intended action for each parsed request segment.

The design will use a **hybrid cascade architecture**, introduced incrementally:

1. Deterministic rule-based matching as the first and initial active method.
2. An embedding-based fallback, enabled only after evaluation demonstrates that deterministic matching is insufficient.
3. An optional LLM-based fallback, introduced only if the earlier methods fail to meet measured requirements.

Every stage must support abstention. No stage may force an uncertain request into an executable intent merely because it must return something.

The resolver will not select tools, extract every argument, determine whether a request is complete, resolve pronouns, or authorize execution. These remain separate responsibilities.

## Design principles

- [ ] **Closed vocabulary:** only explicitly supported intent values may be resolved.
- [ ] **One segment at a time:** each `RequestSegment` receives its own resolution result.
- [ ] **Deterministic first:** straightforward, well-supported requests should not require an ML model or LLM call.
- [ ] **Abstention is valid:** ambiguity and lack of a match are explicit outcomes.
- [ ] **No tool selection inside intent resolution:** an intent describes what the user wants, not which tool must execute it.
- [ ] **No premature learning system:** embedding and LLM fallbacks remain optional and disabled until evaluated.
- [ ] **No destructive normalization:** the resolver may normalize a matching representation, but must preserve the original request and must not rewrite `CanonicalQuery`.
- [ ] **Tests before integration:** define behavior in tests before changing production code.
- [ ] **One architectural owner per concern:** intent, completeness, reference resolution, capability selection, and execution decisions remain separate.

## 0. Establish the baseline

**Goal:** verify the current repository state before starting implementation.

Starting point (verify before beginning):

- Branch: `gui-integration`
- Latest known commit: `6c5e56f`
- Last full-suite result: 410 tests passed

- [ ] Verify the working tree is clean.
- [ ] Verify the current branch and latest commit.
- [ ] Re-run relevant focused tests.
- [ ] Run the full test suite and record the current baseline.
- [ ] Inspect `request_parsing/` and identify the actual parser test filenames.
- [ ] Inspect `RequestUnderstanding` and `RequestUnderstandingAdapter`.
- [ ] Inspect `CapabilitySelector`, `PlannerDecision`, and `DecisionType`.
- [ ] Inspect `ReferenceResolver`, `ControlLayer`, `TaskBuilder`, `PlanBuilder`, `ToolSelector`, and `PlanValidator`.
- [ ] Confirm where the current runtime computes `PlannerDecision` relative to request understanding.
- [ ] Record any relevant differences between the current code and the prior audit before changing code.

Suggested focused test command (adjust paths to actual test filenames):

```bash
PYTHONPATH=. uv run pytest -q \
  tests/test_request_understanding_canonical_query.py \
  tests/test_task_builder.py \
  tests/test_plan_optimizer.py \
  tests/test_optimizer.py
```

**Exit criteria:** the working tree is clean, existing interfaces are understood, and a baseline test result is recorded.

## 1. Finalize the intent and result contracts

Before implementing production logic, settle the taxonomy and its semantics.

### Initial candidate taxonomy

- [ ] `NAVIGATE`
- [ ] `CALCULATE`
- [ ] `EXPLAIN`
- [ ] `LOAD_DOCUMENT`
- [ ] `DOCUMENT_QUERY`
- [ ] `CONVERSATIONAL`
- [ ] `UNKNOWN`

This is the candidate taxonomy to review and lock, not an assertion that every value already exists in code.

### Separate user intent from information source

A user's action is not the same as the source of information. For example, “summarize it” describes an operation, while “it” may refer to a local PDF, web article, or user-provided text.

- [ ] Keep `LOAD_DOCUMENT` distinct because it ingests a file and changes available document state.
- [ ] Define document operations explicitly, such as `QUESTION`, `SUMMARIZE`, `FIND`, and `ANALYZE`, if supported by the agreed contract.
- [ ] Represent the requested operation and source constraint separately where needed.
- [ ] Treat `UNKNOWN` as a fallback sentinel, not a supported user goal.
- [ ] Ensure the resolver does not resolve pronouns or choose a document; those remain reference-resolution responsibilities.
- [ ] Finalize and document the finite intent vocabulary before coding the resolver.

### Resolution outcomes

Define three outcomes with distinct semantics:

- `RESOLVED`: one supported intent has been identified.
- `AMBIGUOUS`: multiple plausible intents remain and cannot be distinguished reliably.
- `NO_MATCH`: no supported intent has sufficient evidence.

- [ ] Define an explicit `ResolutionStatus` for these outcomes.
- [ ] Ensure a resolved result contains a known supported intent.
- [ ] Ensure an ambiguous result contains its competing candidates.
- [ ] Ensure a no-match result does not invent a resolved intent.
- [ ] Keep “recognized but incomplete” separate from “unknown intent.” For example, `calculate` can resolve to `CALCULATE` even though its expression is missing.

### Public result contract

- [ ] Define an immutable `IntentResolution` model.
- [ ] Include resolution status.
- [ ] Include the resolved intent or explicit unknown sentinel, as defined by the finalized model.
- [ ] Include competing candidates where ambiguous.
- [ ] Include the method/stage that produced the result.
- [ ] Include a stable rule identifier and matching evidence for deterministic results.
- [ ] Include document-operation metadata only where the finalized contract permits it.
- [ ] Do not add an arbitrary confidence float to deterministic results; represent deterministic evidence and outcomes directly.

**Exit criteria:** the intent values and outcomes have precise semantics and can be tested without importing the planner or runtime.

## 2. Create the root-level package and test files

Create `intent_resolution/` at repository root, parallel to `request_parsing/`—not under `planner/`.

Target initial structure:

```text
jarvis-ai/
├── request_parsing/
│   └── ...
├── intent_resolution/
│   ├── __init__.py
│   ├── models.py
│   ├── protocols.py
│   ├── rules.py
│   └── resolver.py
├── planner/
├── control/
├── conversation/
├── tests/
└── ...
```

- [ ] Create `intent_resolution/` at the repository root.
- [ ] Create `models.py` for the public enums and immutable result/candidate types.
- [ ] Create `protocols.py` for a small stage interface so fallback stages can be added without changing the public API.
- [ ] Create `rules.py` for deterministic rules, specificity, evidence, and conflict detection.
- [ ] Create `resolver.py` for the public `IntentResolver` facade and cascade orchestration.
- [ ] Create `__init__.py` and export only the intended public types and resolver.
- [ ] Do not create embedding or LLM fallback modules yet.
- [ ] Keep the package independent from `Planner`, `ToolSelector`, `Executor`, and live tool implementations.

Create tests using the repository's established naming conventions; suggested starting filenames:

- [ ] `tests/test_intent_resolution_models.py`
- [ ] `tests/test_intent_resolution_rules.py`
- [ ] `tests/test_intent_resolver.py`

**Exit criteria:** the package boundary and public API are clear before integration.

## 3. Write contract tests first

Add tests before implementing production matching logic.

### Supported request examples

- [ ] `open GitHub` resolves to `NAVIGATE`.
- [ ] `calculate 5 + 6` resolves to `CALCULATE`.
- [ ] `explain transformers` resolves to `EXPLAIN`.
- [ ] `load /home/user/paper.pdf` resolves to `LOAD_DOCUMENT`.
- [ ] `summarize this PDF` resolves to the agreed document intent/operation, without assuming an unresolved source is already known.
- [ ] `hi` resolves to `CONVERSATIONAL`.

### Negative and confusing examples

- [ ] `explain open source licensing` must not be classified as navigation merely because it contains “open.”
- [ ] `electric current` must not trigger current-information retrieval merely because it contains “current.”
- [ ] `2 + 3` must not be treated as a greeting because it is short.
- [ ] A request with no matching supported pattern produces `NO_MATCH`.
- [ ] Two equally plausible competing matches produce `AMBIGUOUS`.
- [ ] `calculate` remains a recognized calculation intent even though it lacks an expression.
- [ ] A recognized intent with missing required information is not treated as an unknown intent.

- [ ] Use parametrized tests for related examples.
- [ ] Test intended behavior rather than mirroring specific regex implementations.
- [ ] Include both positive examples and negative/near-miss examples for every intent.

**Exit criteria:** tests define success, ambiguity, no-match, and incomplete-request behavior before matching logic is implemented.

## 4. Implement the data models

Implement `intent_resolution/models.py`.

Candidate public types:

- [ ] `Intent`
- [ ] `ResolutionStatus`
- [ ] `IntentResolution`
- [ ] `IntentCandidate`
- [ ] `DocumentOperation`, if required by the finalized taxonomy
- [ ] A small resolution-method enum (for example, deterministic rules, embeddings, or LLM), where useful

Implementation requirements:

- [ ] Use immutable dataclasses and string-valued enums, consistent with existing request-parsing models.
- [ ] Validate that resolved results contain a supported known intent.
- [ ] Validate that ambiguous results contain competing candidates.
- [ ] Validate that no-match results do not invent a resolved intent.
- [ ] Validate document-operation metadata against the agreed contract.
- [ ] Keep models independent of runtime objects.
- [ ] Add unit tests for valid and invalid model combinations.

**Exit criteria:** model tests pass and the public contracts can be imported from the root-level package.

## 5. Implement deterministic matching

Implement the first active stage in `intent_resolution/rules.py`.

### 5.1 Define explicit matching rules

Possible stable rule identifiers include:

- [ ] `navigate.explicit_action`
- [ ] `calculate.explicit_instruction`
- [ ] `calculate.parseable_expression`
- [ ] `document.load_explicit`
- [ ] `document.query_explicit`
- [ ] `explain.explicit_request`
- [ ] `conversation.exact_greeting`

Finalize the identifiers and rule semantics in code. Each rule must have one clearly defined purpose.

### 5.2 Match structure, not arbitrary substrings

- [ ] Use token boundaries and scoped action phrases.
- [ ] Use URL/domain patterns and known destination entities for navigation evidence.
- [ ] Reuse an appropriate mathematical parser to recognize supported expressions where practical.
- [ ] Recognize document-loading actions separately from document-question operations.
- [ ] Support incomplete but recognizable commands so completeness checking can handle missing slots.
- [ ] Do not let a single incidental keyword trigger an intent unless it is a deliberately supported standalone command.
- [ ] Keep the existing parser responsible for splitting compound requests.

Examples to preserve:

- `open GitHub` is a navigation request.
- `explain open source licensing` is an explanation request.
- `2+3` may be a calculation even without the word “calculate.”
- `load this PDF` is a load intent even when the path is missing.

### 5.3 Define specificity and conflict handling

- [ ] Prefer a more specific valid rule over a broad generic rule.
- [ ] Do not let broad keyword matches override specific actions.
- [ ] Return `AMBIGUOUS` when equally specific candidates conflict and evidence cannot distinguish them.
- [ ] Return `NO_MATCH` when no rule has sufficient evidence.
- [ ] Do not use first-match-wins as an implicit replacement for a precedence policy.
- [ ] Add tests for overlapping rules and precedence.

### 5.4 Preserve the original request

- [ ] Limit normalization to the matching representation.
- [ ] Do not mutate `RequestSegment.text`.
- [ ] Do not overwrite the original request.
- [ ] Do not replace expanded topic names with abbreviations.
- [ ] Do not duplicate or alter `CanonicalQuery` transformations.
- [ ] Return match evidence rather than rewriting the request into a tool command.

**Exit criteria:** deterministic rules pass positive, negative, ambiguous, and unknown-intent tests.

## 6. Add the cascade orchestrator

Implement `IntentResolver` in `intent_resolution/resolver.py`, using the stage interface defined in `protocols.py`.

- [ ] Expose a public API that accepts one `RequestSegment` and returns one `IntentResolution`.
- [ ] Keep request splitting in `RequestParser`; do not split compound requests inside the resolver.
- [ ] Implement the initial cascade with deterministic rules as the only active stage.
- [ ] Ensure a decisive deterministic match short-circuits later stages.
- [ ] Define how unresolved outcomes may proceed to later enabled stages.
- [ ] Preserve ambiguity or no-match if all enabled stages abstain.
- [ ] Ensure a stage failure never silently creates an intent.
- [ ] Do not compare raw embedding similarity and LLM-reported confidence as if they were calibrated, directly comparable probabilities.
- [ ] Keep embeddings and LLM calls disabled in the initial configuration.

Use fake stages to test orchestration without loading a model or making network calls:

- [ ] A successful first-stage match short-circuits later stages.
- [ ] A no-match result permits a later stage to try when one is enabled.
- [ ] Unresolved ambiguity is preserved if no fallback resolves it.
- [ ] A stage failure does not silently produce an intent.
- [ ] The default configuration invokes only deterministic rules.

**Exit criteria:** the cascade works as a small, testable facade, with no model dependency in version one.

## 7. Integrate with `RequestUnderstandingAdapter`

Wire the independently tested package into the existing request-understanding path.

- [ ] Resolve each parsed `RequestSegment` independently.
- [ ] Populate `RequestUnderstanding.intent` or the finalized structured resolution field.
- [ ] Preserve original segment text and offsets.
- [ ] Preserve entity-extraction behavior.
- [ ] Preserve canonical-query behavior.
- [ ] Preserve the association between each segment and its resolution result.
- [ ] Inject `IntentResolver` into the adapter where practical so tests can substitute a fake implementation.
- [ ] Do not make the adapter run tool selection or execution after identifying an intent.

Adapter tests:

- [ ] A single request receives one intent resolution.
- [ ] A compound request receives one result per parsed segment.
- [ ] Segment ordering and original text remain unchanged.
- [ ] An unknown segment does not inherit a neighboring segment's intent.
- [ ] Existing entity extraction and canonical-query tests remain green.

**Exit criteria:** request understanding produces intent information without changing downstream runtime decisions yet.

## 8. Keep completeness checking separate

Implement or wire `CompletenessChecker` as the next independent M7 step after intent resolution is stable.

Initial required-information expectations:

- [ ] `NAVIGATE`: a valid destination is available.
- [ ] `CALCULATE`: a parseable expression is available.
- [ ] `LOAD_DOCUMENT`: a valid, supported file source is available.
- [ ] `DOCUMENT_QUERY`: a resolvable document or source is available.
- [ ] `EXPLAIN`: a sufficiently specified topic is available.
- [ ] `CONVERSATIONAL`: no tool arguments are required.

Local-document validation:

- [ ] Check that a file path or other supported source is present.
- [ ] Check that the extension is supported.
- [ ] Check that the path/source is accessible where the runtime can validate it safely.
- [ ] Check that the document source can be resolved.
- [ ] Check that a document query has usable document context.
- [ ] Keep vector-store inspection and document retrieval out of `IntentResolver`.
- [ ] Clarify incomplete recognized requests instead of selecting a different intent.

**Exit criteria:** a recognized but incomplete request remains a recognized intent and cannot proceed to execution until its completeness requirements are satisfied.

## 9. Integrate decisions before planning

Only after the above contracts are stable, correct the runtime ordering so request understanding produces the decision before planning begins.

Target sequence:

```text
RequestParser
      |
      v
IntentResolver
      |
      v
CompletenessChecker
      |
      v
ReferenceResolver
      |
      v
PlannerDecision
      |
      +-- EXECUTE ----> planning
      +-- CLARIFY ---> response, then stop
      +-- RESPOND ---> conversational response
      +-- REJECT ----> rejection response
```

- [ ] Verify the current runtime decision ordering before editing it.
- [ ] Move/rework decision calculation only after resolver and completeness contracts are tested.
- [ ] Preserve the frozen M7 component ownership boundaries.
- [ ] Ensure `CONVERSATIONAL` does not select a tool.
- [ ] Ensure `UNKNOWN` and `AMBIGUOUS` cannot silently fall back to `ExplainTool`.
- [ ] Ensure incomplete requests do not enter planning.
- [ ] Ensure `CLARIFY` is terminal for the current execution attempt.
- [ ] Ensure resolved intent still passes capability selection, plan validation, and control checks before execution.
- [ ] Add integration tests that assert both the returned decision and the number of tool executions.
- [ ] Test that a clarification response alongside tool execution is treated as a failure.

**Exit criteria:** request understanding gates planning, and unresolved intent cannot reach tool execution.

## 10. Evaluate the deterministic baseline

Build a labeled evaluation set before introducing ML or LLM fallbacks.

- [ ] Include varied phrasings for every supported intent.
- [ ] Include short commands and compound requests.
- [ ] Include near-miss examples.
- [ ] Include incomplete but recognizable requests.
- [ ] Include genuinely unsupported requests.
- [ ] Include ambiguous examples.
- [ ] Include document-loading and document-query examples.
- [ ] Include representative follow-up phrases.
- [ ] Start with approximately 20–30 positive examples per intent and at least 50 negative, near-miss, or out-of-scope examples; expand based on discovered failure modes.
- [ ] Keep held-out examples separate from examples used to create rules.
- [ ] Record per-intent precision and recall.
- [ ] Record macro-F1 and the confusion matrix.
- [ ] Record unknown/no-match detection performance.
- [ ] Record ambiguity detection performance.
- [ ] Record false matches that would have led toward execution.
- [ ] Record latency and dependency cost.

**Exit criteria:** the deterministic baseline has reproducible measurements and documented weaknesses. Do not add ML just because it is available.

## 11. Add embedding fallback only if warranted

This is an optional extension. Implement it only if the deterministic baseline struggles with paraphrases or other recurring, measured cases.

- [ ] Create an embedding stage using curated labeled examples for supported intents.
- [ ] Do not use arbitrary tool descriptions as the intent dataset.
- [ ] Return candidate intents and evidence from the stage.
- [ ] Calibrate similarity thresholds and top-candidate margins on validation data.
- [ ] Abstain when similarity is insufficient or candidates are too close.
- [ ] Evaluate against deterministic rules on held-out examples.
- [ ] Measure whether it improves classification without increasing dangerous false matches or weakening unknown detection.
- [ ] Keep the embedding fallback optional and independently testable.
- [ ] Do not reuse tool-selection similarity as intent confidence without separate validation.
- [ ] Keep the fallback disabled if it does not provide a measurable improvement.

**Exit criteria:** the embedding stage demonstrates measurable benefit without regressing execution safety.

## 12. Consider an LLM fallback only after evaluation

The LLM stage is the last optional fallback, not the primary classifier.

- [ ] Consider this stage only if deterministic and embedding stages leave recurring important cases unresolved.
- [ ] Provide the model with the finite, approved intent vocabulary.
- [ ] Constrain output to a validated structured schema.
- [ ] Require an explicit abstention option.
- [ ] Treat the user request as untrusted classification input, not as instructions that can alter the taxonomy.
- [ ] Validate every returned value.
- [ ] Implement timeout and failure handling.
- [ ] Prevent the LLM from selecting or executing tools.
- [ ] Do not treat the model's self-reported confidence as calibrated confidence.
- [ ] Do not allow the LLM to override a high-precision deterministic match.
- [ ] Measure latency, cost, classification quality, and failure modes against the same evaluation set.
- [ ] Do not ship the fallback unless evidence justifies its operational cost and failure surface.

**Exit criteria:** evidence demonstrates that the LLM fallback adds enough value to justify its complexity and operational cost.

## 13. Final regression and release

Run focused suites throughout implementation; adjust test paths to match the actual repository layout.

```bash
PYTHONPATH=. uv run pytest -q \
  tests/test_intent_resolution_models.py \
  tests/test_intent_resolution_rules.py \
  tests/test_intent_resolver.py
```

- [ ] Run focused intent-resolution tests after each logical change.
- [ ] Run request-understanding and planner integration tests after wiring.
- [ ] Run `git diff --check` before committing.
- [ ] Review `git status --short`, `git diff --stat`, and the complete diff.
- [ ] Run the full test suite before completing the integration milestone.

```bash
PYTHONPATH=. uv run pytest -q
```

- [ ] Compare the result against the actual baseline established at Step 0; 410 passing tests is the last known baseline, not a guaranteed fixed count.
- [ ] Keep each commit logically scoped and ensure tests for a behavior change are in the same commit.
- [ ] Commit on `gui-integration` and push completed changes.
- [ ] Leave the frozen `docs/PLAN.md` unchanged; record new architectural decisions through the repository's ADR process where appropriate.

## 14. Recommended commit sequence

- [ ] Commit 1: define intent-resolution contracts and tests.
- [ ] Commit 2: add the deterministic root-level `intent_resolution/` package.
- [ ] Commit 3: populate request-understanding records with resolver results.
- [ ] Commit 4: implement completeness checking and tests as a separate change.
- [ ] Commit 5: reorder runtime decision flow so planning begins only after understanding.
- [ ] Commit 6: add integration tests proving unresolved requests cannot execute.
- [ ] Commit 7: add the evaluation corpus and baseline metrics.
- [ ] Commit 8: add embedding fallback only if baseline results justify it.
- [ ] Commit 9: add LLM fallback only if a measured gap remains after embedding evaluation.

Do not create empty fallback modules or implement optional stages merely to make the architecture appear sophisticated.

## Definition of done — First release

- [ ] `intent_resolution/` is a standalone package at the repository root, parallel to `request_parsing/`.
- [ ] Every parsed segment receives a resolution result.
- [ ] The intent vocabulary is finite and documented in code.
- [ ] Deterministic matching handles supported intents and known near-misses.
- [ ] Ambiguous and unmatched requests are explicit outcomes.
- [ ] An incomplete intent cannot proceed to execution.
- [ ] Request understanding populates the intent/resolution field.
- [ ] Planning is gated by the resulting `PlannerDecision`.
- [ ] No embedding model or LLM is required by the default path.
- [ ] The existing regression suite remains green.
- [ ] The implementation has a reproducible baseline against which future cascade stages can be evaluated.

## Core architectural boundary

**`IntentResolver` answers: “What kind of action is the user requesting?”**

It does not answer:

- Which file does “it” refer to?
- Is the request complete?
- Which capability should be selected?
- Which tool should run?
- Is execution authorized?

Those remain separate responsibilities in M7.

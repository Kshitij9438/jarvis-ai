---

# 11. Plan progress

**Audited:** 2026-10-19 against the `jarvis-ai-gui-integration` snapshot
**Method:** every claim below was checked in code, by running the test suite, or by driving the real runtime. Nothing is inferred from README or docs.
**Current position:** M6 complete, M7 partial, M8 onward not started.

This section is a status log. It adds no architecture. Items under 11.3 are
corrections of fact discovered during implementation, which Section 10 allows.

> **Verification caveat.** `ollama` and `sentence_transformers` were stubbed
> outside the repo (no GPU, models or network in the audit environment).
> All **400 tests pass** with those stubs (baseline was 84). Findings that
> depend on real model behavior are marked *(model-dependent)*. The snapshot
> has no `.git`, so M0's clean-branch check and "each fix is its own commit"
> are unverifiable.

## 11.1 Milestone status

| Milestone | Status | Evidence |
|---|---|---|
| M0 Baseline | Unverifiable | No git history. Suite is green (400 tests). |
| M1 Isolated defects | Partial | D2, D3 done. D1 root cause persists downstream (F5). |
| M2 Conversation state | Done in-process | `ConversationContext` has all 7 planned fields. `ConversationManager` owns lifecycle. `ExecutionContext` untouched. Persistence works across `runtime.run()` calls; not reachable over HTTP (F2). |
| M3 Decision contract | Done, minimal | `DecisionType` has 4 variants. `PlannerDecision` carries only `type`. `"hi"` is covered by a `RESPOND` test. Planner greeting special case still exists (F6). |
| M4 Clarification | Mostly done | `explain something` returns `CLARIFY` with no plan and zero tool executions. Covers 4 regex patterns only. LLM-dependent (F3). |
| M5 Reference resolution | Mostly done | `its` resolves to `transformers`. Two candidates clarify. Deterministic, no LLM. Detection is crude (F4). |
| M6 Intent → capability | Done | `retrieval_signals.py` + `retrieval_decision.py` replace the keyword list. `explain`/`describe`/`walk me through` give identical retrieval decisions. Golden tests in `test_m6_retrieval_golden.py`. |
| M7 Planner migration | Partial | See 11.2. |
| M8 Context architecture | Not started | No `ContextManager`. Legacy `requires` still read by `PlanBuilder`. |
| M9 Execution contracts | Not started | No failure classification anywhere in `control/`, `executor/` or `execution/`. |
| M10 API contract | Not started | `ChatResponse` unchanged. No `conversation_id` in the request. `/api/chat` returns HTTP 500 on clarification (F2). |
| M11 Event streaming | Not started | `run_with_events()` still collects then returns. Event names do not match the plan's list. |
| M12 GUI state migration | Not started | Single `App.tsx` (522 lines) plus `api.ts` and `types.ts`. No `components/hooks/state` split. |
| M13 Response rendering | Not started | No Markdown, code, LaTeX or sources cards. |
| M14 Developer Inspector | Pre-existing only | Inspector shows events and plan. No three-layer hierarchy. |
| M15 Visual polish | Not started | No live thinking indicator. |
| M16 Suite hardening | Seeded | Golden-style tests exist in `test_clarification`, `test_decision_layer`, `test_reference_resolver`, `test_m6_retrieval_golden`. No consolidated suite. |
| M17 E2E scenarios | Not started | No concurrency or HTTP-level tests. |
| M18 Documentation | Not started | 29 of 49 `.md` files are empty, including all 4 ADRs. `DependencyResolver` is still referenced in 8 places. |

## 11.2 M7 component status

| Planned component | State |
|---|---|
| RequestParser | **Unwired.** `request_parsing/` (10 modules, 151 tests) is imported by nothing in the runtime. The adapter and `PlanBuilder` both still use `re.split(r"\band\b\|\bthen\b\|,")`. |
| IntentResolver | Missing. `RequestUnderstanding.intent` is never populated. |
| CompletenessChecker | Missing. The decision is a regex that runs *before* understanding and is passed *into* the adapter, which inverts Section 4's ordering. |
| ReferenceResolver | Done, and correctly upstream of planning (runs in `runtime.py`). |
| CanonicalQuery | Done and consumed by `TaskBuilder` for `explain` and `web_retriever`. A5 only partly resolved: `TaskBuilder._clean_query` and `ControlLayer` still re-transform queries. |
| CapabilitySelector | Done, substring-based (F7). |
| PlanBuilder / PlanOptimizer / PlanValidator | Done. `TaskOptimizer` remains as a facade. |
| Pipeline split | `Planner.plan()` still runs optimizer, validator, intelligence, control layer, context resolver and scorer in one method. |

**Exit-criteria gap:** `test_plan_scorer.py`, `test_plan_variants.py`,
`test_planner_intelligence.py` (and `test_arg_extractor.py`) are 0-byte files.
M7's "all planner tests pass" is vacuous for them.

## 11.3 Defects found (verified by reproduction)

**F1. Bogus `open_website` step on every `explain`.**
`explain.requires_context = ["web"]`, and both `open_website` and `web_retriever`
declare `produces_context = ["web"]`. `ContextDependencyResolver._find_producer`
returns the first registered producer (`open_website`), injected with a `query`
arg and no `url`. It fails schema validation on every explain request.
Warning: switching the producer to `web_retriever` would make every explain hit
the web and undo M6. Resolve the `requires_context` declaration first (M8).

**F2. Clarification does not work end to end over HTTP.**
- `/api/chat` returns HTTP 500 on any clarification (`ClarificationRequest` is not a dict).
- `api/server.py` calls `runtime.run(request.message)` with no `conversation_id`, so `"transformers"` after `explain something` starts a new conversation.
- The GUI filters on `item.success`, so the clarification question is never shown. The D2 button now displays "Execution completed."

**F3. Clarification depends on the LLM with no fallback.**
`clarify_question()` returns `None` when the LLM fails, and `runtime.py:224` and
`:299` dereference `.question`. Resumption also requires an LLM-derived
`pending_request.intent`, so an LLM failure silently disables it.

**F4. Pending-clarification and reference handling.**
- After `explain something`, any next message is folded in: `calculate 5 + 6` becomes `explain calculate 5 + 6`.
- An answer to an ambiguity clarification is not resumed, so the original intent is lost.
- `that`/`this` are replaced as pronouns: `so that i can learn` became `so bert i can learn`.
- `it?` is not detected (whitespace split without punctuation stripping).

**F5. D1 root cause fixed in one of three places.**
`PlanOptimizer` has the `{ai, ml, dl}` allow-list. `ControlLayer._is_meaningful_query`
still rejects queries under 3 characters and `PlanValidator` requires `> 3`.
The canonical `ai` is dropped there; the runtime survives only through a
fallback to the raw goal. The allow-list is also hard-coded separately from
`CanonicalQuery`'s synonym map.

**F6. Planner greeting special case survives M3.**
`Planner._is_trivial_input` treats any input of 3 characters or fewer as a
greeting: `2+3`, `AI` and `git` all return "Hey! How can I help you?".
`"hi"` takes the `RESPOND` path but returns an empty results list (no reply text).

**F7. Segmentation and capability matching are lexical.**
- `compare transformers and neural networks` is split on "and" into two explains.
- `CapabilitySelector` matches substrings: `explain open source licensing` routes to navigation, `state-of-the-art` routes to calculation.
- `requires_current_information` matches `current` in `electric current`.

**F8. Test-coverage gaps.**
- `test_planner_retrieval.py` tests `Planner._should_use_retriever`, but the live code uses the identical copy in `PlanBuilder`.
- No test covers concurrent requests (D3 is unguarded) or any HTTP endpoint.

## 11.4 Section 6 golden scenarios

| Scenario | Backend result | Notes |
|---|---|---|
| `explain something` | Clarify, zero tools | Not visible in GUI (F2) |
| `transformers` as answer | Resolves to explain transformers | Works only in-process |
| `explain transformers` | Execute | Includes bogus step (F1) |
| `…` then `what are its applications?` | `its` resolved to transformers | Pass |
| `compare…` then `its applications?` | Clarify | Pass; turn 1 split on "and" (F7) |
| `open github` | Execute | Pass |
| `calculate 5 + 6` | Execute | Pass |
| `open github then explain git` | Execute, order preserved | Pass |
| `hi` | Respond, no tools | No reply text (F6) |

## 11.5 Suggested order for the next steps

1. F1, F3, F5: small, backend-only, each touches live behavior.
2. Decide the fate of `request_parsing/`: wire it into the adapter, or retire it.
3. Add `IntentResolver` and `CompletenessChecker` so understanding produces the decision (completes M7).
4. Fill the empty M7 test files, and test the live `PlanBuilder` retrieval path instead of the `Planner` copy.
5. M8 onward as written. F2 is resolved by M10.
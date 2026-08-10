# JARVIS — Reasoning Architecture & GUI Migration Plan

**Version:** 1.0 — frozen
**Status:** Approved for execution. No further architecture is to be added to
this document; implementation notes belong in commit messages and ADRs, not
here.
**Baseline:** `gui-integration` branch, 84 passing tests
**Governing rule:** *No architectural component gets replaced until we can state
its replacement's input contract, output contract, owner, and tests.*

**Prime invariant** — the one sentence this entire migration exists to make
true:

> JARVIS must never execute merely because a tool can technically be selected.
> It executes only after the request has been understood sufficiently to
> justify execution.

Everything below — the decision contract, clarification, reference
resolution, context ownership — is the architecture that makes that sentence
enforceable rather than aspirational. The GUI (M12–M15) is the visual
expression of this decision system, built only once the decision system
itself is correct.

---

## 1. Why this plan exists

JARVIS currently treats every user message as an executable request:

```text
User → ToolSelector → TaskBuilder → Optimizer → Executor
```

That assumption is the root cause of its worst behavior: given `"explain
something"`, the system does not recognize that it has nothing to explain — it
selects a tool, builds a task, and executes a pipeline anyway, producing either a
meaningless answer or a hallucinated topic instead of asking what the user meant.
The same root cause produces the second failure mode: `"what are its
applications?"` has no mechanism to resolve `"its"` against anything, because
there is no persistent conversational state to resolve it against.

Every other problem in this document is either a direct symptom of that one
design gap, or an independent defect that happened to surface while investigating
it. This plan fixes the isolated defects immediately (they don't require the
redesign), then closes the design gap through a sequenced migration that keeps
the existing test suite green at every step.

---

## 2. Governing principles

1. **Understand before you execute.** A request is only planned and run once it
   is understood well enough — clarify or ask, don't guess.
2. **One owner per concern.** Plan quality is `PlanScorer`'s job. Request
   understanding confidence is a different, earlier question with a different
   owner. Context availability has exactly one source of truth. A dependency is
   expressed one way, not two.
3. **The GUI reflects state; it does not decide anything.** It consumes
   `PlannerDecision`, `ExecutionEvent`, `Response`, and `ConversationState`. It
   never re-implements reasoning that belongs in the runtime.
4. **Deterministic before LLM.** Every new decision point defaults to cheap,
   testable, rule-based logic first (matching the existing `ControlLayer`
   philosophy of "zero LLM calls, purely deterministic logic"). An LLM is
   introduced only where evidence shows deterministic logic is insufficient.
5. **Every commit leaves the test suite green.** If a contract intentionally
   changes, the tests that assert the old contract are updated in the *same*
   commit — never deleted or weakened just to make CI pass.
6. **Clarification is terminal for the current execution attempt.** When a
   `PlannerDecision` is `CLARIFY`, no planning, tool selection, task
   construction, execution, retrieval, or repair may occur for that request:

   ```text
   CLARIFY
     │
     └──→ response
          └──→ STOP
   ```

   Not:

   ```text
   CLARIFY → tool selection → retrieval → execution → "what did you mean?"
   ```

   The `"explain something"` golden scenario (Section 6) exists specifically to
   enforce this — it asserts zero tool executions, not just a clarification
   message *in addition to* execution.

---

## 3. Problem inventory

Every problem below was confirmed directly against the code in this repository,
not inferred from description.

### 3.1 Isolated defects (fix immediately, no redesign required)

| # | Problem | Where | Why it's a problem |
|---|---------|-------|---------------------|
| D1 | `TaskOptimizer` rejects queries `≤ 2` characters *after* normalizing phrases like `"artificial intelligence"` → `"ai"` | `planner/optimizer.py`, `_filter_invalid()` | The class's own normalization step creates the exact value its own validation step then throws away. `"explain AI"` silently produces no `explain` step. |
| D2 | GUI suggestion button labeled **"Explain something"** actually submits `"explain how transformers work"` | `gui/src/App.tsx:264-269` | The visible label and the hidden request mean different things. It also hides the very failure mode (`"explain something"`) this whole plan exists to fix, instead of demonstrating it. |
| D3 | `run_with_events()` mutates `self.execution_loop.event_callback` on the shared `JarvisRuntime` singleton, reset in a `finally` block | `app/runtime.py:121-158`; singleton constructed once at import in `api/server.py:23` | Under concurrent FastAPI requests, one request's events can be delivered to another request's callback, or dropped entirely, mid-flight. This is a live race condition, not a hypothetical. |

### 3.2 Architectural problems (require the migration below)

| # | Problem | Where | Why it's a problem |
|---|---------|-------|---------------------|
| A1 | No request-understanding stage before planning | `planner/planner.py: plan()` goes straight from segmentation to tool selection | There is no point at which the system asks "do I actually understand this well enough to act?" — incompleteness and ambiguity are indistinguishable from a normal request. |
| A2 | No conversational memory, only per-request execution context | `app/runtime.py: run()` creates a fresh `ExecutionContext(user_input)` every call | `ExecutionContext` tracks *this request's* tool results; nothing tracks *the conversation's* active topic across turns, so `"its"` has nothing to resolve against and a clarification question can't be followed up on. |
| A3 | No first-class clarification outcome | `Planner.plan()` always returns a `Plan` | The system is structurally unable to say "I need more information" — it can only produce a plan, good or bad. |
| A4 | Retrieval decision is a fragile keyword list | `planner/planner.py: _should_use_retriever()` — `"what is"`, `"explain"`, `"theory"`, etc. | `"explain"` appearing anywhere in the input is sufficient to force web retrieval, regardless of whether JARVIS already knows the answer or whether the query is even meaningful yet. |
| A5 | Query string is re-interpreted at every pipeline stage | raw → extracted → cleaned → normalized → sanitized → optimized, across `arg_extractor`, `task_builder`, `optimizer`, `control_layer` | No single point owns "what does this query actually mean now" — each stage's transformation is invisible to the others, making the abbreviation bug (D1) and the `"its applications"` bug both possible and hard to trace. |
| A6 | Context logic duplicated across six modules | `Planner`, `ContextDependencyResolver`, `ControlLayer`, `Executor`, `ExecutionContext`, `execution/context_signals.py` | Multiple places independently decide "is context available," with only partial sharing (`context_signals.py` helpers). A behavior fix in one place doesn't guarantee the others agree — this is the exact class of bug already found and fixed once in `ControlLayer` (duplicate context injection removed in favor of `Executor` as sole owner). |
| A7 | Two competing dependency-declaration systems on tools | `tools/rag_tool.py`: `requires = ["load_document"]` (legacy, kept intentionally) alongside `requires_context = ["document"]` (current, actually enforced) | A tool author using `requires` reasonably expects it to be enforced the way `requires_context` is. It isn't. This is unresolved technical debt, not yet a live bug. |
| A8 | `/api/chat/events` is not real streaming | `app/runtime.py: run_with_events()` executes the whole request, collects events into a list, returns them all at once | The frontend cannot show live progress ("retrieving... generating...") because the backend has no mechanism to push events until the entire request is already finished. |
| A9 | GUI exposes raw runtime internals as the primary result | Inspector currently the only place richer state is shown; message body is plain `{message.content}` with no Markdown/source separation | Debug-only state (`_buckets`, `history`, `MAX_PER_BUCKET`) and raw retrieval dumps are not a user-facing answer. There's also no rendering layer (Markdown/code/citations) at all yet. |
| A10 | Architecture docs describe a class that no longer exists under that name | `docs/01-repository-spec/{class-index,module-index,public-api,ownership-matrix,runtime-index}.md` still reference `DependencyResolver`; the actual class is `ContextDependencyResolver` | Documentation that lies about the current shape of the system is worse than no documentation — it actively misleads whoever reads it next. |

---

## 4. Target architecture

```text
                    USER MESSAGE
                         │
                         ▼
              ┌────────────────────┐
              │ Conversation State  │   ← persists across turns
              └─────────┬──────────┘
                         │
                         ▼
              ┌────────────────────┐
              │ Request Understander│   ← intent, completeness, references
              └─────────┬──────────┘
                         │
          ┌──────────────┼───────────────┐
          ▼               ▼               ▼
      COMPLETE        AMBIGUOUS      CONVERSATIONAL
          │               │               │
          ▼               ▼               ▼
        PLAN          CLARIFY       RESOLVE CONTEXT
          │               │               │
          └──────────────┼───────────────┘
                         ▼
                  EXECUTION PLAN
                         │
                         ▼
                   CONTROL LAYER
                         │
                         ▼
                      EXECUTOR
                         │
                         ▼
                       TOOLS
                         │
                         ▼
                      RESULTS
                         │
                         ▼
                 RESPONSE BUILDER
                         │
                         ▼
                        USER
```

**Layer ownership** (this is the architectural invariant this plan protects):

| Layer | Answers |
|---|---|
| Conversation State | What has this conversation established so far? |
| Request Understander | What is the user asking, and do I understand it well enough? |
| Reference Resolver | What is being referred to, and is that reference resolvable? |
| Context Manager *(A6 fix)* | What contextual information is actually **available** right now? |
| Planner | What should we do about it? |
| Control Layer | Is this plan safe and valid? |
| Executor | How do we carry it out? |
| Response Builder | How do we communicate the result? |

No layer duplicates another layer's answer. This is the rule that A6 and A7
violate today and that this plan exists to restore — and it is why **reference
resolution** (semantic: "what does 'its' mean?") and **context availability**
(mechanical: "do we have web/document context stored?") are kept as two
separate rows above, owned by two separate components, even though both were
loosely grouped under "Context" in earlier drafts of this plan:

```text
ConversationContext
        ↓
RequestUnderstanding
        ↓
ReferenceResolver     ← owns "its" → transformers
        ↓
Planner
```

`ContextManager` (M8) owns *availability* only — "is the `document` bucket
genuinely populated," "has `web_retriever` actually run successfully." It does
not decide what a pronoun refers to. That is the Reference Resolver's job
(M5), which reads from `ConversationContext`, not from `ContextManager`.

---

## 5. Milestones

Each milestone states **what** changes, **why it's needed now** (not before, not
after), and **exit criteria**. M0–M11 are backend-only; the GUI is not touched
until the backend contract it consumes is stable.

### M0 — Baseline
- [ ] Verify all 84 tests currently pass (re-run, don't assume).
- [ ] Verify a clean git state on `gui-integration` before any change.
- [ ] Record this as the baseline commit to diff every later milestone against.
- No unrelated cleanup gets mixed into this migration.

### M1 — Three isolated defect fixes
Before writing any fix, inspect the exact current implementation of each — the
plan states *what* is wrong, the repository states *how* to fix it safely.
Don't fix from memory of this document's description.

- **D1:** Replace the length-based validity check in `TaskOptimizer._filter_invalid()`
  with a semantic check (e.g., an explicit allow-list for known short-form
  queries produced by the synonym map, or a check for "was this produced by
  normalization" rather than raw length).
- **D2:** Make the "Explain something" button submit the literal string
  `"explain"` — so JARVIS is forced to demonstrate clarification, which is the
  actual behavior this whole plan is building toward.
- **D3:** Make the event sink local to each request invocation instead of a
  mutated attribute on the shared runtime singleton.
- **Exit criteria:** full 84-test suite green; each fix is its own commit.

**Checkpoint: stop and reassess after M1, before beginning M2.** This keeps
the migration a controlled, incremental process rather than letting an
18-milestone plan collapse into one continuous rewrite.

### M2 — Conversation state
- Introduce `ConversationContext`, distinct from `ExecutionContext`, holding:
  - conversation id
  - conversation history
  - active topic / entity
  - pending clarification
  - **pending request** (see below)
  - resolved references
  - last assistant response
- **Why `pending_request` specifically matters:** for the sequence
  `"explain something"` → *(clarify)* `"What would you like me to explain?"`
  → `"transformers"`, the third turn is a single, topic-less word. Without a
  stored `pending_request` (`intent = EXPLANATION`, `missing_slot = TOPIC`),
  `"transformers"` is indistinguishable from an unrelated one-word request and
  the system has lost *why* it asked the clarifying question in the first
  place. `pending_request` is what lets the answer to a clarification be
  recombined with the original, now-completed intent.
- Comes *before* clarification (M4), because clarification without state
  degrades into repeating the same question forever.
- **Exit criteria:** conversation id persists across two sequential calls to the
  runtime; `"explain something"` → `"transformers"` resolves to a completed
  `EXPLANATION(transformers)` request on the second turn, not a fresh,
  context-free interpretation of the word `"transformers"` alone;
  `ExecutionContext` is untouched (still owns per-request tool state).

### M3 — Request decision contract
- Introduce `PlannerDecision` with variants: `EXECUTE`, `CLARIFY`, `RESPOND`,
  `REJECT`. Nothing downstream consumes it yet — this milestone only establishes
  the contract and its tests.
- **`RESPOND` explicitly covers conversational input that requires no
  execution at all** — not only post-execution responses. `"hi"` →
  `RESPOND` → `"Hello! How can I help?"` → zero tools, same as the existing
  `_is_trivial_input()` greeting short-circuit does today, just now expressed
  through the decision contract instead of a special case in `Planner.plan()`.
  This must be stated explicitly here, or a later implementer could reasonably
  read `RESPOND` as "the response after execution" and reintroduce a special
  case for greetings elsewhere.
- **Exit criteria:** contract is fully specified and unit-tested in isolation
  (input: raw understanding output; output: one of the four variants); `"hi"`
  is covered by a `RESPOND` unit test, not a separate code path.

### M4 — Clarification
- Wire `CLARIFY` into the runtime: `"explain something"` → intent =
  explanation, topic = missing → clarification question, **zero tools execute**.
- This is the plan's first golden regression test (Section 6) — it goes into
  the reasoning regression suite immediately, not deferred until M16, which
  only consolidates and hardens what M4 onward has already been accumulating.
- **Exit criteria:** `"explain something"` produces a clarification response
  with no `Plan` execution; existing direct-command tests (`"open github"`,
  `"calculate 5 + 6"`) remain unaffected.

### M5 — Reference resolution
- Owned by the **Reference Resolver** (Section 4), reading from
  `ConversationContext` — not by `ContextManager` (M8), which owns
  availability, not semantics. Deterministic-first strategy, no LLM call for
  ordinary references:

  ```text
  explicit reference → recent active entity → conversation context
        → confidence check → if ambiguous: clarify
  ```

- `"explain transformers"` then `"what are its applications?"` resolves `"its"`
  → `transformers`. `"compare transformers and neural networks"` then `"what
  are its applications?"` has two candidates and clarifies instead of guessing.
- **Exit criteria:** both golden scenarios above pass; no LLM call is made for
  either.

### M6 — Intent → capability separation
- Replace `_should_use_retriever()`'s keyword list (A4) with a decision based on:
  does JARVIS already know enough / is current information required / did the
  user explicitly ask for search / is existing context sufficient.
- Intent (`EXPLAIN`) maps to a capability (`knowledge retrieval`), which maps to
  candidate tools (`web_retriever`, `explain`) — not directly to one tool.
- **Invariant, precisely stated:** `keyword presence ≠ retrieval decision`.
  This is *not* "if the word `explain` appears, never retrieve" — that would
  just be the same bug inverted. `"explain the latest transformer
  architectures"` legitimately *should* retrieve, because "latest" signals a
  need for current information, not because "explain" is present. The fix
  removes lexical presence as the deciding factor; it does not flip which
  answer a keyword implies.
- **Exit criteria:** the retrieval decision for a given input is unchanged when
  a neutral synonym is substituted for `"explain"` (e.g. `"describe"`,
  `"walk me through"`) — i.e. the decision no longer keys off that specific
  word at all.

### M7 — Planner migration
- Split the pipeline into two clearly bounded phases instead of one flat
  chain — this keeps reference resolution where Section 4 already says it
  belongs (part of *understanding* the request, not part of deciding *how to
  execute* it):

  ```text
  ┌──────────── REQUEST UNDERSTANDING ────────────┐
  │ RequestParser                                 │
  │      ↓                                        │
  │ IntentResolver                                │
  │      ↓                                        │
  │ CompletenessChecker                           │
  │      ↓                                        │
  │ ReferenceResolver                             │
  │      ↓                                        │
  │ PlannerDecision                                │
  └──────────────────────┬────────────────────────┘
                         │
                EXECUTE / CLARIFY /
                  RESPOND / REJECT
                         │
                         ▼
  ┌──────────────────── PLANNING ─────────────────┐
  │ CapabilitySelector                            │
  │      ↓                                        │
  │ PlanBuilder                                   │
  │      ↓                                        │
  │ PlanOptimizer                                 │
  │      ↓                                        │
  │ PlanValidator                                 │
  └───────────────────────────────────────────────┘
  ```

  Planning only begins once Request Understanding has already produced a
  `PlannerDecision` of `EXECUTE` — `ReferenceResolver` runs once, upstream,
  as part of understanding, not as a planning stage that could be
  re-entered or re-run mid-plan. `ContextResolver` and `ClarificationManager`
  from earlier drafts of this milestone are absorbed into
  `CompletenessChecker` / `PlannerDecision` above, since clarification is a
  *decision produced by* understanding, not a separate stage after it.
- Migrate incrementally: new component sits alongside the old one, downstream
  pipeline is repointed one stage at a time, old component is removed only after
  its replacement's tests pass.
- Also resolves **A5** (query re-interpretation): a single `CanonicalQuery`
  concept replaces raw → extracted → cleaned → normalized → sanitized →
  optimized; downstream stages consume it rather than re-transforming it.
- **Exit criteria:** all existing planner-related tests (`test_planner.py`,
  `test_task_builder.py`, `test_optimizer.py`, `test_tool_selector.py`,
  `test_plan_scorer.py`, `test_plan_variants.py`,
  `test_planner_intelligence.py`) pass, updated in place where the contract
  intentionally changed; the Planning phase never runs `ReferenceResolver`
  itself — if it needs a resolved reference, it was already resolved upstream.

### M8 — Context architecture (resolves A6, A7)
- Introduce a single `ContextManager` owning: available context, context
  production, context consumption, and context history — **availability only**.
  Reference resolution is explicitly *not* in this list; it is owned by the
  Reference Resolver introduced in M5 (see Section 4's corrected ownership
  table). `ContextManager` answers "do we have it"; Reference Resolver answers
  "what does it refer to."
- `Planner` asks "what context is available?"; `Executor` asks "what does this
  tool require?" — neither computes the answer itself anymore.
- Retire the legacy `requires` field on tools in favor of `requires_context` /
  `requires_tools`, explicitly modeled as two different concepts, then delete
  the legacy field once nothing reads it.
- **Exit criteria:** `execution/context_signals.py`'s existing invariant
  ("bucket presence does not imply usable context") becomes the *only* place
  this judgment is made; `ControlLayer`, `Executor`, and `Planner` all delegate
  to it rather than each holding their own copy.

### M9 — Execution contracts
- **Not** the full `ToolResult(success, data, error)` migration yet (that's a
  larger tool-by-tool migration, deliberately deferred) — this milestone
  formalizes failure *classification* on top of the existing `⚠️` convention:
  transient / bad-args / missing-context / wrong-tool / unrecoverable, feeding
  a slightly smarter (still subtractive-by-default) repair step.
- **Exit criteria:** `ExecutionLoop`'s repair logic can distinguish these
  classes without changing the existing `⚠️`-prefix contract tools rely on.

### M10 — API contract
- Introduce `PlannerDecision`, `ConversationResponse`, `ExecutionEvent` as the
  actual API response shapes, replacing the current
  `{message, plan, results, context}` shape.
- **Exit criteria:** `/api/chat` returns a `type`-discriminated response
  (`clarification` | `answer`) instead of always returning raw plan/results.

### M11 — Real event streaming (resolves A8)
- Replace collect-then-return with genuine push-as-it-happens events via SSE:
  `request.started → understanding.completed → clarification.requested |
  plan.created → step.started → step.completed → execution.completed →
  response.created`.
- **Exit criteria:** a client connected before the request starts sees events
  arrive incrementally, not all at once at the end.

*— Backend is now stable. GUI work begins. —*

### M12 — GUI state migration
- Restructure `App.tsx` into `components/ hooks/ state/ api/ types/`, matching
  the new backend contracts (`PlannerDecision`, `ExecutionEvent`, etc.)
  end-to-end in TypeScript rather than untyped `event.type: string`.
- **Exit criteria:** GUI no longer imports or reasons about backend
  implementation classes (`TaskBuilder`, `ToolSelector`,
  `ContextDependencyResolver`) — it consumes the API contract only.

### M13 — Response rendering (resolves part of A9)
- Markdown, code blocks, LaTeX, tables, source citation cards, separated from
  the raw retrieval dump. Sources become collapsed-by-default cards, not inline
  bracketed text.
- **Exit criteria:** an `explain` answer with sources renders as formatted
  prose with a separate, collapsible "Sources · N" section — never raw
  `[Source 1: domain]` text as the visible answer.

### M14 — Developer Inspector (resolves remainder of A9)
- Event-driven, three-layer information hierarchy: Conversation (primary) →
  Activity (expandable summary) → Inspector (full diagnostics: request,
  understanding, plan, context, execution, timing).
- **Exit criteria:** default conversation view shows zero internal state;
  Inspector, opened explicitly, shows everything currently dumped inline today.

### M15 — Visual polish
- Live step-by-step "thinking" indicator, transitions, loading/error states,
  responsive layout.

### M16 — Regression suite hardening
- The reasoning regression suite does not start here — it starts at **M4**,
  the moment the first critical reasoning behavior (`CLARIFY`) exists to
  protect. Each subsequent milestone adds its own golden test as it ships:
  M5 adds the reference-resolution scenarios, M6 adds the retrieval-invariant
  scenarios, M7 adds a full-pipeline regression pass, and so on. Waiting until
  M16 to begin protecting reasoning would leave nine milestones of new
  behavior unguarded while they're being built.
- M16 is where that already-growing suite gets **consolidated and hardened**:
  organized into the unit / integration / golden-scenario structure of
  Section 7, deduplicated, and reviewed for coverage gaps against Section 6
  as a complete set — not authored from scratch.

  ```text
  M4  → first golden test (CLARIFY)
  M5  → reference-resolution golden tests
  M6  → retrieval-invariant golden tests
  M7  → full-pipeline migration regression
  ...
  M16 → consolidate / harden the suite
  M17 → full E2E suite
  ```

### M17 — End-to-end scenarios
- Twelve-scenario golden suite covering greeting, direct command, ambiguous
  request, clarification, contextual follow-up, web retrieval, document RAG,
  calculator, multi-step, tool failure, invalid input, concurrent requests
  (directly exercising the M1/D3 fix).

### M18 — Documentation (resolves A10)
- Rewritten only now, against the *actual final system* — not before, so it
  isn't stale again in a month. Stale diagrams and docs referencing
  `DependencyResolver` are removed as part of this milestone, not patched
  piecemeal earlier.

---

## 6. Golden regression scenarios

These are the scenarios that matter most and should never regress once fixed:

```text
"explain something"                                    → clarify
"transformers"  (as answer to the above)                → resolves prior clarification, then answers
"explain transformers"                                  → answer
"explain transformers" → "what are its applications?"   → resolves "its" → transformers
"compare transformers and neural networks"
  → "what are its applications?"                        → clarify (two candidates)
"open github"                                            → execute
"calculate 5 + 6"                                        → execute
"open github then explain git"                           → execute, order preserved
"hi"                                                      → conversational, no tools run
```

---

## 7. Test strategy

Three levels, maintained throughout the migration:

- **Unit** — request understanding, clarification, reference resolution, query
  normalization, tool selection, plan scoring — each in isolation.
- **Integration** — request → planner → executor → context → response, as a
  pipeline.
- **Golden scenarios** — Section 6, run end-to-end through the real runtime.

**Rule for the whole migration:** every commit leaves the suite green. If a
contract intentionally changes, the affected test is updated in the *same*
commit as the behavioral change — never deleted or loosened just to unblock CI.

---

## 8. What is explicitly deferred

To keep this migration's blast radius honest:

- Full `ToolResult(success, data, error)` migration away from the `⚠️`-string
  convention (M9 only adds classification on top of it).
- LLM-based reference resolution (M5 ships deterministic-only; LLM fallback is
  only added later if evidence shows the deterministic path is insufficient).
- LLM-based re-planning in `ExecutionLoop` repair (still subtractive-only after
  this migration; failure *classification* from M9 is a prerequisite for this,
  not this migration itself).

---

## 9. Summary

| Phase | Scope | Depends on |
|---|---|---|
| M0–M1 | Baseline + isolated defects | Nothing — start immediately |
| M2–M6 | Conversation state → clarification → references → intent/capability | M1 |
| M7–M9 | Planner migration, context unification, execution contracts | M2–M6 |
| M10–M11 | API contract, real streaming | M7–M9 |
| M12–M15 | GUI migration, rendering, inspector, polish | M10–M11 |
| M16–M18 | Regression suite, E2E scenarios, documentation | Continuous from M4 onward, finalized last |

Backend (M0–M11) ships value on its own — `"explain something"` clarifying
correctly does not require a single line of GUI change. GUI work does not begin
until the backend contract it depends on (M10–M11) is stable, so the frontend is
built once against a real contract instead of twice against a moving one:

```text
Reason correctly
      ↓
Expose correct state
      ↓
Define stable API
      ↓
Stream correct events
      ↓
Render beautifully
```

not:

```text
Make GUI beautiful
      ↓
Try to hide backend problems
```

The current GUI already demonstrates why this order matters: it faithfully
presents whatever the backend produces, including whatever the backend gets
wrong. Polishing it before the reasoning architecture is fixed would only
build a prettier interface around incorrect behavior.

---

## 10. Freeze notice

This document is v1.0. It has been through four review passes and the
architecture is considered settled: reference resolution and clarification
ownership are unambiguous (Section 4), `RESPOND` and `CLARIFY` semantics are
explicit (Governing Principles, M3), the retrieval-decision invariant is
precisely worded (M6), `ReferenceResolver` sits in Request Understanding
rather than in the planning pipeline (M7), and the regression suite is
understood to start growing at M4, not M16 (M16). Further changes to this
plan should be corrections of fact discovered during implementation, not new
architectural ideas — those go through the ADR process referenced in M18,
after the relevant milestone ships, against the system as it actually is.

**Next action — the concrete sequence, in order:**

```text
M0
 ↓ verify clean gui-integration branch
 ↓ run the 84 tests, confirm they pass
 ↓ record baseline
 ↓
M1-D1  (TaskOptimizer abbreviation fix) → tests → commit
 ↓
M1-D2  (Explain-button mismatch fix)    → tests → commit
 ↓
M1-D3  (event_callback race fix)        → tests → commit
 ↓
checkpoint — inspect the diff, decide whether M2 is ready
```

Do not proceed to M2 until that checkpoint is explicitly reached and
reviewed. This keeps the migration a controlled, incremental process rather
than a continuous rewrite.
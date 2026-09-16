# Revision plan: a small controller for graph-based proof checking

Date: September 15, 2026. Status: revision rationale. The [implementation receipt](controller-implementation-2026-09-15/README.md) records delivered software, validation and remaining release gates.

For implementation, read the [detailed controller plan](controller-implementation-plan.md) first. It supplies the exact interfaces, coherent work-unit batching, response contracts, migration and acceptance fixtures. This document records the revision rationale and the same C0-C5 sequence.

**The coordinator model owns the scientific work. The controller is a synchronous local tool for bookkeeping, bounded assignment preparation and scheduling suggestions. It never calls a model or runs a self-directed checking loop.**

This plan revises the implemented database pilot examined in the [goal-alignment audit](goal-alignment-audit-2026-09-14/review.md), baseline source identity `6b27574bf1baece6d7c1bbd5c404a9eca4afe14ad75b6db3e42d74e485f1f428`. It preserves the [architecture](architecture.md), typed records and existing Archify UI. It is the next focused revision, not another replacement architecture.

## 1. Responsibility boundary

| Decision or operation | Owner | Controller contribution |
|---|---|---|
| Read the paper; choose scope, sources and meaningful division points | Coordinator | Capture sources, supply IDs and validate submitted records |
| Classify assumptions, definitions, local results and external restatements | Coordinator | Enforce the allowed categories; never infer them from prose |
| Identify dependencies, joint inputs, cases, scopes and proof routes | Coordinator | Store explicit references and report structural inconsistencies |
| Add an intermediate claim or change a proof split | Coordinator | Preserve discoveries and recompute work after an explicit graph edit |
| Track unfinished work and suggest an order | Controller | Derive tasks and prerequisites from accepted records |
| Choose scientific priority, models, contexts and parallel assignments | Coordinator | Prepare selected work and report mechanical constraints |
| Judge mathematics, implications and disagreements | Checker models and coordinator | Validate representation/provenance and save judgments |
| Handle a failed submission | Coordinator/checker | Preserve the input and return exact diagnostics |
| Calculate audit completion | Controller through shared assessment logic | Account for required current work, independently of whether outcomes are positive |

The initial graph is provisional. The coordinator registers major items and source-backed routes first, then refines meaningful intermediate claims while checking. Routine algebra need not become separate nodes. An intermediate or part may be established by a group inside its parent's argument; it does not automatically need its own argument.

Robustness means the controller has a defined, bounded response when it cannot proceed. Missing structure, source ambiguity, uncertain ordering or an oversized task returns control to the coordinator. The controller does not solve those problems by guessing.

## 2. The complete workflow

| Stage | Coordinator/model action | Tool action | Saved result |
|---|---|---|---|
| Register | Read the manuscript and propose items, routes, uses and scopes | Existing source and graph-authoring commands validate and commit | One source-linked local graph |
| Inspect | Review unfinished work and decide priorities/refinements | `work list` derives tasks and coordinator actions | No authored task ledger |
| Prepare | Select suggested work or name a coherent subset | `work prepare` assembles bounded context and response scaffolds | Immutable task-scoped packet |
| Reason | Coordinator dispatches a checker through the host's agent tools | Controller is idle while the model reasons | Worker returns structured output |
| Register output | Coordinator supplies its trusted envelope and unchanged worker bytes | `work submit` preserves, validates and registers output | Receipt, saved draft or recoverable diagnostic |
| Continue | Correct representation, acquire context, refine the graph or move on | Recompute work; `work inspect` retrieves prior submissions | Resumable progress |
| Review/deliver | Arrange independent review, reconciliation and applicable global checks | Existing review/report tools use the same assessment rules | Honest completion and reader state |

The loop belongs to the coordinator's instructions:

```text
read and register the initial graph
while the coordinator chooses to continue:
    inspect the derived worklist
    resolve graph/source/scope questions when necessary
    prepare a bounded assignment
    dispatch a checker through the host's agent tools
    submit its structured response
    choose the next action from the receipt or diagnostic
save a checkpoint and a concrete continuation state
```

A model-written prose plan may explain priorities. It cannot declare tasks complete, change audit scope or override evidence. Those changes require validated records. Checker discoveries become drafts or source-grounded proposals; only the coordinator applies graph refinements.

## 3. Four bounded controller operations

These are proposed interfaces under the existing `paper_audit.py` entrypoint.

| Operation | Inputs | Output and limits |
|---|---|---|
| `work list DB --audit ID` | Audit ID, optional coordinator focus and pagination | Revision, progress, task/unit rows and coordinator actions. Default 20 rows, maximum 100; cursor tied to snapshot |
| `work prepare DB --audit ID` | Optional explicit task IDs/focus, mode and context limits | One coherent packet, response scaffold, selected/deferred IDs and compact receipt. Default at most 5 work units; hard maximum 10; a unit can contain several checks |
| `work submit DB --submission FILE --response FILE` | Trusted coordinator envelope and original worker bytes | Saved submission reference plus accepted mappings, draft receipt, diagnostics or changed-input details |
| `work inspect DB` | Exactly one request ID, packet ID or audit ID; optional detail output or bounded audit-history pagination | Receipt/diagnostic, prepared context or history. Metadata by default; large content written only on explicit detail request |

Preparation may recommend a batch; dispatch remains an explicit coordinator action. The controller has no provider SDK, API keys, model selection, daemon, timer or automatic retry.

One coordinating writer may manage several independent checker contexts. A prepared packet records preparation, not dispatch or a reservation. The coordinator passes already-assigned task IDs to exclude from new suggestions. After interruption, unfinished prepared packets are shown for inspection; the coordinator checks actual host worker status before reassigning. Preparation/submission history is separately paginated; deriving tasks must not load every old packet body. There are no worker leases or automatic expiration rules.

### Derived task rows

Use existing obligation IDs for ordinary checks. Rows contain the exact target, major owner, argument if applicable, role/action, required flag, prerequisite IDs, concise reasons, saved draft/check references and next action. Mathematical outcome, freshness and support remain separate fields.

| Work state | Meaning |
|---|---|
| `ready` | Records/context exist and ordinary scheduling prerequisites have been examined |
| `waiting` | Another recorded task remains unfinished; name it |
| `needs_coordinator` | Structure, source, scope or assignment size requires an explicit decision |
| `satisfied` | This examination has current accepted evidence under the audit rules |

Drafts remain unfinished. Current completed `gap`, `refuted` and `inconclusive` judgments can satisfy examinations. Missing work never becomes an inconclusive judgment automatically.

Actions such as “register the establishing inference” are derived diagnostics with stable target-based IDs, not new mathematical collections or check kinds. They disappear when the underlying records satisfy the applicable rule.

## 4. Work derivation and ordering

Use the detailed recorded proof structure, not the major-node display projection. Ownership is not a dependency.

**Scope.** For Focused audits, follow actual consumed internal prerequisites and relevant local context from the selected roots. Stop at assumptions explicitly in force. External results follow source verification/application checking. For Full audits, reconcile current proof inventory against declared coverage and explicit exclusions. New results/routes enter required work or reopen scope review. Only the coordinator decides exclusions. Parser candidates cannot certify that the entire manuscript was inventoried.

**Exact establishment.** A consumed proof-required claim needs an establishing group or route for that exact claim. A child's argument does not establish its parent. A theorem with no incoming edges still needs derivation/final composition. Missing structure produces a coordinator action, not a check against a nonexistent group. If the paper omits justification, the coordinator represents and judges the omission through source-backed argument/check records; the controller does not fabricate a proof route.

**Ordinary work.** Derive source fidelity, applications, joint derivations, required cases/discharges, final composition, external-source verification, independent review, reconciliation and applicable global tasks from existing records. One derivation must feed status, worklist, report progress and release completion. Do not add a second completion calculation.

**Ordering.** Normally recommend supplier examination before dependent applications, applications before joint derivation, and local groups/cases before final composition. A completed defect upstream does not cause an endless wait. Downstream work can proceed with conditional or unavailable support clearly displayed.

**Batch selection.** Use the ready frontier as a seed, then grow through compatible downstream work in the same argument/result context and role. Each group is one complete-context unit containing its application, derivation and applicable case/discharge obligations. A later unit, including final composition, can join when its unfinished predecessors are included earlier in this assignment and its outside prerequisites are examined or explicitly provisional. Return fewer than five units when fewer fit. One assignment can produce many fine-grained checks in one model call. Excluding already-assigned work defers its unit but retains its dependency edges. Provisional selection cannot bypass missing records, unavailable required source, qualification or blinding constraints.

**Cases and alternatives.** Keep all recorded joint premises and required cases. Distinct written routes remain separate audit work even when one proves the conclusion. The controller does not choose the “best” route or ignore failed alternatives.

**Cycles.** Traverse with visited sets and name implicated uses, groups and routes. Do not enumerate all possible paths. Display-projection cycles do not block proof tasks. Detailed dependency cycles produce ordering diagnostics; the coordinator inspects induction, simultaneous reasoning, local hypotheses or circularity and can assign provisional local checks. Record its analysis through ordinary structure/checks, without a generic “cycle approved” checkbox or automatic refutation.

**No ready tasks.** Report remaining waiting/coordinator tasks and reasons. This means neither completion nor “wait forever.” Only shared assessment may report completion.

## 5. Truly bounded packets

Add genuine argument/group/use targets and bounded part checking before batching. Fix the current closure that widens local targets to the whole major owner.

| Task | Essential context |
|---|---|
| Application | Use, supplier statement/part, needed form, substitutions, scope and use-site evidence |
| Joint derivation | Whole group, every jointly required input, relevant applications, exact conclusion, scope and derivation evidence |
| Case/discharge | Recorded case scopes, assumptions, required cases and combination/discharge evidence |
| Final composition | Exact result/part, route, required group/check summaries, coverage, scope and integration evidence |
| Independent review | Source-only statement/proof/context for the declared assignment |
| Reconciliation | Original relevant primary/independent evidence with exact version pins |

Supplier statements must not routinely import their proof excerpts. Include consumed internal passages for an explicit `proof_argument` use or a requested context extension. Correct the current supplier helper that includes every passage.

Apply one configurable serialized worker-input budget after deduplication, initially 128 KiB per assignment, alongside the unit-count limit. This measures bytes, not model tokens or difficulty. The coordinator may request another explicit budget within the implementation plan's ceiling; the controller never silently increases it. Report records/bytes and the largest context contributors.

An indivisible context unit over budget returns `needs_coordinator` and its measured size, with no truncated packet. The coordinator decides whether to split at a meaningful claim, refine source anchors or allocate more context. Scripts never shorten statements or drop premises to fit. Context indivisibility does not require all member checks to be submitted together.

Return packet paths/IDs and compact summaries to the coordinator. It dispatches the worker-facing packet, not its own worklist or internal manifest. Independent workers receive no primary judgments, inferred reconstruction, coordinator diagnoses or database access. Bounded part assignments must be recognized as within their parent's audit scope.

Preparation pins selected task membership, input versions/facets, relation guards and write scope. Generic packet extensions preserve prior evidence. In this first slice, work packets require fresh preparation for added context, because the generic extension path would lose their task scope. Stale selections receive a diagnostic rather than silently changed assignments.

Derive the graph/task view once per call. Load full bodies for selected context where feasible. Full inventory traversal may be linear in graph size; do not repeat it per task. Apply finite diagnostic traversal budgets and return `limit_reached` with continuation information instead of claiming an incomplete traversal is complete.

## 6. Structured submission and recovery

The coordinator envelope supplies reviewer/qualification provenance and packet identity; audit and mode come from the stored assignment. The packet/scaffold supplies assigned targets and expected operations. The worker supplies state, outcome, reasoning, evidence, conditions and next action.

For primary work, a thin adapter expands the scaffold into existing check/observation edits and generates IDs, versions and repeated administrative fields. It never invents reasoning, outcomes, findings or coverage. Coverage spans and claim assignments remain explicit; mechanical offset helpers may reduce authoring work.

Independent output retains the existing unchanged worker-response contract, wrapped by the controller's trusted envelope. Reuse the review submission planner, source-grounded mapping and reconciliation. Do not create a second independent-review method. A new claim identified by a worker remains source-grounded pending evidence until the coordinator registers it.

Each explicit submission is atomic over its included edits. A prepared assignment may be completed across multiple submissions. A submission may contain fewer tasks than were prepared and mix complete checks with valid drafts. Other tasks remain pending. Any malformed included edit rejects that included batch as a whole. Do not silently discard invalid entries and commit the rest; the coordinator can resubmit an explicit corrected subset.

An unresolved independent `SourceTarget` mapping is structurally valid pending work, not a malformed judgment. The existing review path may stage resolvable checks while the response remains `needs_revision`; those checks receive no independent-review completion credit until the response is accepted under the declared coverage rules. Preserve that distinction when reusing review submission. A partial worker response must not be relabelled as a complete review of a larger proof.

A partial-save receipt returns the remaining task IDs and a request to prepare their current context. Earlier saves may change check/coverage references in the original packet, so do not require remaining work to keep using an obsolete packet. Carry forward existing drafts. If unsaved reasoning was already produced, compare its original consumed inputs with the new packet and preserve both provenance references. Progress-only or cosmetic changes can be rebound mechanically; changed mathematical inputs, including judgments actually consumed by composition/reconciliation, require reconsideration. Never exempt all changes made by the same batch or restart mathematical reasoning merely because a previous partial save advanced the revision.

| Result | Mechanical response | Coordinator action |
|---|---|---|
| Complete judgment, including a defect | Save and return receipt | Decide scientific follow-up |
| Draft/explicit partial batch | Save; keep unfinished work visible | Resume/reassign with saved reasoning |
| Schema/reference/coverage-structure error | Preserve bytes; return field/index diagnostics; no check credit | Correct representation |
| Relevant input change | Preserve proposal and original packet; identify changed inputs | Decide what needs reconsideration |
| Cosmetic-only change | Atomically compare consumed facets/memberships; preserve provenance and eligible work | No new mathematics solely for a caption |
| Missing context/graph refinement | Preserve observation or draft | Acquire source or refine graph |
| Invalid envelope/qualification or unsupported version | Explicit rejection before acceptance | Correct setup/dispatch |

No rejection calls a model. Hash the canonical trusted envelope together with the hash of the exact original response bytes; generated IDs and adapter-expanded edits are not the logical request digest. Exact retries keep the request ID; an accepted request returns its original receipt before generating new edits or revalidating new inputs. A reused ID with different envelope/response content is rejected. Corrected content or a deliberate new attempt after a conclusive rejection uses a new request ID, preserving the earlier diagnostic. No retry policy tries to turn a negative mathematical judgment into a positive one.

### Minimal durable bookkeeping

Reuse packets for prepared context, checks for drafts/next actions, responses/maps for independent evidence, and commits for accepted work. Task state stays derived.

Add **one operational submission index** referencing existing blobs so rejected/stale proposals remain discoverable after restart. Store request ID/digest, packet, trusted envelope, original-response hash, received time and diagnostic/receipt. This is transport recovery data, not a second graph or task ledger.

After valid envelope, packet identity/mode, audit and reviewer-provenance checks, commit the original bounded input before interpreting judgments or testing current input-version conflicts. Thus an obsolete packet can produce a preserved conflict rather than losing the proposal. Intake is `received`; processing yields `accepted`, `needs_revision` or `conflict`. Original bytes stay immutable. Acceptance state/receipt must agree with the mathematical commit transaction.

After a crash, `inspect` reports the pending submission and any existing commit. An explicit identical retry resumes safely or returns the original receipt. Do not use optional telemetry as recovery authority.

Advertise and enforce a finite intake-byte limit before loading arbitrary output. Invalid envelopes/credentials or oversized input may be rejected before persistence; say whether bytes were actually saved and preserve the caller's file. SQLite backup is the only recovery transport in this revision and preserves the operational index/blob references. Existing mathematical exports do not restore controller state; no new native JSON restore is required. Operational entries never count as proof support or enter independent packets.

## 7. UI and installed workflow

Keep the major-node Archify graph. Add a read-only worklist with meaningful labels, exact target links, drafts and reasons for waiting. Selecting an intermediate task selects its major owner and opens the exact task below. Work states are distinct from mathematical colors.

The HTML remains a revision-labelled snapshot, without model execution, graph editing or background scheduling controls. Generate reports on explicit checkpoints or meaningful batch boundaries rather than after every controller operation.

The G6 correction, populating reader details on selection, remains a separate large-report improvement. It may follow the controller's functional slice and does not require a new browser application.

Make legacy and database instructions mutually exclusive. Ship the coordinator loop, compact record reference, complete small graph example, response scaffolds and recovery examples. An installed-only coordinator must not need this architecture folder or legacy per-line forms.

## 8. Revision phases

C0-C5 are the next revision of the implemented pilot. They do not restart or renumber the earlier R0-R8 migration plan.

| Phase | Work | Exit evidence | Existing mapping |
|---|---|---|---|
| C0. Interfaces and compatibility | Fix work/scaffold shapes and diagnostics; synchronize owning documents; implement the small migration for receipts and packet support | Historical records/packets preserved; unsupported combinations diagnosed | R2 / P1 |
| C1. Complete derived work | Repair scope/exact establishment; expose shared worklist; add deterministic order and diagnostics | G1 omissions reopen work; completed defects do not deadlock it | G1/G2; R3 / P3 |
| C2. Local assignments | Add local closure, source-only bounded parts, task pins/scaffolds and size limits | Small tasks stay small as unconsumed siblings grow; joint premises stay present | G3; R2-R4 / P1/P3/P4 |
| C3. Submission/recovery | Thin adapters, intake index, precise errors, cosmetic reuse and atomic/idempotent recovery | Invalid output survives restart; stale scientific inputs still conflict; partial work saves | G4/G5; R3-R4 / P3/P4 |
| C4. Usable tool and reader | Wire CLI, installed instructions/examples and work links; rebuild both shared bundles | Installed-only rehearsal completes a short chain and stop/resume | G2/G7; R5-R6 / P5/P6 |
| C5. Integrated evaluation | Vertical scenario, relevant suites/bundle gate, then bounded mathematical pilot | Separate software behavior, reasoning, authoring overhead and unfinished work | R7 / P7; R8 release remains gated |

C1 and C2 can proceed independently after C0 fixes interfaces. C3 integrates their packet rules. C4 can prepare examples in parallel but must exercise the final commands. C5 tests the actual combined tree.

Prefer one work-derivation module and one thin controller adapter, with focused edits to assessment, packets, acceptance, queries and CLI. Reuse common validation and assessment. Do not copy them into a second implementation.

### Contracts and versions

Use existing named version identifiers; add no controller version or executable plan language.

- The submission index and SQL constraint for newer packets require a storage migration from format 2 to format 3, preserving historical bytes.
- Task-scoped packets/scaffolds use packet version 2 with explicit version-1 handling. The current SQL `packet_version = 1` constraint must migrate alongside code.
- Keep record contract 3 if mathematical record shapes/meaning remain unchanged. Derived actions and operational receipts are not new mathematical collections.
- New reader worklist data uses projection version 2 with a matching renderer and explicit handling of version 1.
- Keep `item-audit/1` if scientific review requirements are unchanged; editorial workflow clarification alone does not invalidate prior qualification or mathematics.
- Release core/skill metadata only with acceptance; rebuild both generated bundles from the maintained source.

C0 updates the architecture's scheduling section, handoff commands/transactions/projection, record contract/DDL and shipped protocol together. This plan owns the proposed coordinator/controller boundary; existing contracts still govern today's runtime until coordinated implementation changes land.

## 9. Acceptance scenarios

1. **Simple chain:** recommend prerequisite work, then group compatible applications/derivation/composition into one assignment; one response saves multiple records. Stop and resume with a clear next task.
2. **Defect upstream:** a completed gap/inconclusive judgment is not assigned forever; downstream support remains qualified.
3. **No incoming edges:** an input-free proof still requires derivation and final composition.
4. **Missing intermediate:** absent establishment produces coordinator work and prevents false completion.
5. **Exact target:** a child's argument cannot close its parent; a part proved within its parent needs no redundant argument.
6. **Scope growth:** Focused includes consumed prerequisites; new in-scope results/routes reopen Full work.
7. **Joint inputs/cases/alternatives:** retain distinct dependencies and all required evidence; success of one route does not erase another written route.
8. **Cycles:** finite detailed diagnostics, no blockage solely from major-owner projection, and explicit provisional checking remains possible.
9. **Local scaling:** adding 1,000 unconsumed sibling groups does not enlarge selected group context or import their proofs. Measure rows/bytes, worker input and coordinator output separately.
10. **Limits:** default at most five work units, maximum ten; oversized indivisible context returns measured diagnostics without truncation. Count model assignments separately from fine-grained check records.
11. **Invalid/partial output:** exact errors, original bytes preserved, no accidental partial commit; an explicit valid subset of drafts/checks saves. Refresh and finish its remainder without treating bookkeeping progress as changed mathematics. Unresolved independent mapping stays distinct from malformed output and grants no premature completion credit.
12. **Retry/crash:** repeat a request and interrupt after intake/after mathematical commit; inspect/resume without duplicate judgments or lost input. Fresh adapter-generated IDs cannot change the logical request digest.
13. **Changed evidence:** caption edits avoid repeated mathematics; changed statement/scope/source/relevant membership cannot silently accept obsolete reasoning.
14. **Independent scope:** bounded source-origin part within a parent audit is assignable; no primary work or coordinator-only diagnostics leak.
15. **UI/installation:** a task opens its exact reader location; installed-only usage works without development documents or legacy paperwork.
16. **Nothing ready:** report why coordinator action is needed; never call this completion merely because nothing was selected.

Use these as adversarial behavior fixtures, not tests mirroring helper internals. Run relevant suites once on the final integrated tree and broaden only for new failures/concerns.

The live pilot remains bounded to two hours. Include a realistic short chain, joint inference, meaningful intermediate, imperfect response and stop/resume. Measure source/graph authoring, fresh reasoning, formatting corrections, input conflicts, controller work and report time separately. Record unfinished scope honestly; reaching the time bound is not completion. Fresh independent mathematical review and actual browser acceptance remain distinct evidence.

## 10. Size boundary

The controller keeps no autonomous goal, scientific plan, alternate graph, persistent scheduling queue, worker leases or model conversation history. It does not decide proof importance, acceptable assumptions, correctness or where an oversized argument should be split.

Its job is: **given saved graph records and an explicit coordinator request, return bounded actionable work or register a structured response with an honest receipt.** The coordinator remains responsible for building/refining the graph and directing the scientific investigation.

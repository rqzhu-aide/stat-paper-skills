# Implementation plan: a bounded proof-checking controller

Date: September 15, 2026. Status: implemented interface specification. Actual validation, pilot limitations and open release gates are recorded in the [implementation receipt](controller-implementation-2026-09-15/README.md).

This is the concrete implementation specification for the database pilot. Read this document first. It replaces the ready-frontier-only batching rule in [controller-revision-plan.md](controller-revision-plan.md): **the ready frontier seeds a coherent assignment, which may include an ordered sequence of local applications, derivations and final composition in one model call.**

The coordinator owns manuscript interpretation, graph construction/refinement, scientific priorities, model dispatch and adjudication. The controller performs bounded mechanical work on accepted records. It never calls a model, invents a dependency, writes mathematical reasoning, chooses a scientific proof route or retries until a judgment becomes positive.

## 1. Delivery target and baseline

The audited source identity is `6b27574bf1baece6d7c1bbd5c404a9eca4afe14ad75b6db3e42d74e485f1f428`. The [goal-alignment audit](goal-alignment-audit-2026-09-14/review.md) records the missing scope, scheduling, packet, recovery and instruction behavior. Record the actual starting identity again when implementation begins; preserve unrelated working-tree changes and historical audit evidence.

A successful first slice permits the following without per-record model calls:

1. The coordinator registers the source-linked graph for a short argument.
2. One preparation returns source-fidelity work, two applications, their joint derivation and final composition as one assignment.
3. One checker response produces five separately addressable observations/checks, with explicit coverage where needed.
4. One submission validates and saves those records atomically.
5. A gap upstream remains attached to its actual derivation; a downstream implication may remain locally valid while overall support is conditional.
6. An interrupted, partial or malformed response can be inspected and continued without losing its reasoning.
7. The same derived task model supplies status, the reader and release completion.

The first-slice fixture starts with supplier statements/source context already examined. Its five observations/checks are separate from the explicit coverage row also saved by that submission; it does not assert that a fresh whole-paper audit has only five obligations.

The current runtime already provides records, sources, packets, bindings, checks, reviews and publication. Implement this as focused changes around that core, not a new agent framework.

### Document ownership

This document owns the proposed controller interfaces, assignment policy, limits and implementation sequence. The linked [task design](controller-handoff/task-derivation-design.md), [packet/reader design](controller-handoff/packet-reader-design.md) and [submission design](controller-handoff/submission-design.md) supply implementation details; this document wins if names/defaults differ. Existing [record shapes](handoff/record-contract.md), mathematical meanings and immutable-evidence rules remain authoritative unless a change is explicitly specified here. Synchronize the affected architecture/handoff sections during C0. Do not leave two incompatible workflow instructions in the installed skill.

## 2. Three objects, one source of truth

| Object | Definition | Persistence |
|---|---|---|
| Obligation | One examination: source fidelity, application, derivation, case/discharge, composition, external source, independent review, reconciliation or global check | Derived requirement; existing check/observation/reconciliation records satisfy it |
| Work unit | Complete context for one group and its application/derivation/case/discharge obligations; composition, source fidelity, ungrouped application, external-source and global/reconciliation work may form standalone units | Derived grouping only |
| Assignment | One ordered sequence of compatible units for a single role and local argument/result context | Existing immutable packet with version-2 assignment metadata |

The default assignment has at most five units; the maximum is ten. It can produce more than ten fine-grained records. Those limits bound assignments, not the number of mathematical facts the reviewer may record.

A group unit has indivisible context: all its premises and relevant scope must be supplied together. It does not impose all-or-nothing progress. Each explicit submission is atomic over its included edits, and the worker may return an explicit subset or drafts.

Do not create task, queue, lease, active-worker or planner tables. The only new operational table is the submission receipt index specified in section 8.

## 3. Maintained-source changes

| File/module | Responsibility after revision |
|---|---|
| `assessment.py` | Correct effective scope and exact establishment; derive required obligations and mathematical states once |
| New `work.py` | Pure task dependency/unit derivation, ordering, selection and pagination |
| New `controller.py` | Thin prepare/submit/inspect orchestration and primary response adaptation; no provider calls |
| `packets.py`, `refs.py`, `bindings.py` | Local indexed context, version-2 task scope, per-task semantic inputs and original-packet provenance |
| `contract.py`, `validation.py` | Closed controller DTO schemas; narrow `work_primary` permissions; shared prospective-state validation |
| `acceptance.py`, `review.py` | One transaction-owned acceptance kernel; original-input idempotency; independent staging/mapping preservation |
| `storage.py`, `schema.sql`, `export_import.py` | Format-3 migration, receipt accessors, packet-version handling, accurate snapshot-format reporting |
| `queries.py`, `projection.py`, renderer | Same task derivation, readable task links and separate local/support indicators |
| `cli.py` | Four work verbs and explicit native storage migration |
| Skill references/examples, bundle builder/tests | One installed coordinator workflow; both bundles generated from maintained source |

Avoid a second copy of validation or completion logic. A new internal DTO module is unnecessary unless the new schemas make `contract.py` materially harder to navigate.

## 4. Effective scope and task graph

### 4.1 Scope is graph-derived, never scientifically inferred

For Focused audits, traverse actual consumed uses, local scope assumptions and exact establishing structures from the selected roots. Stop proof-establishment traversal at explicitly assumed premises. Include source-fidelity/context obligations where the existing method requires them. External results use source verification and application checking; they do not automatically need a local proof.

For Full audits, reconcile registered in-scope proof items and written routes against targets/exclusions. A newly registered result or route must add work or reopen scope review. Exclusions remain explicit coordinator-authored records. The controller cannot detect an entirely omitted mathematical dependency or guarantee that a parser found every declaration. The coordinator must read/review the inventory; checkers compare each assigned written argument with its recorded premises while doing substantive checking.

A major result needs its own final composition. A child's argument is insufficient. Parts and intermediates may be established by a group inside the parent's route; do not create redundant arguments. A consumed local claim with no establishing group/route produces a coordinator diagnostic. A result with no incoming edge still needs its own proof work.

A structural draft remains saveable. If the source omits justification, the coordinator records the source-backed omission and judges it through ordinary argument/check records. Scripts never manufacture an input-free proof to close missing structure.

### 4.2 One derived view

Implement pure functions around one snapshot:

```python
derive_scope(graph, audit, limits) -> ScopeView
derive_task_graph(graph, scope, assessment) -> TaskGraph
derive_units(graph, task_graph) -> UnitGraph
select_assignment(work, request, limits) -> Selection
```

Split enumeration from evaluation to avoid circular imports: scope/obligation enumeration must not depend on already evaluated work states; assessment evaluates those obligations; work ordering consumes the resulting view. `status`, projection and release call the same derivation, not independently maintained lists.

Ordinary rows use the existing `obligation_id(audit_id, target, kind, role)`. Required fields:

```text
id, target: Ref, owner: Ref|null, argument: Ref|null,
kind, role, action, required: bool,
state: ready|waiting|needs_coordinator|satisfied,
prerequisite_ids: [ID], waiting_on: [ID], blocker_ids: [ID],
judgment_refs: [PinnedRef], draft_refs: [PinnedRef],
next_action: string|null,
outcome, freshness, dependency_support
```

Kinds/outcomes retain existing enums. Actions are `check`, `compare_source` or `reconcile`. Coordination diagnostics are separate derived rows with `id, code, target_refs, related_task_ids, message, required`; use stable IDs from audit/code/target identity, not source line numbers or mutable captions.

A current completed gap/refutation/inconclusive examination can be satisfied. Drafts, stale evidence, incompatible review and unresolved conflicting judgments are not. Do not infer satisfaction from transport receipt state or a nonempty reasoning string alone.

### 4.3 Ordering edges

Use the detailed recorded structure, not ownership-projected visual edges.

| Task | Ordinary ordering predecessors |
|---|---|
| Source fidelity | Required source/context availability; no mathematical predecessor |
| Application | Relevant source comparisons and the supplier's required primary establishment/source verification, except an explicit assumption |
| Group derivation | Its application obligations |
| Case/discharge | Recorded case/input examinations and necessary scope context |
| Composition | Required local groups/cases/discharges and exact target/part comparisons; coverage is required context/output, not a separately completed predecessor |
| Independent review | Source/provenance/qualification readiness, not primary reasoning as input |
| Reconciliation | The primary and accepted independent records actually compared |
| Global work | Its declared scope and recorded applicable prerequisites |

Do not make a local use of an intermediate wait for its containing theorem's final composition. Its local establishing group supplies the predecessor. Do not make primary work wait for independent review by default. Multiple written routes remain in scope; deterministic ordering is not scientific selection of a preferred route.

Missing written coverage keeps completion false but does not prevent preparing composition. Return uncovered spans as required output that the worker can supply in the same response as its composition check. Validate that combined prospective state at submission; otherwise requiring already-complete coverage would force an unnecessary extra model call.

Completed negative outcomes do not create an endless scheduling wait. Their implications remain in the separate support calculation. Disputed or incomplete inputs are named explicitly; the coordinator may request provisional local reasoning.

## 5. Coherent batching algorithm

Detect genuine task cycles before contracting each group and its applicable obligations into one context unit. Then remove ordinary internal ordering edges from the unit graph and retain the ordered obligation list inside it. Compute unit readiness from external predecessors, not from members that are waiting on one another in a valid internal sequence. A satisfied member is supplied as prior work, not assigned again.

1. Determine the requested audit/focus and role. Exclude already-assigned obligations from selection only, retaining their dependency edges. Defer a group unit if any pending member is already assigned; its dependents do not become falsely ready.
2. Choose a ready seed by coordinator focus, source order and stable ID. A focus such as Lemma 1 means “work toward this target”; unfinished external prerequisites may be recommended first.
3. Fix the local context to one argument/result and role. A source-fidelity unit can attach to that context without duplicating its logical obligation.
4. Add compatible units in dependency order. A later unit is eligible when every unsatisfied predecessor is either already included earlier in this assignment or is an explicitly permitted provisional boundary.
5. Include final composition in the same assignment when its required local predecessors are satisfied or included earlier and its complete context fits.
6. Stop at the unit/context limits. Return the included units plus deferred IDs/reasons. Never fill capacity with unrelated tasks merely to reach five.
7. If no complete first unit fits, return a coordinator diagnostic, not a truncated packet.

This is deterministic batching of recorded work. It does not choose new proof boundaries or add inferred claims.

Explicit task selection expands to its complete group context unit. The permitted-result list identifies only unsatisfied requested/unit obligations; successful prior checks are not reassigned. The worker may save a subset. Provisional mode can cross unfinished mathematical examinations but cannot bypass absent records, unavailable required evidence, invalid scope, qualification or blinding.

If an early unit fails, later local implications may still be checked under their exact stated premises. Final composition must report what the combined argument actually establishes. “All local applications were conditionally valid” is not sufficient for a supported complete route.

Use visited sets and strongly connected components or equivalent finite cycle detection. Name implicated uses/groups/routes. A display-only cycle does not block work. A genuine ordering cycle returns a diagnostic and permits explicit provisional local assignments; the coordinator judges induction, simultaneous reasoning or circularity. Do not add a generic cycle-approval record.

### Operational limits

| Limit | Initial value |
|---|---:|
| Units per assignment | Default 5, allowed 1-10 |
| Serialized worker packet | Default 131,072 bytes; explicit requests up to 1,048,576 |
| Unique packet records | 2,048 hard ceiling in this implementation |
| Worker response intake | 2,097,152 bytes |
| Coordinator envelope intake | 65,536 bytes |
| Worklist rows | Default 20, maximum 100 |
| Snapshot traversal | At most 100,000 distinct records and 500,000 relation visits |
| Returned diagnostics | At most 100, with total count/truncated flag |

These are computational limits, not mathematical thresholds. All loops are finite. Measure before materializing oversized blobs where possible. A limit failure names the exceeded bound and responsible context. No timeout or limit becomes mathematical failure or completion. Make traversal ceilings injectable in tests; future increases require explicit configuration, never silent retries.

Full-scope derivation may be linear in graph size. Reuse one snapshot/view per command and use indexed local lookups; do not scan full bodies once per unit. If full derivation exceeds its budget, report `analysis_complete: false` and no completion claim. Do not generate work from a secretly truncated graph.

## 6. CLI and Python interfaces

All commands return one JSON object on stdout; reuse exit codes 0/2/3/4/5/6. Diagnostic envelopes use the existing CoreError convention. Do not introduce a second exit-code system.

```text
paper_audit.py work list DB --audit ID
    [--focus COLLECTION:ID] [--snapshot REV] [--limit N] [--cursor TOKEN]

paper_audit.py work prepare DB --audit ID --mode primary|independent|reconcile
    [--focus COLLECTION:ID] [--task ID ...] [--exclude-task ID ...]
    [--max-units N] [--max-bytes N] [--allow-provisional] --out DIRECTORY

paper_audit.py work submit DB --submission ENVELOPE.json --response RESPONSE.json

paper_audit.py work inspect DB (--request ID | --packet ID) [--out DIRECTORY]

paper_audit.py work inspect DB --audit ID [--limit N] [--cursor TOKEN]

paper_audit.py migrate DB --backup BACKUP.db
```

Proposed public Python entry points:

```python
list_work(db, *, audit_id, focus=None, revision=None, limit=20, cursor=None) -> dict
prepare_work(db, *, audit_id, mode, focus=None, task_ids=(),
             exclude_task_ids=(), max_units=5, max_bytes=131072,
             allow_provisional=False) -> dict
submit_work(db, *, envelope_bytes: bytes, response_bytes: bytes) -> dict
inspect_work(db, *, request_id=None, packet_id=None,
             audit_id=None, limit=20, cursor=None) -> dict
```

Keep source/graph authoring through existing `source`, `get` and `apply` commands. The controller does not turn a worker's graph suggestion into an automatic graph edit.

List output contains `revision, audit_id, analysis_complete, progress, tasks, units, coordinator_actions, next_cursor`. The cursor encodes snapshot, filters and last sort key; reject changed filters or an unavailable snapshot rather than silently mixing revisions. Prepared/submission history is separately bounded and not included as full payloads in every worklist.

Prepare output contains `packet_id, revision, audit_id, mode, selected_unit_ids, assigned_task_ids, conditional_on_task_ids, deferred, size, files`. A normal blocked/oversized selection returns exit 0 with `prepared:false` and coordinator actions; malformed requests use exit 2. The CLI writes worker packet, coordinator manifest and scaffold to the requested directory, refusing conflicting existing files and registered source/database destinations. Reissuing inspection can regenerate those artifacts from immutable DB payloads.

Submit output contains `request_id, stored, state, committed_revision, receipt, record_map, remaining_task_ids, diagnostics, next_actions`. Successful drafts/negative judgments are exit 0. Malformed output is exit 2, conflict exit 3, and missing source exit 5; if intake was preserved, return `stored:true` and its request ID even with nonzero exit. Pending independent identity mapping is a successfully stored result at exit 0 with `state:needs_revision`.

Inspect requires exactly one of request, packet or audit selection. Detail inspection returns historical intake outcome and current linked response/task state separately. An old pending receipt does not become a new receipt when mapping later succeeds. Use `--packet` for a prepared assignment that never received a submission; use `--audit` for bounded metadata-only history.

After a submission, return compact next-action hints so the coordinator need not call a model merely to fetch counters. Do not automatically prepare, dispatch, render, retry or reconcile.

## 7. Packet and response contracts

### 7.1 Packet version 2

Retain the existing manifest fields: packet identity/version, base revision, mode, targets, read set, membership guards, source-context digest and write scope. Ordinary `get` emits version 2 with its established non-controller payload and command permissions. `work prepare` adds a coordinator-only `work` object:

```text
audit_id, mode, context: {owner, argument},
units: [{id, task_ids, prerequisite_unit_ids}],
tasks: [{id, target, kind, role, action, prerequisite_ids,
         consumed_inputs, membership_guards, draft_refs}],
conditional_on_task_ids, limits, size
```

Use the task fields/types from section 4; references in the manifest are pinned wherever a version is required. `consumed_inputs` records the original version plus the existing named facet/digest needed by that task. Unit/task arrays retain assignment order. `size` reports unique records, source excerpt bytes and exact serialized worker bytes. Do not add another version number for this object.

For primary work, the task list is an exact authorization list: `(audit, target, kind, role, action)`, including source-comparison actions. A supplier supplied as context is not another permitted target. Extend creation validation as well as replacement validation; the current major-owner scope expansion cannot enforce this boundary. Coverage is limited to assigned argument contexts and supplied anchors. Findings may target assigned structures and their supplied inputs; any affected use/check must be in that context. All structural relationships still pass existing validators. Independent discovery instead retains its source-based review/mapping scope, without requiring primary task IDs.

Prepare local context directly through indexed relations. Include all joint premises and complete selected excerpts. Ordinary use supplies the exact supplier statement, substitutions and scope, without its proof; `proof_argument` explicitly includes borrowed proof. Do not assemble the whole owner and then filter it. Final composition legitimately needs its route's broader coverage and structural context. See the [packet closure rules](controller-handoff/packet-reader-design.md#3-local-closure-rules).

Persist the coordinator manifest and worker payload separately using the existing packet row/manifest and blob facilities. Primary workers receive the ordered task instructions and deduplicated evidence. Independent workers receive only the existing source-origin assignment and source material; they must not receive primary intermediate claims, group order, work states, conditions inferred by the coordinator, other reviewers' judgments or operational receipts. Their own preserved source-based response may support continuation without primary reasoning or coordinator diagnoses; this is continuation of the same review, not a new independent opinion. Task bindings remain in the coordinator manifest. Blinding checks inspect the complete emitted independent payload, including filenames, scaffolds and headings.

For independent preparation, validate the declared audit's existing qualification prerequisites. At submission verify that the actual reviewer matches the supplied valid qualification. Do not add repeated calibration calls per assignment.

Each accepted check retains its own semantic binding. Never bind it to the union of every other task in the assignment. When composition consumes checks created in this same submission, compute its binding against the complete prospective state, including those generated check IDs. Do not pretend those checks existed at preparation time.

Additional evidence cited by an individual result must come from its supplied, provenance-checked context and enter that result's binding, including rebase comparisons. It does not automatically become every sibling check's input. New/unprovided evidence requires explicit source registration/context preparation; the adapter never fetches it implicitly.

Existing source-context review requirements remain in force. This revision does not remove the database-wide source-context digest. Comparing its metadata need not load all source bodies. Historical version-1 packets keep their original semantics and bytes; they do not acquire invented task metadata. Generic `get --extend` keeps its existing behavior. Reject that command for work packets in this slice because its current rebuild would erase task scope; refine/acquire the required context and prepare a replacement work packet instead.

### 7.2 Coordinator envelope

Define a closed `WORK_SUBMISSION` schema with every field present:

| Field | Type and rule |
|---|---|
| `contract_version` | Literal `3`; existing record contract remains unchanged |
| `request_id` | Nonempty opaque ID for this logical input |
| `packet_id` | Original packet the worker saw; must match the response |
| `rebase_packet_id` | Fresh compatible work packet ID or null; section 8 defines its restricted use |
| `reviewer` | Nonempty coordinator-supplied reviewer identity |
| `qualification_id` | Existing qualification ID for independent work; null for primary/reconcile |
| `exposure` | `source_only` or `compromised` for independent work; otherwise null |
| `exposure_note` | String; nonempty for compromised exposure |

Infer audit and mode from the stored assignment. The worker cannot override its role or provenance. These are coordinator attestations under the existing trust model, not authentication of a provider account by this script. Preserve the independent worker's separate exposure report and apply existing compatibility rules to both accounts.

### 7.3 Primary worker response

Define one closed root shape:

```json
{
  "packet_id": "original-packet-id",
  "results": [],
  "coverage": [],
  "findings": []
}
```

All three arrays are required. At least one proposed result, coverage span or finding is required; an empty response returns `NO_WORK` without a mathematical commit. Omitted tasks remain unfinished. Duplicate result task IDs are invalid.

`results` is the following tagged union. Every listed field is required; scaffolds fill identities and null placeholders.

| Variant | Fields |
|---|---|
| Check | `type: "check"`, `task_id`, `state`, `outcome`, `reasoning`, `evidence_refs`, `conditions`, `next_action`, `replaces`, `supersedes` |
| Source comparison | `type: "source_fidelity"`, `task_id`, `result`, `note`, `evidence_refs` |

Check fields use the existing body types: state `draft|complete`, existing outcome enum or null, string reasoning, anchor IDs, nonempty-string conditions, and string-or-null next action. A complete result requires a non-null outcome and nonempty reasoning. `replaces` and `supersedes` are pinned check references or null. A replacement must name a packet-listed current draft for the same task and reviewer; use its exact version and preserve any existing `supersedes` link in that draft. A correction of completed evidence creates a new check with an explicit `supersedes` reference, which may itself be saved as a draft. Do not silently select one of several drafts or replace a completed judgment. Newly authored checks receive generated IDs, audit, target, kind, role, reviewer and protocol from trusted context.

Source comparison uses the existing observation values `matched|needs_attention`, a string note and anchor IDs. It does not use mathematical outcomes or manufacture a proof check. Generate its target/reviewer from the task and envelope.

Coverage entries are explicit authoring input:

```text
argument_id, anchor_id, start_offset, end_offset,
classification: substantive|structural,
claim_refs: [Ref to items/parts],
check_task_ids: [ID], existing_check_refs: [PinnedRef to checks],
replaces: PinnedRef to coverage|null, note: string
```

Offsets retain the current half-open Python Unicode-character convention. Map `check_task_ids` to check results explicitly included in this response, never observation tasks; resolve existing pinned references without silently updating them. Generate the body `check_ids`. Preserve existing span, overlap, claim and structural-coverage validation. The controller does not infer coverage from a completed task, a source excerpt being present or a fluent explanation.

Finding entries create ordinary open findings:

```text
target: Ref, category, description, evidence_refs: [anchor ID],
related_task_ids: [ID], existing_check_refs: [PinnedRef to checks],
affected_uses: [use ID], impact_reason: string
```

Use existing categories `presentation|proof_gap|dependency_mismatch|statement_refutation|inconclusive`. Map related task IDs to this response's generated checks. Generate ID, audit, `lifecycle: open` and `resolution: null`; do not infer a finding automatically from a negative outcome. Finding resolution stays an explicit coordinator operation through the established edit path.

If a worker notices a missing dependency, it records the issue in a draft/next action and, where useful, a source-backed finding targeting the existing argument/group. The coordinator registers the missing item/use and prepares current work. Do not add a second discovery queue or allow the primary adapter to create graph nodes.

### 7.4 Independent and reconciliation responses

Independent workers keep the existing closed `WORKER_RESPONSE` shape:

```text
packet_id, covered_targets, coverage_note, exposure_report, judgments
```

Each judgment retains its existing `Ref|SourceTarget`, kind, state, outcome, reasoning, evidence, conditions, next action and supersession fields. The coordinator wraps unchanged worker bytes with section 7.2's envelope. Reuse the independent planner, mapping and acceptance rules; do not force independent discoveries into the primary task outline. A source-based identity needing mapping is valid pending evidence, distinct from malformed output.

For `mode: reconcile`, the coordinator supplies the existing `BATCH` response shape (`contract_version, request_id, packet_id, edits`) through the existing reconciliation validation profile. Its request/packet identity must agree with the envelope. This preserves the existing scientifically authored comparison and successor-check behavior without another response language. Direct existing review/map/reconcile commands remain supported.

## 8. Atomic registration, partial work and recovery

Implement the [submission design](controller-handoff/submission-design.md), including its proposed DDL and transaction seam. Its operational column named `role` records assignment mode (`primary|independent|reconcile`), not the two-valued `checks.role`. Do not copy a reconciliation mode into a check's role.

### 8.1 Two bounded transactions

1. Read each file once under its byte limit. Validate the envelope shape and compute the logical digest from canonical envelope plus the SHA-256 of exact worker bytes, before generating any record IDs.
2. In a short writer transaction, check for an identical existing request first and return its terminal receipt even if current provenance has changed. Reject a reused ID with different input. For new intake, check the global commit request-ID namespace and supported packet/audit/provenance, then preserve the original envelope/response blobs and insert one `received` index row. Freshness conflicts are tested after intake, so an old packet does not lose its response.
3. Interpret the retained response. In one writer transaction, revalidate mutable prerequisites, expand mechanical fields and validate the complete prospective record state through the shared acceptance kernel. Commit mathematical records and the terminal submission receipt together.
4. On a known malformed/conflicting proposal, commit no mathematical edits; finalize its retained diagnostic separately, checking that another caller did not already complete it. On interruption or unexpected transient failure, leave it `received` for explicit replay.

Extract a transaction-owned acceptance helper; do not nest existing accepting commands or duplicate their validators. Allocate the next mathematical revision under `BEGIN IMMEDIATE` as `COALESCE(MAX(revision), 0) + 1`. Construct the final immutable receipt, insert the commit first, then versions, heads, references and bindings in their required order, then finalize the operational row before commit. Intake alone allocates no mathematical revision.

Introduce the narrow internal `work_primary` validation profile: create primary checks, observations, coverage and findings; replace only authorized own drafts and pinned coverage; retire nothing. Existing `apply` and `compare` cannot simply be called sequentially because a mixed response must be atomic. Reuse their existing body/reference checks within this profile.

An accepted draft or a completed defect is an accepted submission. Neither implies theorem support. `needs_revision` can have a mathematical receipt for a valid independent response staged for mapping. A malformed included judgment instead rejects the included batch as a whole. Never silently discard malformed entries and credit the remainder.

### 8.2 Continuation and freshness

Save an explicit subset without requiring the entire assignment to finish. Return remaining task IDs and current next actions. A later preparation includes saved drafts and the current context for remaining work.

If reasoning was already produced under an older packet, retain its original response and packet ID. A new envelope may name `rebase_packet_id` for freshly prepared acceptance context. This is a new request, not an identical retry. Compare original task-level mathematical facets, source context and required memberships atomically with the fresh context before using its write expectations. Require compatible audit/mode and the same obligations referenced by this submitted subset, not equality of both complete assignment lists. Fresh preparation can omit tasks already saved, but must authorize every included edit. Preserve both packet identities in provenance and the receipt.

Cosmetic captions or unrelated progress can be rebound without fresh mathematical reasoning. An upstream proof repair changes derived support but does not stale a local application that consumed only the unchanged statement. A changed consumed statement, substitution, scope, group membership, borrowed proof, or prerequisite judgment actually consumed by composition requires reconsideration. No blanket exemption covers writes made by the same assignment/coordinator.

Keep the generic non-controller raw-version acceptance path strict. Apply this reuse behavior only where the explicit task-level comparison exists. Existing source-context changes still need the established source-review/reuse treatment; do not declare every unchanged excerpt automatically reusable.

### 8.3 Inspection and backup

`inspect` distinguishes the original submission receipt from current task/independent-response state. Mapping later accepted evidence does not rewrite the old intake receipt. A `received` request can be replayed unchanged; terminal requests return the original result. Corrections and deliberate new attempts use new IDs. Move existing successful mapping replay lookup before current response-state rejection.

Add bounded metadata-only `work inspect DB --audit ID [--limit N] [--cursor TOKEN]` as a history form, mutually exclusive with request/packet detail. Return preparation and submission IDs, revisions, modes, linked outcomes and next cursor. Load payloads only for detail inspection. This is history discovery, not a task ledger or claim that a worker is currently running. The coordinator checks its host's worker state before reassigning; `--exclude-task` communicates active assignments to preparation.

SQLite backup is the only recovery transport required here. It preserves commits, packets, all receipts and blobs. Existing mathematical JSON export is not a native controller-state backup; its history option adds record versions, not an operational restore facility. Do not build a new archive/restore subsystem. Report actual database format in exports and verify backup reopening, pending replay and receipt/blob integrity in fixtures.

## 9. Compatibility and migration

| Identifier | Before / after | Location and change rule |
|---|---|---|
| Native storage format | 2 / 3 | DB metadata and DDL; adds intake table and packet-version constraint support |
| Record contract | 3 / 3 | Existing mathematical bodies and batch contract; no new mathematical collection |
| Packet format | 1 / 2 | Each stored manifest/payload/row; new task metadata and local assignment support |
| Reader projection | 1 / 2 | Projection payload/renderer; adds derived worklist and precise task links |
| Review protocol | `item-audit/1` unchanged | Audit/qualification/check records; workflow clarification does not change mathematical review requirements |
| Overview format/schema | Unchanged | Separate overview interchange identifiers; never interpret “schema 2” as native storage format 2 |
| Core/skill release version | Acceptance-gated | Bundle manifest and skill metadata; update only after integrated evaluation and release decision |

New databases use format 3. Support reading formats 2 and 3; require format 3 for writes. Opening a database does not migrate it. The explicit migration first makes a non-overwriting SQLite backup, detects intervening writers, then changes metadata/tables atomically. Rebuild the packet table using SQLite's supported table-rebuild procedure to permit versions 1 and 2 while preserving all old rows/blobs and foreign-key references. Restore foreign-key enforcement and check integrity on every path. See the [migration sequence](controller-handoff/submission-design.md#6-storage-2-to-3-migration-and-compatibility).

Migration creates no mathematical commit, fictitious input receipts or fresh qualification. Format 3 migration is an idempotent already-current response; unknown/newer formats fail clearly. Existing overview/legacy converters continue their documented conversions into freshly initialized latest-format stores.

`insert_packet` must persist the validated manifest's actual version instead of always writing the compiled default. New `get` and `work prepare` emit version 2. Old version-1 packets remain inspectable and usable by their supported legacy commands; `work submit` requires a version-2 work assignment. Projection readers explicitly support 1 and 2, or identify unsupported versions before rendering. Neither reader fabricates missing worklist data for projection 1.

## 10. User workflow and reader behavior

Ship one concise coordinator workflow with the installed database lane:

1. Read the manuscript and register source-linked major items, meaningful intermediate claims, scopes, uses and joint/case groups. The coordinator chooses boundaries and reviews inventory completeness.
2. Ask for the derived worklist, choose the next scientific focus, and prepare one coherent assignment. Use several model calls only when independent context, argument boundaries or size limits require them.
3. Dispatch the worker payload through the host's available model/subagent tool. The controller does not own that call.
4. Submit the unchanged response with the coordinator envelope. Save partial reasoning. For formatting errors, use returned field diagnostics; another scientific review is unnecessary unless the meaning/input changed.
5. Interpret findings, refine the graph/source where justified, then prepare current remaining work. Reuse unaffected judgments.
6. Obtain independent review and explicit reconciliation as required. Render at meaningful checkpoints. Report examined scope, unresolved work and mathematical support separately.

Provide a complete small graph fixture, the [response example](controller-handoff/example-primary-response.json), envelope example, partial-save example, malformed-output repair and stop/resume transcript in installed references. Development architecture files must not be required at runtime. Keep legacy instructions in their own lane so the coordinator does not perform both old ledger paperwork and new database entry.

The major-node Archify graph remains the overview. Its lower reader exposes intermediate claims and individual checks on a selected connection, and whole-route composition on a selected result. Add a read-only worklist that links to those exact locations. Display local judgment, upstream support and work state separately: a locally valid use can have unresolved overall support. Do not turn receipt states or completed task counts into green proof colors.

Keep the HTML a labelled snapshot with no worker dispatch or database mutation. The G6 lazy-reader improvement can be delivered separately after this controller slice; it is not justification for a new browser application. Browser acceptance still requires actual visual inspection of the installed reader.

## 11. Implementation order and completion gates

Use the existing C0-C5 phases; do not create a parallel numbering system. A programmer may split commits internally, but each phase must leave a reviewable integration point.

| Phase | Concrete deliverable and owning modules | Required exit evidence | Earlier mapping |
|---|---|---|---|
| C0 | Freeze these DTOs/fixtures; add storage-3 schema, explicit migration and compatibility; synchronize architecture, handoff, record reference and protocol wording | Old record/packet hashes and receipts unchanged; rollback/backup checks; closed-schema rejection examples | R2 / P1 |
| C1 | Correct effective scope/exact establishment in assessment; implement pure task/unit derivation and selection in `work.py`; share with status | Focused/Full omissions reopen work; local intermediate order; cycles bounded; one coherent multi-unit assignment | G1/G2; R3 / P3 |
| C2 | Implement local version-2 closures, task bindings, creation whitelist, worker scaffolds and source-only bounded independent scope | Group packet size independent of unrelated siblings; every joint input present; no primary outline leaks; complete-unit overflow | G3; R2-R4 / P1/P3/P4 |
| C3 | Refactor acceptance transaction seam; implement receipt intake/adapters/partial saves and explicit rebase in `controller.py`; reuse review planner | One response atomically saves observations/checks/coverage/findings; exact replay; crash recovery; semantic conflict versus cosmetic edit | G4/G5; R3-R4 / P3/P4 |
| C4 | Wire CLI and read-only history/worklist projection; ship concise installed workflow/examples; regenerate both bundles | Installed-only chain plus interrupted/draft recovery; precise reader links; compatible overview lane and bundle identity | G2/G7; R5-R6 / P5/P6 |
| C5 | Run integrated behavior/scaling/regression fixtures, then bounded live mathematical pilot and browser acceptance | Separate software correctness, scientific checking, authoring cost, model calls and remaining scope | R7 / P7; R8 release still gated |

C1 and C2 may be developed in parallel after C0 fixes interfaces; integrate their task bindings before C3 accepts work. C4 documentation can be drafted earlier but must be rehearsed using the final installed commands. Migrate copies during development, preserving the real audit store. Do not bump release metadata merely because automated tests pass.

### Required behavior fixtures

| Scenario | Assertion that matters to the user |
|---|---|
| One coherent argument | With supplier prerequisites examined, one prepare/submit round saves source comparison, two applications, joint derivation and final composition as five addressable observation/check records, plus explicit coverage; no per-record dispatch required |
| Same-assignment successor | Seed expands beyond the initially ready frontier into its local successors; all outside prerequisites are examined or explicitly provisional |
| Upstream gap | Lower derivation owns the gap; higher use is checked against its exact statement; examined work is not scheduled forever and global support stays qualified |
| Exact scope | Missing consumed establishment, a newly registered Full result and a parent incorrectly covered by its child each prevent false completion |
| Cases and cycles | Required cases/alternative routes remain visible; genuine internal unit cycles are detected before contraction; projection-only cycles do not block work |
| Local context | Adding 1,000 unconsumed sibling groups does not enlarge selected group records/worker bytes; supplier proof appears only for explicit proof borrowing |
| Mixed submission | Included observations, drafts, complete checks, coverage and findings commit together; one invalid entry gives exact array/field diagnostics and no mathematical commit |
| Exact authority | A validly shaped check against an unassigned same-owner target is rejected; a context supplier is not authorized merely because its body was supplied |
| Partial save | Save two checks, interrupt, inspect, prepare the remainder and finish without restarting unchanged reasoning; omitted tasks remain unfinished |
| Replay and crash | Crash after intake or around final commit, retry with the same ID, and obtain exactly one mathematical receipt; changed bytes under that ID fail |
| Freshness | Caption/progress changes avoid new mathematics; changed consumed scope/statement/group/input judgment conflicts; local bindings survive an unrelated upstream proof repair |
| Independent review | Source-origin part within parent scope is assignable; malformed output stays retained; pending identity maps gain no premature credit; map replay returns its original receipt |
| Limits and history | Oversized context is not truncated; unfinished traversal never claims completion; preparation can be found after a crash before submission |
| Migration and recovery | Packet-1 bytes/receipts survive migration; SQLite backup resumes retained work; mathematical export makes no controller-restore claim |
| Installation and reader | Both generated cores match source; installed-only workflow avoids development docs/legacy forms; worklist opens the exact lower-reader task |

Use real small database fixtures through public commands for the integrated slice. Supplement with focused unit tests for pure ordering/selection and adversarial transaction faults. Assert semantic record/receipt effects and rows/bytes, not particular private helper names or elapsed-time thresholds. No live model provider is needed to prove batching and bookkeeping; live reasoning is a separate evaluation.

Extend existing new-format vertical/race/scaling tests where they already cover the relevant behavior. Add focused controller tests rather than duplicating every legacy fixture. Run the relevant new-format, reader, installer and bundle gates on the final integrated tree. Broaden legacy testing when shared/legacy behavior changed or a regression warrants it. Record exact commands, identities, skips and results; never substitute an old passing report for current evidence.

### Two-hour live pilot

Use a realistic short chain with a joint inference, meaningful hidden claim, upstream defect, incomplete response and restart. Let the coordinator build/refine the graph and dispatch checkers. Measure source/graph authoring, fresh mathematical reasoning, formatting corrections, conflicts, controller time and report time separately. Count model calls and obligations per assignment; identify any call spent only retrieving bookkeeping or repeating unchanged mathematics.

The pilot succeeds as workflow evidence when it can preserve and resume work, localize defects and explain its remaining scope without manual database repair. It is not a guarantee of mathematical completeness or faster reasoning on every paper. Stop at two hours and record unfinished work. Fresh independent mathematical review, the forward evaluation and real-browser acceptance remain explicit release evidence. Only then make the R8 distribution/version decision.

## 12. Scope boundary for the implementer

The controller delivers four tool operations over one graph database. Its durable additions are one small submission index and versioned assignment metadata. Scientific plans remain coordinator prose; scientific decisions remain source-linked records and judgments.

Do not add provider adapters, background loops, autonomous retries, queues/leases, persistent task mirrors, automatic graph extraction, new proof-status enums, generic cycle approval, native JSON restore or another reader application. If a later requirement needs one of those, bring it back as a separate design decision. The completion criterion for this revision is that the coordinator can efficiently direct coherent mathematical work and recover its results using the small tool surface above.

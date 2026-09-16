# Task derivation and coherent assignment proposal

Implementation detail, September 15, 2026. No production change. [The controller implementation plan](../controller-implementation-plan.md) owns interfaces, assignment policy and limits; this document supplies task-derivation details under that contract.

The controller reads accepted graph records and saved judgments. It never adds a mathematical dependency, chooses which proof is scientifically preferable, or decides that an unproved assertion is acceptable. The coordinator retains those decisions.

## 1. Three distinct objects

1. An **obligation** is one fine-grained examination, with the existing ID from `obligation_id(audit_id, target, kind, role)`. Examples are an application check, group derivation, source-fidelity observation and final composition.
2. A **work unit** groups obligations that should share one complete context. A group unit includes its application obligations, derivation and required case/discharge checks. Composition, source fidelity, ungrouped application, external-source verification, global tasks and reconciliation may form standalone units. Units are derived, not stored as another ledger.
3. An **assignment** is an ordered selection of compatible units for one role and local argument context. Its ready frontier is a starting point. Downstream units may join when their external prerequisites have been examined and their unfinished internal predecessors are included earlier in this assignment.

Thus one primary model call can return application checks, the corresponding group derivation, later local group checks and final composition. Five units does not mean five check records. A unit has indivisible context, but a response may explicitly submit only some assigned obligations; current completed members are not needlessly checked again.

## 2. Proposed derived interfaces

No function below writes a record, calls a model, changes scope or consumes an outcome as a scientific instruction. Snapshot/view arguments represent one fixed database revision. All results are ordinary serializable data.

```python
def derive_scope(graph: GraphView, audit: Audit, limits: TraversalLimits) -> ScopeView: ...

def derive_task_graph(
    graph: GraphView, scope: ScopeView, assessment: AssessmentView
) -> TaskGraph: ...

def derive_units(graph: GraphView, tasks: TaskGraph) -> UnitGraph: ...

def select_assignment(
    work: WorkView, request: PreparationRequest, limits: WorkLimits
) -> Selection: ...
```

Reuse a single graph/scope view and the shared assessment result within one request. `assessment.py` owns scope and obligation enumeration; enumeration does not depend on evaluated task states. Assessment evaluates those obligations, and `work.py` derives their ordering, units and selection. The public `list_work` and `prepare_work` entry points use this same sequence. Status, projection and release must not implement competing definitions of completion.

`PreparationRequest` carries the implementation plan's `mode`, `focus`, ordinary `task_ids`, `exclude_task_ids`, `max_units`, `max_bytes` and `allow_provisional` fields. Explicit task selection expands to a complete context unit. Unit IDs remain derived receipt/selection identifiers, not a second public authoring interface.

### Ordinary task row

Every row has exactly these fields. Ref/PinnedRef retain their existing meanings. Arrays are deterministically ordered and duplicate-free.

| Field | Type and meaning |
|---|---|
| `id` | Existing obligation ID |
| `target` | Ref of the exact check/observation target |
| `owner` | Major-item Ref or null for audit/global work |
| `argument` | Argument Ref when directly applicable, otherwise null |
| `kind` | Existing obligation kind, including `source_fidelity` and `reconciliation` |
| `role` | `primary`, `independent` or `coordinator` |
| `action` | `check`, `compare_source` or `reconcile`; determines the response scaffold |
| `required` | Whether this examination is required in the effective audit scope |
| `state` | `ready`, `waiting`, `needs_coordinator` or `satisfied` |
| `prerequisite_ids` | All ordinary ordering predecessor obligation IDs |
| `waiting_on` | Unsatisfied ordering predecessor IDs at this revision |
| `blocker_ids` | IDs of structural/source/provenance diagnostics that prevent ordinary preparation |
| `judgment_refs` | Current and relevant historical PinnedRefs from shared assessment, not a duplicated judgment body |
| `draft_refs` | Active saved draft-check PinnedRefs |
| `next_action` | Saved draft next action verbatim, or null; selection among drafts uses stable revision/ID order |
| `outcome` | Shared assessment outcome or null; never synthesized by the scheduler |
| `freshness` | Shared assessment freshness or null |
| `dependency_support` | Existing dependency support value or null where not applicable |

Audit ID and revision belong once in the response envelope, not repeated in every row. Labels are resolved from the existing target records for presentation. `waiting_on` is redundant only as a convenient bounded projection of `prerequisite_ids`, never independently editable.

Coordinator diagnostics are a separate `coordinator_actions` array, not fake mathematical obligations. Each contains `id`, `code`, `target_refs`, `related_task_ids`, `message`, and `required`. IDs hash audit ID, code and stable target identity. Missing establishment and unresolved Full inventory coverage are required coordinator work and block completion; a detected cycle is an ordering diagnostic, not an automatic mathematical rejection. Do not add a `cycle_approved` record type.

### Work-unit row

```text
{id, kind, role, argument, owner,
 obligation_ids, pending_obligation_ids, predecessor_unit_ids,
 blocker_ids, state}
```

Group IDs are derived from audit/role/group identity. Standalone unit IDs are derived from the obligation ID. Unit state is satisfied only when all required member examinations are satisfied. A unit may retain completed members in context while scaffolding only its pending members.

## 3. Scope and exact establishment

### Scope traversal

Use iterative traversal with visited sets and reference indexes. Retain the source/use/argument that caused each inclusion, so the coordinator can inspect why a prerequisite is required.

- **Focused:** begin with coordinator-selected roots and their requested parts. Follow the registered routes, group inputs and actual `uses.from` references. Include prerequisite establishing work recursively. Include relevant scope statements and source context.
- **Full:** reconcile the current typed proof inventory in this paper with explicit exclusions. Newly registered in-scope results enter required work or create an explicit scope-review diagnostic. Do not treat the absence of a target-list update as an exclusion.
- A parser candidate is not an accepted item. The controller does not infer proof-required declarations from arbitrary text or certify inventory completeness from parser output.
- An assumption explicitly in force in the current scope is context for that application. Do not recursively demand its proof for that application. Check exact recorded identities and scope ancestry; do not infer implications from strings. A claim assumed locally may still require proof when consumed elsewhere without that assumption.
- Definitions require their recorded source/context work. External results require source verification and their actual applications, without an invented local proof. Separately registered arguments remain accountable under the existing audit rules.
- Preserve all registered required routes and written coverage in the effective scope. Draft or optional material does not become a required mathematical route merely because it shares a major owner.

The traversal needs context-sensitive assumption stopping: visiting a claim once as a local assumption must not suppress a later visit that requires its establishment outside that scope.

### Establishment lookup

Look up `arguments.target` and `groups.conclusion`, with registered owning arguments. Do not test whether the owner's aggregate family contains any argument.

- A required major theorem/result needs its own registered complete route and final composition. An argument for one of its intermediate claims is insufficient.
- An intermediate can be established by a group inside its parent's argument. It need not own a separate argument.
- A theorem part may be covered by the whole parent argument and its final composition, or have a separately recorded establishing group/argument. Do not require redundant part arguments simply because parts are separately addressable. The whole-result composition consumes the current parts membership and exact statements.
- When a part/intermediate is used within that same parent proof before final composition, its recorded local establishing group supplies its ordering predecessor. Do not mechanically make every local use wait for the enclosing argument's final composition. If no local establishment is recorded, return the missing-establishment/cycle context to the coordinator rather than inventing it.
- For a consumed proof-required claim with no establishment, emit `register_establishment` naming that claim and its uses. If the paper supplies no justification, the coordinator represents that omission and records the appropriate examination. The controller does not manufacture an input-free proof on its own.

## 4. Examination state and dependency edges

Use the shared assessment's `satisfied` decision. An active current completed gap, refutation or inconclusive judgment counts as examined. A draft, stale judgment, compromised independent response or unresolved conflicting judgment does not. The worklist must not independently redefine these rules.

Scheduling dependencies express the ordinary examination order, not a logical proof of the conclusion:

| Obligation | Ordinary predecessor examinations |
|---|---|
| Source fidelity | No mathematical predecessor; required source/context must be available |
| Application | Relevant required source comparisons; the supplier's required primary establishment/source-verification examinations, except an explicitly assumed premise |
| Group derivation | Its member applications and relevant source comparisons |
| Case/discharge check | Required input examinations and the explicitly recorded case/scope context; no extra inferred cases |
| Final composition | Required local groups, their case/discharge examinations and exact target/part comparisons; written coverage is required context/output, not already-completed predecessor work |
| Independent review | Dispatch/provenance/source requirements, not a dependency on primary outcomes |
| Reconciliation | The particular primary and accepted independent examinations being reconciled |
| Applicable global check | Coordinator-selected scope/context and recorded protocol requirements; no invented dependencies on unrelated tasks |

For a supplier established by an internal group, its group examinations are predecessors; the enclosing argument's final composition is not automatically one. A separately registered route to that supplier contributes its own composition examination. Do not select the most favorable alternative route to make a task ready. Preserve the declared audit work; explicit provisional assignment remains available.

Every edge must be attributable to an accepted reference, recorded route/scope relation or existing audit requirement. Neither statement similarity nor a model-independent interpretation of the prose creates an edge. Primary work does not wait for independent review by default.

No incoming uses is not completion. An input-free group still has a derivation obligation. Its argument still has final composition. An empty task set caused by absent structure yields a diagnostic, not `all([])` success.

State precedence for unfinished tasks is: an unavailable required source/record/provenance input yields `needs_coordinator`; otherwise unfinished ordering predecessors yield `waiting`; otherwise `ready`. Satisfied tasks remain satisfied when nothing relevant changed. Repeated assignment does not reopen a completed negative judgment.

## 5. Group contraction and coherent batch growth

### Contract obligations into units

Place a group's application, derivation and required case/discharge obligations in one unit for each role. Keep standalone composition/fidelity/ungrouped-application/external-source/global/reconciliation obligations in their own units.

Detect strongly connected components, or use equivalent finite cycle detection, on the detailed obligation graph **before contraction**. Retain the precise implicated task/use/group/route references, including cycles entirely inside one proposed unit. Evaluate ordinary readiness on unfinished ordering predecessors; an already satisfied examination is not a scheduling wait. A retained within-unit cycle among unfinished obligations requires explicit provisional selection and must not disappear when self-edges are removed.

For every obligation edge `predecessor -> successor`, add the corresponding unit edge only when the unit IDs differ. Remove self-edges and deduplicate edges. Applications preceding derivation inside one group must not make that unit wait on itself. Keep the internal obligation ordering for the scaffold.

Derive unit readiness from its external predecessor units, retained internal cycle diagnostics and hard blockers. Do not copy the most restrictive member-task state: an acyclic derivation waiting for applications inside the same unit can be included with those applications.

Compute cycle candidates on the detailed task/unit relationships, not the major-owner display graph. A cycle in scheduling dependencies is not automatically circular mathematics; report the exact route/group/use references. Avoid merging entire major owners or alternative arguments into one scheduling unit, which would introduce spurious dependencies.

### Compatible local context

The normal mathematical batch has one role and one registered argument. It may include:

- group units in that argument;
- that argument's final-composition unit;
- source-fidelity units needed for those groups/target, ordered before dependent units.

A fidelity task may serve several arguments without being duplicated. Its placement in an assignment is derived from the argument context using it; its identity and saved observation remain singular. It cannot pull a supplier's entire proof argument into the consumer's assignment.

Independent, reconciliation and global assignments use their existing role-specific contexts. Never mix primary and independent work. Independent worker payloads must not expose primary unit/group identities or coordinator diagnoses merely because the coordinator's internal selection uses them.

If one assignment includes primary source observations and mathematical checks, the submission adapter must validate and commit the explicitly included edits atomically through the shared engine. Do not secretly split it into separate compare/apply transactions.

### Deterministic selection

1. Recompute the selected snapshot's work. Defer any unit containing a pending obligation that the coordinator declares already assigned. Retain that predecessor in downstream readiness; do not remove it from the task graph. This default avoids overlapping group assignments and is a suggestion filter, not a worker lease.
2. Choose a ready pending seed that works toward the explicit focus, including an unfinished external prerequisite when necessary. Use source position then stable identity as tie-breakers. No score for scientific importance is inferred.
3. Fix its local argument/role context. For a source-fidelity seed, explicit argument focus wins; otherwise choose the deterministic compatible argument context recorded by the task graph. A standalone source task with no such context remains standalone.
4. Add a compatible pending unit only if it has no hard blocker and every unfinished predecessor unit is already selected earlier. Satisfied predecessors are already examined even when their outcome is negative. This grows from the ready frontier into downstream work.
5. Repeat in deterministic order until the unit cap or serialized context budget would be exceeded. Composition may therefore follow included groups in the same assignment.
6. Deduplicate context before measuring. If a later unit does not fit, defer that unit and its not-yet-included dependents, retaining the valid earlier selection. Do not split its group or remove one joint premise to make it fit. No knapsack search is needed.
7. If the first indivisible unit cannot fit, return `prepared:false` and a coordinator diagnostic with measured size and largest contributors, with no truncated worker packet.

Example: supplier work is already examined; group G has two applications, derivation and a case check; H uses G; C is final composition. One selection can be `[G, H, C]`, producing more than three fine-grained checks in one model call. If H also needs an unexamined external supplier outside this argument, H and C remain deferred; G can still be assigned.

Explicit provisional selection may waive named unfinished mathematical ordering predecessors. Record those waived IDs in the preparation receipt and retain conditional/unavailable support. It cannot bypass absent records, unavailable required source, qualification or blinding requirements. Do not silently convert an ordinary selection into provisional work.

A remaining cycle of unfinished scheduling predecessors has no ordinary topological frontier. Return its exact references and waiting reasons while leaving unrelated ready components available. The coordinator can refine the representation or explicitly select provisional local work. Neither “no ready unit” nor a cycle diagnostic is a completion verdict.

## 6. Limits and returned selection

Limits from the controller implementation plan:

| Limit | Default | Maximum/policy |
|---|---:|---|
| Worklist page | 20 rows | 100; snapshot-bound cursor |
| Assignment | 5 work units | Hard maximum 10 units; check count may exceed 10 |
| Serialized worker input | 131,072 bytes | Explicit requests up to 1,048,576 bytes; never silently enlarged |
| Unique packet records | 2,048 | Hard ceiling in this implementation |
| Snapshot traversal | 100,000 distinct records and 500,000 relation visits | Stop at either bound and report `analysis_complete:false` |
| Returned diagnostics | At most 100 | Include total count and truncated flag |

Inject traversal ceilings in tests; future increases require explicit configuration. Count relation visits, including repeated visits, rather than only unique edges so repeated work remains bounded. Do not use Python recursion depth as a graph policy. An incomplete traversal cannot assert scope completeness or produce work from a secretly truncated graph. It reports the exceeded bound and responsible context; it need not implement a resumable traversal protocol. Worker response and coordinator-envelope intake limits belong to the submission adapter and remain as specified in the main plan.

The public prepare result uses the main plan's `packet_id`, `revision`, `audit_id`, `mode`, `selected_unit_ids`, `assigned_task_ids`, `conditional_on_task_ids`, `deferred`, `size`, and `files` fields. The coordinator manifest retains local context, satisfied evidence references and detailed size counts without expanding that public contract. The worker receives only the role-appropriate assignment payload. Controller diagnostics and large manifests remain outside independent contexts.

## 7. Acceptance cases

1. **Chain:** source fidelity, a direct group and its composition fit in one argument assignment; the next argument's work becomes the next suggestion after acceptance.
2. **Contraction:** two applications plus derivation form one ready unit, with no self-edge. Saving only one application leaves the unit pending without repeating that completed check in the scaffold.
3. **Coherent expansion:** a seed group, downstream group and composition join one assignment when outside prerequisites are examined. They are not restricted to the initial frontier.
4. **Outside prerequisite:** an unfinished supplier in another argument prevents default inclusion of the dependent unit; it does not prevent unrelated ready units from being suggested. Explicit provisional selection names the skipped predecessor.
5. **Negative upstream:** current completed gap/refuted/inconclusive evidence satisfies examination ordering; support remains separately qualified.
6. **Zero inputs:** no incoming edges still produces group derivation and final composition; absent structure produces coordinator work.
7. **Exact establishment:** a child's argument cannot close the parent. A part covered by its parent or an intermediate established by a local group needs no redundant argument.
8. **Scope:** a theorem-only Focused request includes its actual internal prerequisites. Full inventory growth reopens required work. Explicit exclusions are retained visibly.
9. **Scoped assumption:** a claim assumed in one local scope does not create a proof prerequisite there; the same claim consumed unconditionally elsewhere still does.
10. **Cases/alternatives:** every joint input and required case remains present; separate written routes are not merged into a conjunctive scientific claim or discarded after one succeeds.
11. **Cycles:** actual task-cycle references are finite and actionable, including a cycle wholly inside one group before contraction. That unit is not ordinarily ready merely because contraction removed self-edges. Major-projection-only cycles leave ordinary work available. Provisional assignment does not imply mathematical approval.
12. **Caps:** five units can contain more than ten checks. Hard cap is ten units. Deduplicated context is measured before issuance; an oversized group is never truncated.
13. **Source before group:** a source-fidelity unit can seed a batch and precede its group/composition, with one explicit primary submission committing valid observations/checks atomically.
14. **Partial response:** valid included drafts/checks commit together; omitted tasks remain pending; any invalid included edit rejects that included batch without rejecting future corrected subsets.
15. **No double ownership:** a unit with an explicitly already-assigned pending member is deferred, and its unfinished dependents do not become ready by omission. This filter creates no persistent controller lease. After interruption, preparation is not misreported as dispatch or task completion.
16. **Traversal exhaustion:** record and relation-visit caps are separately exercised with injected small bounds. No truncated scope is labeled complete or used to generate apparently complete work; the response names the exceeded bound and responsible context.

These cases extend the existing G1 public-API counterexamples and task/packet tests. They should assert user-visible task sets, selections, evidence and completion behavior, rather than reproduce helper implementation details.

# Local packets and reader integration for the coordinator controller

Planning proposal, 2026-09-15. No production changes are made by this document. [The controller implementation plan](../controller-implementation-plan.md), particularly sections 1-6, owns commands, limits, assignment policy, and version decisions. Its packet-manifest specification owns final closed field names; descriptions below specify required behavior without introducing another contract.

## 1. Work units and assignments

An **obligation** is one fine-grained examination, satisfied through the existing check, observation, or reconciliation records. A **work unit** is one complete group together with its applicable application, derivation, case-coverage, and scope-discharge obligations. Composition, source fidelity, ungrouped applications, external-source verification, global work, and reconciliation can also be standalone units. An **assignment** is one ordered sequence of compatible units for a single role and local argument/result context. It contains at most five units by default and never more than ten. A source-fidelity unit can attach to that local context without duplicating its logical obligation. One assignment can legitimately produce more than ten fine-grained records.

Indivisibility concerns the context for a work unit. Never split a joint inference into packets containing different subsets of its premises. It does not require all checks in a unit or assignment to be submitted atomically: completed checks, drafts, and a partial subset remain useful saved work.

The coordinator model supplies and refines the graph. The controller orders recorded dependencies and selects existing work. It must not invent intermediate claims, choose an undeclared proof route, silently discharge a case, or infer that every predecessor must be established through the same alternative argument.

A composition unit may follow local group units in the same assignment when every prerequisite outside the assignment is satisfied or an explicitly permitted provisional boundary, and the required unfinished internal predecessors are included earlier in the assignment. It retains its own check identity and full composition context. Provisional preparation never makes a composition supported without the required actual support. If its context does not fit, return that unit to the coordinator rather than declaring the preceding local checks a complete proof.

## 2. Version-2 compatibility and exact task scope

Reuse the persisted packet, immutable manifest, canonical `records` table, and transaction-owned acceptance kernel. All newly prepared packets use version 2; version 1 historical packet bytes remain immutable and readable through the main plan's migration/version handling. Do not retrofit a task whitelist onto a historical generic packet.

Two version-2 packet uses remain distinct:

| Producer | Assignment metadata | Submission behavior |
| --- | --- | --- |
| Existing generic `get` | The `work` key is absent | Existing author/primary/source-only independent/reconcile behavior and generic `get --extend` remain available. These packets do not imply a selected controller assignment. |
| `work prepare` | Coordinator manifest contains `work` with ordered units, exact task authorization, and per-task semantic inputs | `work submit` uses the appropriate narrow acceptance path. A primary assignment uses `work_primary`; a generic `apply` must not bypass its task whitelist. |

Generic `get` remains the coordinator's source/graph authoring tool. Do not narrow its existing broad owner closure as an incidental consequence of implementing work preparation, and do not treat its role `primary` as proof that it is a task-scoped controller packet. New indexed local closure is selected by `work prepare`.

Use the main plan's single `work` object in the coordinator manifest. Do not introduce competing `assignment`, `task_scope`, or separate whitelist root fields. Its required information is:

```text
work:
  audit_id, mode, context: {owner, argument}
  units: [{id, task_ids, prerequisite_unit_ids}]
  tasks: [{id, target, kind, role, action, prerequisite_ids,
           consumed_inputs, membership_guards, draft_refs}]
  conditional_on_task_ids, limits, size
```

The manifest's existing base revision identifies its snapshot. Unit and task arrays retain assignment order. The `tasks` list is the authorization list; permitted results are derived from its unsatisfied selected obligations, not invented by the worker. A satisfied member of an included unit is prior work, not a newly assigned result slot. Source comparisons use their observation action, rather than being forced into a check-only whitelist. `consumed_inputs` pins the original versions and named facets/digests relevant to each task; `membership_guards` records its required memberships. Bodies and excerpts shared by several units occur once in `records`; units reference them. Derived boundary-support descriptions belong in the primary instructions, not an alternative authorization schema. The independent worker receives none of this primary task outline or internal `work` object.

The packet may contain a supplier as context without authorizing new judgments against every record of that supplier. The primary assignment writes its permitted result slots and associated findings through `work_primary` and the shared acceptance kernel. Do not make a second implementation of validation or mathematical completion. If the worker discovers a necessary graph change, it reports the change to the coordinator; the coordinator uses generic `get`/author/apply to refine records before preparing replacement work.

Changing only `TARGET_COLLECTIONS` is insufficient. Current creation scope in `validation._scope` expands item/part targets to their major owner, while `acceptance.accept` primarily limits replacements through `write_scope`. Extend assignment validation so new observations/checks also remain within assigned task/action/target/kind/role slots. Do not solve local targets by adding a paper-scoped target or exempting validation. Reject `work submit` for a generic packet with no assignment, and reject unsupported historical packet versions rather than guessing a whitelist.

For this first controller slice, retain generic `get --extend` unchanged for generic packets. Reject `get --extend` on a task-scoped prepared packet with an actionable instruction to obtain/refine the required source/graph context and call `work prepare` again. The current extension path re-enters broad `_build`; using it unchanged would erase the assignment boundary. A future prepared-packet extension would have to preserve audit, role, task whitelist, limits, original provenance, and task-specific extra evidence. It must not be implemented as an implicit generic extension.

## 3. Local closure rules

Prepare context using indexed relation lookups. Do not call `statement_closure` for the major owner and then filter its output.

| Selected material | Include | Do not expand automatically |
| --- | --- | --- |
| Group unit | Group body; all uses in that group; group conclusion; argument header and target statement; full required scopes, case scopes, and discharged scopes; explicit group/use evidence | Every other group, argument, part, or hidden claim owned by the same theorem |
| Each input use | Exact source and destination statements; needed form; substitutions; regime; application reason; scope; source passages that establish the statements | The supplier's proof, its other consumers, or all arguments that prove the supplier |
| Proof-borrowing use | All preceding material plus the proof/evidence passages explicitly borrowed by `type=proof_argument` | Other proofs of the same supplier |
| Scope | Scope body; parent chain; declared assumptions and their statement context; scope evidence | Unrelated scopes belonging to the same argument |
| Local source | Complete selected anchor excerpts; pinned source metadata; relevant source limitations/reviews | Every anchor or full source blob merely because it belongs to the same file |
| Prior assessment | Same-audit checks/findings relevant to selected targets; exact predecessors needed for explicit supersession/reuse | Every audit, qualification, review response, or history entry in the database |
| Composition unit | Argument target and parts; all structural material, coverage, scopes, uses, and evidence required by the current composition binding; relevant completed prerequisite checks | The theorem's other alternative arguments or its downstream consumers |

The owning major item is a label/navigation boundary, not a recursive retrieval instruction. Including its body does not require loading the excerpts behind every passage listed in that body. Supply a compact boundary description of source-only context not loaded; it must not be mistaken for missing evidence needed by the assigned inference.

For local primary units, load the selected audit rather than using the existing `finish()` loop over every audit and qualification. Include historical material only when a selected current record refers to it and it affects the work.

For same-argument ordering, derive edges from the registered conclusion/use relationships. Group units in one assignment stay within its local argument/result context and role; a source-fidelity unit may attach as specified in section 1. Respect recorded case/route structure. Return ambiguous producer/route structure to the coordinator instead of selecting a proof route implicitly.

## 4. Reuse existing source and binding semantics

The closest existing semantic specification is `bindings._Builder`:

- `statement()` includes statement/definition anchors and scope, then the parent item for a part.
- `borrowed_proof()` includes proof/evidence anchors for a proof-borrowing use.
- `use()` and `group()` bind the application/inference records and complete `uses_in_group` membership.
- `argument()` defines the broader context needed for composition.

Mirror these dependencies in local packet preparation. Keep each accepted check's binding computed by `compute_bindings` on the prospective state and constrained by its original prepared task inputs. Include any additional evidence explicitly cited by that result only in the corresponding task/check binding, after validating its original packet provenance. The assignment's union record table is a transport optimization, not the semantic input set of every check.

Composition may consume checks generated by earlier results in the same response. Bind it against the complete prospective state, including those new IDs; do not invent preparation-time versions for them or attach them to unrelated application checks. Use the task's recorded prerequisite relationship to distinguish these internal results from a previously saved judgment that the worker actually consumed.

Do not bind every check to every sibling unit, shared attachment, or upstream status record. Existing generic packets retain their documented read-set conflict behavior. Work submission must use the central plan's task-specific freshness rule for the submitted task set rather than deriving every check's inputs from the union packet read set. Explicit reuse follows its `rebase_packet_id` contract: retain the original response/packet, use a new request, compare the original task inputs and extra evidence with the fresh context, and require that fresh context to authorize every included edit. A real consumed input changing must still prevent acceptance against unread current content; a later accepted check must never be rebound silently to a newer source.

The current `packets._Closure.supplier()` claims not to load proofs but adds every passage's anchor. Correct this for the new local closure: ordinary statement use loads statement/definition passages, while `proof_argument` explicitly loads the borrowed proof. Preserve the existing source anchoring operations and anchor hashes. If an anchor is stale, missing, or too broad, return the problem to the coordinator. Register finer complete source anchors through `source anchor`; never trim an excerpt during packet serialization.

Keep the current packet source-context check for the first implementation. Relaxing its database-wide sensitivity is a separate change. Read only the source IDs/version/hash metadata needed for that digest, not all source bodies.

## 5. Local proof judgment and upstream support are distinct

A worker can conclude that a group is justified **under its explicit input statements** even when a supplier's proof is still unchecked. The worker must not promote that supplier to verified or hide it as an unstated assumption.

Return and display separately:

1. The saved local check outcome and reasoning under the declared premises.
2. Derived upstream availability from the existing assessment engine.

Default ordering waits for outside required examinations or includes their work earlier in the same assignment. Crossing an unfinished mathematical boundary requires explicit `--allow-provisional`; the assignment names those tasks in `conditional_on_task_ids`. Completed negative examinations do not cause an endless wait, but their support consequences remain visible. Provisional mode cannot bypass missing required source, absent/invalid graph records, qualification, or blinding. It is never permission to re-import the supplier's entire proof into every local task. A local supported judgment can coexist with an amber connection because upstream support remains unresolved. A known failed supplier must remain visible as such. Do not write an artificial extra mathematical condition merely to encode a pending upstream review.

When an input is produced earlier in the same assignment, the later unit can use that stated intermediate conclusion conditionally. If the earlier check fails, the later local implication can still be saved with precise premises; it cannot establish a complete supported route. Composition must examine the actual completed outcomes and all outside prerequisites.

Updating an upstream proof/check should update derived support without invalidating an otherwise unchanged local implication. Changing the consumed statement, substitution, scope, inference membership, or borrowed proof should affect the corresponding bindings. This is already the intended statement/proof facet distinction.

## 6. Bound preparation and output without losing evidence

Apply the implementation plan's fixed initial limits:

| Bound | Value |
| --- | ---: |
| Units in one assignment | At most 5 by default; explicit requests 1-10 |
| Serialized worker packet | 131,072 bytes by default; explicit requests up to 1,048,576 bytes |
| Unique packet records | 2,048 hard ceiling |
| Full snapshot analysis | 100,000 distinct records and 500,000 relation visits |
| Worklist page | 20 rows by default, at most 100 |
| Returned diagnostic rows | At most 100, with total count and truncation disclosure |

Unit count alone does not bound context. Count records once, use a visited set for scope/statement expansion, and stop preparation on budget overflow before creating a worker assignment. Bounded indexed membership enumeration should detect overflow rather than first loading an arbitrarily large closure. A stored body's byte length can be checked before materializing an oversized excerpt. Reject requests outside the permitted unit/byte ranges; do not clamp silently or retry with a larger budget.

Full analysis may be linear in the registered graph, within its declared ceilings. Reuse one snapshot/view per command. If analysis exceeds a ceiling, return `analysis_complete:false` and no completion claim; never select work from a silently truncated graph. A diagnostic-list truncation flag limits reporting only, not the mathematical context of a dispatched task. Traversal limits are injectable in tests.

Build the closure incrementally in assignment order. If adding the next complete unit exceeds a budget, emit the preceding complete units as one assignment and leave the next unit pending. If the first unit alone exceeds the budget, emit no partial packet and return:

```text
needs_coordinator:
  unit_id, target_ref, reason=oversized_context
  measured_or_lower_bound_bytes, unique_record_count
  largest_contributors: [{record_ref, bytes}]
```

The coordinator decides whether to refine graph/source boundaries, obtain missing context, or request an explicitly larger packet budget within the 1 MiB ceiling. Do not repeatedly prepare the same oversized unit unchanged. It remains incomplete, not mathematically failed. An ordinary blocked/oversized selection returns exit 0 with `prepared:false` and coordinator actions; malformed limit requests return exit 2.

After preparation, serialize the exact worker packet and verify its final byte count before persistence. Oversized worker outputs never carry `truncated=true` or a partial proof context. Prepared-packet context changes require coordinator action and replacement preparation as specified in section 2; they do not fall back to an unbounded generic packet.

The coordinator receives a compact assignment summary and packet path. The worker receives the deduplicated packet. Avoid printing the full packet in both places. Reuse the single assessment snapshot already computed for the worklist; packet preparation must not render the HTML report or derive full assessment again for each unit. Body lookup work should scale with selected context, apart from the small existing source-digest metadata scan.

## 7. Primary and independent privacy

Local ordered graph packets are for primary work. An independent worker must not receive the primary graph's intermediate items, group order, task/obligation IDs or outline, readiness/support labels, other reviewers' judgments, worklist reasons, or report links. Its own preserved source-based response can support continuation without coordinator diagnoses or primary reasoning; this is the same review, not another independent opinion. Assignment/task metadata used by the coordinator stays in the stored coordinator manifest, not the source-only independent worker payload. Do not serialize an internal assignment object into that payload merely because both are version-2 packets.

Continue using `_independent`, `blinding_violations`, the source-origin target restriction, and the existing review submit/map/reconcile paths. The controller can select an independent source target and apply size limits, but must not expose its primary work unit as the worker's outline. The independent worker identifies source-based judgments; mapping happens afterward. Do not build a new independent intake format for this controller change.

The existing independent packet can itself exceed budget. Return it for coordinator action with the same explicit oversized result. Do not opportunistically omit source assumptions to make it fit or relax the privacy rules. Any later optimization of source-only independent context requires its own completeness and blinding tests.

## 8. Worklist in the existing Archify reader

Add a compact, read-only pending-work list using the same derived worklist as the controller. Each row shows the owning result, a short task label, role, and readiness reason. Page it at 20 rows by default and at most 100, preserving snapshot/filter identity in its cursor. Expose a locator such as `{detail_key, section_key, obligation_id}` rather than asking the reader to interpret an opaque obligation hash.

Clicking a row selects the major owner and opens the exact obligation in the current lower reader. A hidden group/claim still does not become a visible graph node. Prefer its owning-result detail when a shared intermediate occurs on several edges; a worklist link must not imply that the first edge owns the only copy of the proof step. Add obligations to reader search so a copied obligation ID can be resolved.

Keep readiness labels separate from proof colors. `Ready for checking` is not green support; `waiting for context` is not a red mathematical defect. Display the snapshot revision and distinguish an empty ready list from a complete audit. Final composition, coverage, and independent-review work remain visible even when local connections are green.

The static HTML does not dispatch workers. No new dashboard, expanded graph, or execution service is needed.

## 9. Implementation order and measurable acceptance

Follow the main plan's C0-C5 phases, not a parallel implementation schedule:

- C0 fixes the version-2 generic/prepared fields and compatibility fixtures.
- C1 derives the units and same-argument ordering consumed by local preparation.
- C2 implements narrow closure, per-task inputs, exact authorization, deduplication, and overflow behavior.
- C3 integrates `work_primary` with the shared transaction kernel and the primary response adapter. The main plan's primary response example saves multiple observations/checks through one submission, including a partial return.
- C4 adds the read-only worklist and exact lower-reader links/search while preserving the Archify shell.
- C5 runs the following behavior cases alongside integrated acceptance, before any separately scoped report-materialization change.

| Case | Required evidence |
| --- | --- |
| Generic compatibility | A new generic version-2 `get` packet has no `work` key and retains its existing author/apply/extend behavior. Historical version-1 payloads remain byte-identical and usable by supported legacy commands. Generic `apply` cannot bypass a prepared task whitelist; `work submit` cannot reinterpret a generic packet as an assignment. Prepared `get --extend` is rejected with the replacement-preparation path. |
| Narrow context growth | Append 1,000 unrelated sibling groups/arguments under the same owner. The chosen local unit's substantive record IDs and excerpts remain unchanged; body-read counters stay bounded. Snapshot/source-digest metadata may change. |
| Supplier proof exclusion | Add a large unused supplier proof anchor. An ordinary application packet does not load that anchor; a `proof_argument` packet does. |
| Complete inference | A group with several joint inputs, substitutions, and case scopes includes every required input and scope even when the unit cap is one. |
| Assignment sharing | At most five selected connected units by default share statement/scope/source bodies once and allow multiple application/derivation checks in one primary assignment. A request above ten units is rejected. |
| Partial return | Save the completed subset and a draft without fabricating missing outcomes. Remaining obligations stay pending on the next worklist. |
| Internal predecessors | A later unit can cite an earlier included conclusion; an earlier gap does not make the later implication or final composition appear fully supported. |
| Composition within assignment | Final composition can join its unfinished preceding groups when outside prerequisites are satisfied; its full closure is retained and separately checked. |
| Budget boundary | Default 128 KiB, explicit 1 MiB maximum, and 2,048-record ceiling are enforced before persistence. A whole next unit can be deferred. One oversized first unit returns `prepared:false` with counts and contributor refs; no truncated packet or assignment is persisted. |
| Bindings and acceptance | Changing a consumed statement/group membership conflicts or invalidates affected work. An unrelated sibling change does not enter a task's semantic inputs. An extra anchor cited by one result binds that result only, with original provenance verified even on explicit rebase. Composition records its consumed same-response checks using their prospective IDs. Each saved check retains its own binding, not the whole assignment union. |
| Read-only context | Attempted checks outside selected target/kind pairs are rejected even if that target appears as a supplier. |
| Independence | Existing blinded-packet tests still pass; controller metadata and primary worklist/graph details cannot leak into independent payloads. |
| Provisional boundary | Default preparation does not silently cross unfinished outside examinations. Explicit provisional preparation names the boundary, preserves local/support separation, and still refuses unavailable required evidence or invalid scope. |
| Reader navigation | A missing hidden-claim obligation is searchable and opens its exact lower-reader section while the major-only graph remains unchanged. Empty-ready and audit-complete states remain distinct. |

Record packet bytes, source-excerpt bytes, unique record count, selected work units, body reads, and preparation time. Use the existing telemetry/receipt facilities instead of adding a metrics service. The earlier synthetic 100-step case, where one hidden-item request returned 101 arguments and over 400 KB, is the regression baseline for the new local packet path.

## 10. Separately deferred: lazy report details (G6)

The controller and narrow packet path must not depend on fixing the renderer's eager record duplication. Keep the existing Archify shell and canonical lower reader for this handoff, adding only worklist navigation and obligation search.

A subsequent G6 change can retain canonical bodies/trace references once and populate detail content on selection, with full print content generated when requested. That work changes report materialization and its acceptance tests. It is distinct from worker packet deduplication and is not a prerequisite for using the controller.

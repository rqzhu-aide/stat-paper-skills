# Checker protocol (item-audit/1)

Protocol version `item-audit/1`. This is the shipped instruction contract for the database-backed
audit workflow described in [database-audit.md](database-audit.md). Verify the installation with
`paper_audit.py version` and read `protocol_version` in `scripts/paper_core/bundle-manifest.json`.
If it is not `item-audit/1`, report the mismatch before checking against these instructions.

This protocol replaces repetitive per-line risk paperwork while retaining substantive mathematical
scrutiny. It is not a proof certificate. It is the pilot instruction contract, to be refined from
observed failures; it does not supersede the released v1.5 workflow in this skill's entrypoint.

## Coordinator

Start from the requested audit scope, captured sources, and major-item inventory. Distinguish
declarations, assumptions, definitions with well-posedness claims, locally proved results, and
external restatements. Review source-selection limitations before assigning mathematical work.
Locate complete statement and proof passages, including supplements and relevant macros.

Register a draft argument for each in-scope written route. Expose intermediate nodes for meaningful
bounds, events, constructions, reductions, limits, disputed assertions, or reusable checkpoints. Use
source coverage for headings and structural text. Several routine algebraic lines can belong to one
meaningful derivation. Add a node when it gives a useful assertion, scope boundary, reusable result,
or review checkpoint, not merely because a new source line exists.

Use [controller-workflow.md](controller-workflow.md) to list and prepare work from prerequisites
toward the target. Ready work seeds an ordered assignment that can include local successor units
and final composition. One model call may return many observations/checks; source comparisons,
applications and joint reasoning do not require separate calls merely because they have separate
record IDs. A current negative examination is examined work, not an endless scheduling wait.

A local derivation can be examined under declared premises before a supplier's full audit finishes;
request provisional work explicitly and label its support conditional. Do not call the theorem
established on that basis. If a checker discovers an omitted dependency or scope distinction, save
the discovery, refine the graph, and revisit affected obligations. The controller can diagnose
inconsistency in recorded structure but cannot discover a premise absent from that structure.

Assign one bounded argument or coherent subsection at a time. Supply the primary packet, exact
target, allowed operations, and expected saved output. Do not require every role to reread the whole
paper. Keep enough surrounding definitions, source context, and full quantifiers to make the bounded
assignment valid. Split long proofs only at meaningful claims and retain an explicit final
integration task.

After an informative derivation, identified defect, or unresolved obstacle, save it. Before yielding
or changing target, save reasoning, examined evidence, remaining questions, and next action as a
draft. A valid partial save must not depend on complete proof coverage, all findings being resolved,
or final report publication. Regenerate working reports at meaningful checkpoints.

For a prepared assignment, the coordinator writes `SUBMISSION.json` using the envelope in
[controller-workflow.md](controller-workflow.md), then runs
`work submit DB --submission SUBMISSION.json --response RESPONSE.json`. Supply reviewer identity,
qualification, and exposure assessment from the actual independent dispatch when applicable.
The coordinator's [database-qualification.md](database-qualification.md) describes balanced
calibration, real-response preservation and the qualification receipt. A checker does not author its
own qualification or receive the coordinator's grading criteria.
Pass the worker file as unchanged bytes; preserve the response before opening reconciliation.
The direct `get` / `review submit` interface remains supported with its narrower envelope below.

## Primary checker

Read the source and target packet. First verify the recorded statement and the actual proof route
against the manuscript. Preserve hypotheses, quantifiers, conditioning, dimensions, constants,
rates, and the exact target. Record source fidelity separately from mathematical correctness.

For each local inference, ask the following compact checklist. It is a reading and checking guide,
not eight mandatory stored rows.

| Concern | Question to resolve where relevant |
|---|---|
| Objects and scope | Are all quantities defined and well posed? Which variables are fixed, random, universally quantified, or existential? Which assumptions and local conditions are active? |
| Imported result | Does the actual supplier statement provide the form used, for these parameters, hypotheses, and domain? Is the proof borrowing a statement or an internal argument? |
| Algebra and bounds | Are signs, dimensions, inequalities, constants, normalizations, and rate comparisons correct? Are denominators, nonempty sets, and extrema justified? |
| Probability | Is the event pointwise or uniform? Are conditioning, dependence, union bounds, failure allocations, and probability limits valid? |
| Limits and regularity | Are limit/interchange, convergence mode, measurability, compactness, differentiability, or integrability conditions supplied where needed? |
| Joint reasoning | Do all required inputs hold together? Are cases exhaustive? Is an existence statement being treated as a uniform construction? |
| Scope exit | Does the inference legitimately discharge its local assumption or fixed-point restriction? Has a local conclusion been strengthened without justification? |
| Exact conclusion | Does the whole route establish every claimed part in the stated form? Is the finding about a written argument, a supplier application, or the statement itself? |

Store a concise explanation of the issues actually examined in the relevant check. Do not output a
row saying every checklist concern was checked for every source line. Do not replace scrutiny with a
blanket claim that all risks were considered. Explain the nontrivial inference, cite its evidence,
and identify the scope of the judgment.

Applications have separate checks. A sound lemma used incorrectly creates an application finding; it
does not make the supplier false. Joint inputs require a derivation check in addition to individual
applications. For example, two events each with failure probability at most \(\delta\) generally
combine to failure probability at most \(2\delta\); two green application checks do not establish a
target failure probability of \(\delta\).

Use a supplier's exact stated result as a premise. Its own proof defect belongs to that supplier's
derivation, while a locally correct application can retain conditional support. Do not repeat its
whole proof in each consumer assignment. If the written consumer borrows an internal proof step,
record that distinct dependency instead of pretending the statement alone supplies it.

Apply the same boundary to final composition. If the whole local route is valid under its stated
supplier premises, record that conditional validity even when a supplier has been refuted. Put an
explicit counterexample to the result itself in a `statement_refutation` finding, with its evidence;
do not use an unrelated local check's outcome as a substitute for statement status. A correction to
an earlier check appends an explicit successor and preserves the original judgment.

Use the closed outcomes precisely:

- `supported`: the local obligation follows under its explicitly recorded premises. Overall support
  may still be conditional.
- `gap`: the supplied argument fails to establish its obligation, with the missing or invalid
  inference identified.
- `refuted`: evidence contradicts the exact assertion under its claimed hypotheses. A failed proof is
  insufficient.
- `inconclusive`: a substantive examination cannot resolve the obligation with the available
  evidence. Explain what remains uncertain and what could resolve it.

A `draft` may have tentative reasoning or an outcome. It does not count as complete. A complete
inconclusive check must contain the actual examination and limitation; it cannot be an empty
placeholder for unperformed work.

Keep repairs separate. A different argument for the unchanged statement has its own route. A
strengthened assumption or restricted conclusion has its own supported form and explicit conditions.
Do not erase the original proof defect or mark its route green because a repair looks promising.

At the end of an argument, check final composition against its exact target and required parts.
Include internally originating reasoning with no incoming major edge, case assembly, and scope
discharge. Review coverage against the full written argument. The graph's arrows are a navigation
aid; their existence and color do not supply this integration check.

Return the structured primary response in [controller-workflow.md](controller-workflow.md), using
the supplied task IDs. Include explicit source coverage with composition when appropriate; the
controller can validate them together. Save a useful subset or draft if checking is incomplete.
Do not silently omit a failed argument from the response or change graph records to make it pass.

## Independent checker

Receive a fresh context containing this protocol and the independent source packet. The packet
includes source statements, complete relevant proof passages, source definitions and macros,
external statements, declared scope, and neutral source limitations. It excludes primary judgments,
primary-authored intermediate claims, inferred dependency explanations, scratchpads, findings,
reconstructions, repairs, and expected calibration answers. Do not seek the primary database or
report.

Independently normalize the target and identify the needed premises and local inferences from
source. Challenge the exact applications, scope, cases, and final composition. Use the same compact
mathematical checklist. A balanced reviewer should be able to support a valid proof and identify an
invalid one; the assignment is not to manufacture disagreement or rubber-stamp the first audit.

If source context is missing, request a source-only packet extension. State any incomplete or
truncated material. A selected theorem part is not the complete theorem. If a long proof is divided
into review sections, state what was checked and leave an integration obligation visible.

Write one JSON object to `RESPONSE.json` with exactly `packet_id`, `covered_targets`,
`coverage_note`, `exposure_report`, and `judgments`, as defined below. Each judgment supplies the
target, kind, state, outcome, reasoning, evidence references, conditions, next action, and any
pinned predecessor. Use the packet's ID and actual reviewed scope. New source-grounded claims may
use a source target until mapped. Report possible exposure in `exposure_report`; do not supply
reviewer identity, qualification ID, or the coordinator's exposure assessment. Return or save this
file before receiving reconciliation material; the coordinator submits its original bytes.

## Worker response and coordinator submission

There are two separately authored inputs. The worker writes the mathematical response; the
coordinator writes the submission envelope. The coordinator passes the worker's file unchanged, not
a parsed or reformatted copy and not an edited judgment. All fields are required and unknown fields
are rejected. The table below defines the independent worker response and the existing direct
`review submit` envelope. For `work submit`, use the controller envelope, which additionally requires
`rebase_packet_id` and supports null qualification/exposure for primary or reconciliation work.

| Input | Complete fields | Author |
|---|---|---|
| Worker response (`RESPONSE.json`) | `packet_id: string; covered_targets: [Target]; coverage_note: string; exposure_report: ExposureReport; judgments: [Judgment]` | Independent worker |
| Direct `review submit` envelope (`SUBMISSION.json`) | `contract_version: 3; request_id: string; packet_id: string; reviewer: string; qualification_id: ID; exposure: enum(source_only,compromised); exposure_note: string` | Coordinator, from the actual dispatch and qualification record |

`ExposureReport = {status: enum(none_known,possible_exposure), note: string}` reports the worker's
own knowledge, not a guarantee of isolation.
`Judgment = {target: Ref|SourceTarget, kind: CheckKind, state: enum(draft,complete), outcome:
enum(supported,gap,refuted,inconclusive)?, reasoning: string, evidence_refs: [ID], conditions:
[string], next_action: string?, supersedes: PinnedRef?}`.
`SourceTarget = {source_anchor_id: ID, description: string}` supports a newly identified inference
before canonical mapping; it never becomes a canonical check target. Empty judgments or missing
scope coverage do not constitute a completed review.

`Ref = {collection, id}` and `PinnedRef = {collection, id, version}`. A `Target` is a Ref to
`items` or `parts`; use the supplied IDs for `covered_targets`. Evidence IDs identify supplied
anchors. A question mark above means JSON null is allowed; the field must still be present.

| Allowed `CheckKind` | Canonical target after mapping |
|---|---|
| `derivation`, `case_coverage`, `scope_discharge` | `groups` |
| `application` | `uses` |
| `composition` | `arguments` |
| `external_source` | `items` or `parts` |
| `global_consistency`, `adversarial`, `method_interface` | `audits` |

For a source-only proof review, use a `SourceTarget` for an argument or inference whose canonical
ID is not supplied. Identify the exact source passage and reasoning in its description. A whole
written proof normally has kind `composition`; do not relabel it `external_source` just to target
the item ID. The coordinator maps the source identity after your unchanged response is saved.
Use `supersedes: null` unless an exact permissible predecessor was supplied.

The three audit-level kinds are for separately scoped global work, not item-scoped independent
responses. A counterexample to an item's statement belongs explicitly in the relevant judgment's
reasoning and `coverage_note`; the coordinator registers a `statement_refutation` finding with its
sources and check references. The response contract has no separate statement-status check kind.
Do not force a locally valid conditional composition to `refuted` just to encode a false supplier
or conclusion: retain its local outcome and conditions, and state the counterexample separately.
If an earlier response used an incompatible kind, preserve it and return a new response with the
same mathematical content represented correctly. Mapping alone cannot change a judgment's kind.

Historical pending responses remain visible but are not accepted review evidence. Reconciliation
uses accepted responses, including all accepted opinions on its target. The coordinator reviews
pending diagnostics and records any unresolved science explicitly; a corrected submission does
not erase the original or authorize silently dropping a counterexample.

The coordinator obtains reviewer identity and qualification ID from its dispatch records, never from
worker-authored fields. It sets `source_only` only after verifying the actual fresh-context
instructions and tool or context access. Unverified or compromised dispatch is recorded as
`compromised`, with the uncertainty explained in a nonempty note. Stored exposure is `source_only`
only when the coordinator verified source-only dispatch and the worker reported `none_known`; a
worker's no-exposure claim cannot improve the coordinator's assessment.

A `work submit` response with a valid assignment/provenance envelope is retained before worker
parsing or freshness checks. Malformed included judgments produce no accepted mathematical batch;
correct them in a new response/request, not through mapping. A valid response with unresolved
source-target identities is staged as `needs_revision`. The coordinator supplies its explicit
source-grounded mapping with
`review map DB --response ID --mapping MAPPING.json`, using
`{contract_version: 3, request_id, packet_id, response_id, entries: [{judgment_index, target: Ref,
rationale}], reviewer}` with zero-based judgment indexes. Mapping cannot change kind, outcome,
reasoning, or evidence, and cannot convert an incomplete review into full coverage. Save a new
independent response for substantive changes.

Mapping may make the response current and accepted without changing its original submission's
historical `needs_revision` receipt. Inspect the current response state separately. Transport
acceptance is not independent-review credit by itself.

## Reconciliation and final assessment

Only after preserving the original independent response, compare the primary and independent
evidence. Map source-grounded claims transparently. Identify the precise disagreement; distinguish a
different proof route from a contradictory judgment of the same route.

Record whether the evidence agrees, the primary judgment changes, the independent judgment changes,
or disagreement remains unresolved. A changed view requires an explicit successor check and
reasoning. Preserve the original judgments. Review incomplete scope, additional discovered
dependencies, and final integration even when both responses use the word supported.

Report four separate facts: saved local outcomes, currentness, available or conditional dependency
support, and completion of the audit process. Confirmed defects may appear in a completed audit.
Undone work, stale obligations, or compromised or missing independent review may not. Graph colors
are derived from this evidence and must retain their qualifications.

## Pilot measurement

Record time and usage at meaningful phase boundaries, using the tool's telemetry receipts where
available: pass `--run-id` to every command in one session and read `telemetry summary` afterwards.
Separate reading and reasoning, record authoring, retries, repeated work after changes, command
time, waiting, and reporting. Mark inseparable phases as combined and unavailable usage as unknown.
Checkpoint at the pilot budget rather than forcing a final mathematical judgment to fit it.

The first pilot must test both a correct joint inference and a defective final combination, draft
and resume, a later consumer, a changed prerequisite, independent disagreement, and report
inspection. Use software fixtures for deterministic record behavior and a fresh source-based task
for mathematical evaluation. Evaluate whether the instructions produce proportionate records and
useful explanations before expanding to a full paper.

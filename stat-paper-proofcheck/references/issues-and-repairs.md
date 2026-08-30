# Issues and Repairs

This file is the canonical contract for issue identity, severity effects, propagation, archival, repair, and historical-current recheck closure. Apply the verdict and confidence scales in [evidence-and-verdicts.md](evidence-and-verdicts.md).

## Canonical issue records

Define each issue once in `audit/06_reports/ISSUE_LOG.json` with:

- unique ID such as `I-001`;
- severity and confidence;
- lifecycle `status`: `open`, `resolved`, or `deferred`;
- `finding_status`: `defect`, `inconclusive`, or `resolved`;
- concise diagnostic `summary`, without repair language;
- `origin_ref`, whose `kind` is `ledger_move`, `obligation_pointer`,
  `dependency_use`, `interface_record`, or `global_check`, and whose
  identifiers resolve one exact canonical record;
- `contract_refs`, whose rows use `kind: conclusion`,
  `obligation_pointer`, or `dependency_use` to identify the exact
  mathematical statement, applicable assumptions, and scope;
- `invalidation_kind`: `proof_gap`, `proof_invalid`,
  `statement_refuted`, `dependency_mismatch`, `scope_inconclusive`, or
  `presentation_only`;
- root `affected_result`;
- `affected_results`, equal to the exact dependency-propagated result set;
- a nonempty `suggested_changes` list, each with a source-locked
  `target_ref`, `action`, exact `proposal`, `verification_status` equal to
  `candidate` or `verified_sufficient`, `required_rechecks`, and the
  repair-cost classification below (`repair_scope`, `assumption_cost`, and
  for `weaken_claim` a `claim_cost`);
- for every S0 or S1 issue, a `repair_search` record with nonempty
  `strategies` rows (`name`, `attempt`, `outcome` equal to `failed` or
  `survives_local_inspection`, substantive `evidence`) and a `conclusion`
  equal to `no_local_repair_found` or `candidate_repair_exists`;
- scope set to `unit` or `global`;
- whether the issue is load-bearing.

The repair search grounds the S0/S1 boundary in attempted repairs rather than
taste: S0 requires `no_local_repair_found` with every strategy `failed`; S1
requires `candidate_repair_exists` with at least one strategy that
`survives_local_inspection`. Record each strategy's exact point of failure
under the paper's stated hypotheses. A strategy that adds an assumption or
weakens the claim may survive local inspection, but it is diagnostic evidence
only: it never resolves the issue, lowers severity, strengthens a verdict, or
edits the manuscript, and its sufficiency claim still requires the full
suggested-change verification path below.

Do not create a second prose definition of the issue. Resolve source location,
locked source quotation, normalized claim, assumptions, failed move, and
downstream use sites from `origin_ref`, `contract_refs`, the ledgers, and the
dependency registry. A missing assumption is an absent requirement, not a
source quotation. Keep `invalidation_kind` separate from severity: severity
measures consequence, while invalidation records what the finding does to the
argument, statement, or dependency.

Reconcile `invalidation_kind` with the component judgments. A `proof_gap`
requires a gap and leaves the statement not established. A `proof_invalid`
requires an invalid argument but does not refute the statement.
`statement_refuted` requires the exact counterexample or contradiction
standard above. A `dependency_mismatch` must appear in the named use status
and dependent closure. A `scope_inconclusive` cannot support a definite defect
claim. A `presentation_only` issue cannot weaken mathematical statuses or
propagate beyond its root.

Schema-5 issues retire the authored `location`, `evidence`,
`downstream_consequences`, and `possible_repair` prose fields. They may be
read only when inspecting a legacy record and cannot support current
finalization. Exact evidence and downstream rows are derived from canonical
references, and repairs live only in `suggested_changes`.

For `origin_ref.kind: ledger_move`, record exact `unit_id`, `step_id`, and
`move_id`. An `obligation_pointer` origin records `unit_id` and `pointer`;
a `dependency_use` origin records `unit_id` and `use_id`; an
`interface_record` origin records `interface_id`; and a `global_check`
origin records its exact `aspect`. Interface and global origins also require a
nonempty `evidence_spans` list of current locked source spans. Every interface
span must be a canonical member of that interface record, and every global
origin must link back from the named global check and name the root affected
result. A conclusion contract reference records
`unit_id` and `conclusion_id`; an obligation-pointer reference records
`unit_id` and `pointer`; and a dependency-use reference records `unit_id`
and `use_id`.
Use the matching canonical registry or check identifier rather than a prose
locator. For an open or deferred issue, a ledger-move origin links back through
the owning step and, for a mathematical failure, the move's
`failure.issue_id`. Dependency, interface, and global origins link back
through the corresponding canonical `issue_ids`. Because an obligation
pointer has no issue field, it instead connects through the exact matching
obligation-pointer row in `contract_refs`. Every current contract
reference must resolve under the current source snapshot. At least one contract
reference must name `affected_result`. For an open or deferred
ledger-move issue, the referenced root conclusion must contain the origin move
in its exact backward support closure, or another root contract must be
demonstrably used by that move. An obligation or dependency origin must repeat
its exact pointer or `Dxxx` use in `contract_refs`. A
`dependency_mismatch` requires the named direct use and its canonical effective
status to be `gap` or `incorrect` for `finding_status: defect`, and `unclear`
for `finding_status: inconclusive`. It cannot borrow a failure from a sibling
use or promote uncertainty into a definite defect. A `statement_refuted` issue
requires a backlinked counterexample or contradiction move. A
`scope_inconclusive` issue requires `finding_status: inconclusive`.

Treat missing or imprecise attribution separately from mathematical support.
When an exact external result contract and its application are verified, the
absence of an inline citation command can support a bibliographic or
`presentation_only` issue, but not `proof_gap`, `proof_invalid`, or a weaker
dependency status by itself. If the source contract or applicability is not
verified, record that substantive uncertainty under the corresponding
dependency status instead.

Each suggested-change `target_ref` uses `kind: source_span` with exact
`file`, `start_line`, `end_line`, and `sha256`. Use `action` equal to
`repair_step`, `strengthen_assumption`, `weaken_claim`,
`correct_statement`, `repair_dependency`, `clarify_scope`, or
`presentation_edit`.

Each suggested change also classifies its cost. `repair_scope` records how
far the edit reaches: `local_step` (a proof rewrite with the statement
untouched), `unit_statement` (the stated result changes, so every use site
needs re-examination), `cross_unit`, or `global`. `assumption_cost` records
how much stronger the hypotheses become: `none`, `tightens_constant`,
`adds_regularity_or_moment`, `changes_regime`, or `structural`. A
`weaken_claim` change also records `claim_cost`: `restricts_scope`,
`weakens_rate`, `loses_uniformity`, or `weakens_mode`, and no other action
may carry one. Consistency is machine-checked: `strengthen_assumption`
cannot cost `none`, a `presentation_edit` must be `local_step` with no
assumption cost, and an issue whose repair search concluded
`no_local_repair_found` cannot offer a change classified `local_step` with
`assumption_cost: none`, since that is exactly the repair the search ruled
out. The classification is diagnostic triage only: it never certifies a
repair, lowers severity, or strengthens a verdict, and whether the label
fits the proposal remains reviewer judgment.

Use `finding_status: defect` when the evidence establishes a defect. Use
`inconclusive` when an ambiguity, unchecked fact, or conditional finding blocks
a conclusion. Use `resolved` only with lifecycle `status: resolved` and the full
resolution record. An open or deferred issue cannot have `finding_status:
resolved`, and a resolved lifecycle record cannot retain a defect or
inconclusive finding status.

## Resolved-issue lifecycle

Preserve the unresolved evidence before modifying anything that could erase or
move the failure. Complete and finalize the unresolved audit, then run:

```bash
python "<skill-root>/scripts/proofcheck.py" archive-issue --root "<audit-root>" --issue-id I-001
```

The command requires a current passed finalization, accepts only an open or
deferred issue, refuses to overwrite an existing archive, and writes
`audit/06_reports/history/I-001-origin.json`. Run it before editing the
paper, ledgers, dependency registry, contracts, challenges, or reports.

The archive binds the byte-exact prior manifest, issue log, final report,
affected ledgers, dependency registry, method-interface registry, inventory,
and source files to the prior finalization and source snapshot. It preserves
the old issue record, exact failure projection, prior contracts, and prior
dependency closure.

Every sealed member has exact `file`, `sha256`, and
`content_base64` fields. The mandatory `prior_artifacts` object
contains `manifest`, `issue_log`, `final_report`,
`inventory`, `dependency_registry`, `method_interface_registry`, and the exact required
`ledgers` list. Each decoded byte sequence must hash to its own digest and
to the same file row in the prior finalization artifact manifest. The archived
issue must be the exact member of the sealed issue log. The archived failure
row must equal both the sealed prior final report row and the recomputation from
the sealed ledger when the origin is a ledger move, the sealed
method-interface registry when it is an interface record, or the sealed
manifest global-consistency check when it is a global check.

The `prior_sources` list uses the same sealed-member shape. Its decoded
file set and hashes must equal the prior manifest's
`source_snapshot.files` membership exactly, with no missing, extra, or
duplicate source. Do not treat separately supplied hashes or live current files
as substitutes for these byte-exact records.

The compact `historical_origin` object in the current issue records:

- `artifact` and its exact `sha256`;
- the prior `source_snapshot_sha256`;
- `required_units`;
- `required_dependency_uses`;
- `required_challenges`;
- `required_report_deliverables`.

Keep the issue's top-level `origin_ref` equal to the archived origin for
identity, even when the old source object has been removed. Do not require that
historical reference to resolve in the current ledger. Update
`contract_refs` and `affected_results` to the current source and
current dependency graph.

Record the current repair under `current_resolution` with:

- `disposition` equal to `repaired`, `replaced`, or
  `removed`;
- `current_ref` equal to the clean current canonical origin for a
  repaired or replaced object, and null for a removed object;
- substantive `mapping` from the archived failure to the current state;
- current locked `evidence_spans`;
- `verification_status: verified_sufficient`;
- `required_rechecks` equal to the historical-current affected-unit
  union;
- `retired_dependency_uses` containing exactly every archived use absent
  from the current closure, each with `use_id`,
  `prior_edge_sha256`, substantive `reason`, and
  `recheck_evidence`.

A repaired or replaced `current_ref` must resolve to a clean current
record and connect to a current contract or support closure on the root
affected result. A removed disposition requires a null current reference and
evidence that the archived origin no longer resolves. `removed` means
that the failed move, dependency use, interface origin, or global origin was
removed inside a retained and cleanly rechecked affected result. It does not
mean that an entire theorem or audit unit can be deleted from scope. Retiring a
whole result requires a separately scoped retirement audit.

Also record a substantive `resolution` and `source_revision`, the
current `source_snapshot_sha256`, substantive `recheck_evidence`,
`rechecked_units`, `rechecked_dependency_uses`, and
`reconciled_deliverables`. The rechecked units and dependency uses must
equal their historical-current unions. A retired use remains in the recheck
union and needs its retirement evidence.

Remove the resolved issue ID from current proof-failure, dependency,
interface, and global-check backlinks. Preserve its challenge trigger and run
the fresh post-repair challenge required by
[challenge-protocol.md](challenge-protocol.md). Do not reuse the archived
challenge.

In the generated report, preserve the archived failure location, quote,
premises, rule, and failure evidence exactly. Resolve the mathematical
contract, downstream propagation, relation statuses, severity effect, and
recheck closure from current canonical records. The report must not rewrite the
historical failure or present an old downstream edge as current.

For an open or deferred load-bearing issue, start at `affected_result` and
follow the reverse internal dependency graph. Set `affected_results` to the root
and every in-scope transitive dependent reached by that load-bearing finding.
Do not leave out a downstream result because its ledger predates the issue.
Every reached result must carry a status no stronger than the propagated
finding. For a non-load-bearing issue, do not invent downstream propagation.

Propagate the effect conclusion by conclusion and keep one canonical issue ID
for the one root finding. Do not create a new issue merely because that finding
weakens a downstream result. Put the root ID on the canonical origin and on
the exact dependency or global records whose schemas carry that propagation.
If an affected dependency makes its invoking downstream step conditional or
failed, reuse the root ID only on that exact step named by the canonical `Dxxx`
edge. Do not attach it to an unrelated or otherwise valid downstream step.
Represent the full effect through the same issue's `affected_results`, the
affected `Cxxx` conclusion status, and the exact dependency closure.

A method-interface issue also records:

- `interface_id` linking the canonical interface record;
- `finding_class`: `exposition_ambiguity`, `estimator_target_mismatch`,
  `implementation_mismatch`, `reproducibility_gap`, or `scope_boundary`;
- `affected_layer` and evidence class;
- the estimator-target status, implementation inspection status, both
  code-comparison verdicts, and execution-provenance status copied exactly from
  the interface record;
- the implementation inspection mode resolved exactly from the canonical
  interface record for reporting;
- the evidence needed to resolve the finding.

The generated issue summary preserves these fields. Every later report,
handoff, or synthesis must preserve the canonical finding status, finding
class, affected layer, affected result set, relation statuses, confidence, and
inspection scope. Strengthen the claim only after new evidence is entered into
the canonical records and revalidated.

A suggested change remains `candidate` unless its target is source locked and
the revised source, root finding, and full historical-current closure have been
rechecked. Use `verified_sufficient` only with the resolved-issue evidence
above and completion of the full union recheck. Set
`required_rechecks` to the exact sorted historical-current affected-unit
union. A suggestion cannot lower severity, resolve an issue, or strengthen the
verdict by itself.

A resolved method-interface issue additionally needs a semantic contract
containing the protected mathematical meaning, minimal authoritative supporting
spans, dependent claims, conditions that reopen the issue, a regression check,
and the source snapshot identifier. Lock authoritative definitions, algorithms,
or configurations, not merely redundant explanatory prose. A changed
supporting hash marks the contract stale; the validator does not infer that
semantic meaning survived the edit.

Local ledgers reference issue IDs. They do not create competing descriptions.
Dependency and external-use records reference the same canonical IDs. Generate
`ISSUE_SUMMARY.md` with the bundled script so counts, severities, lifecycle
states, finding states, and affected results come from the canonical log.

Generate each final-report finding from the same record. The generated finding
must show the exact failure location and locked quotation; the normalized
statement, applicable assumptions, and scope; the failed move or other
canonical origin, including its exact premises and recorded failure evidence;
severity and current invalidation effect; one exact
downstream location and source quotation for every propagation edge; and the
structured suggested changes. If any reference or quotation cannot be resolved
against the current snapshot, finalization must fail rather than substitute a
paraphrase.

For a dependency-use origin, always include the originating `Dxxx` row in the
propagation table and resolved-issue recheck closure, even when the dependency
itself lies outside `affected_results`. Then add every downstream edge reached
through the affected-result closure.


When archiving more than one repair-affected issue, each archive changes the issue log and makes the prior finalization stale. Rerun finalization before the next archive. Never construct an origin archive after the repair.

When a dependency or source is missing, mark the affected unit conditional or blocked, record the exact needed evidence, and continue only with independent units. Do not fill missing material from memory.

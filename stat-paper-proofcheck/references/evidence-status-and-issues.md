# Evidence, Status, and Issue Discipline

## Evidence classes

Keep three classes separate:

1. **Observed:** explicitly present in the manuscript or verified external source.
2. **Inferred:** a reviewer reconstruction supported by observed material.
3. **Not established:** missing, ambiguous, externally unchecked, or dependent on unresolved work.

Every strong judgment must cite exact manuscript lines, theorem or equation labels, pages, or verified external theorem locations.

## Evidence specificity

Evidence must identify the paper-specific claim, objects, premises, operation,
source anchor, and observed success or failure relevant to that record. It
cannot merely restate a status or generic checklist.

Under evidence contract 4, final validation treats exact normalized wording
repeated across at least four distinct, unrelated substantive steps as nonspecific when it
appears in `checks.literal`, `checks.atomicity.evidence`, a move
`justification`, or `checks.adversarial`. It also treats the same risk
evidence reused across at least three distinct aspects within one step, or
across at least four unrelated applicable-risk steps, as nonspecific. A
paper-specific `not_applicable` row is excluded from the cross-step
applicable-risk count, but not from the within-step cross-aspect check.
Repetition below these thresholds is not positive evidence of specificity, and
cosmetic wording changes do not make generic evidence adequate.

## Assurance boundary

This protocol is non-formal. It can provide high assurance through exact source coverage, independent reconstruction, dependency closure, adversarial search, and a fresh critical-path challenge. It cannot provide the soundness guarantee of a small proof-assistant kernel.

Mechanical validation establishes that source hashes, normalized-field
dispositions, premise origins and active reference anchors, exact
reference-occurrence dispositions, `Dxxx` dependency-use mirrors, atomic move
links and reachability, source-unit coverage and hashes, one-move inferential
steps and their support roles, structured failure and status links, risk
dispositions, joint side-condition discharge, and per-conclusion support
closures are present and internally consistent. Audit-wide validation also
establishes that the reviewed closure registry matches the current source
snapshot, inventory, and scope; every direct dependency has one exact use
record; obligation and external-evidence hashes are current; compatibility and
global-consistency matrices are complete; statuses and issues propagate; and
progress and report claims reconcile. It does not establish that the
mathematics written in those fields is true.

The local active-anchor check is conservative and static. It rejects commented
labels and labels inside disabled or unresolved conditional branches, but it
also masks common command and environment definition bodies, inline `\verb`,
and common verbatim-like environments. It still does not expand macro
invocations or execute TeX. Unrecognized or dynamically generated definitions,
verbatim constructs, and labels can evade static masking. Inspect them during
manual source-resolution review, and do not rely on the local active-label
result alone.

Mechanical validation also rejects unresolved placeholders throughout the
normalized obligation and substantive proof or evidence fields. Exact `unclear`
is allowed in normalized fields only with a matching `unclear` disposition. A
status such as `not_applicable` does not replace paper-specific evidence
explaining why the aspect is absent. Record the mathematical content, the
observed failure, or an appropriate nonverified status.

## Unit verdicts

Use one verdict per proof unit:

- `verified`: all source lines and substantive steps checked; every premise is
  anchored, every declared dependency is verified, every risk is passed or
  specifically not applicable, and every side condition is discharged.
- `conditionally_verified`: each unresolved cause is explicit and maps exactly
  to an open side condition, conditional or unchecked dependency, or open risk.
- `gap`: a necessary claim is not established.
- `incorrect`: a definite invalidity or counterexample is established.
- `unclear`: ambiguity blocks a defensible conclusion.
- `not_checked`: detailed checking is incomplete.

Do not average step statuses. The weakest load-bearing step controls the unit verdict.

A verified step cannot inherit an open, failed, unclear, unchecked, or
conditional load-bearing input. A conditional step cannot hide a failed or
unclear dependency or risk. The structured condition list must be an exact
bijection with its unresolved causes. The unit verdict remains the weakest
substantive step verdict; component judgments can impose additional gates but
cannot upgrade that verdict.
Keep these judgments separate:

- `contract_fidelity`: whether the normalized obligation faithfully matches the stated result;
- `argument_status`: valid, conditional, gap, invalid, unclear, or not checked;
- `statement_status`: established, conditional, refuted, not established, unclear, or not assessed;
- `dependency_closure`: whether every load-bearing dependency resolves with compatible assumptions and conclusions;
- `use_site_sufficiency`: whether the established result is sufficient where later used.

Derive dependency availability from the named conclusion's own contract
fidelity, argument status, statement status, and dependency closure. Do not use
another conclusion or the unit-level weakest summary to cap an independent
conclusion. An established conclusion supplies `verified` only when its
contract, argument, and closure are verified; any conditional component
supplies at most `conditional`. A refuted conclusion supplies `incorrect`. A
`not_established` conclusion supplies `gap`, even when the proof failure is an
invalid argument. An unclear or unassessed conclusion supplies `unclear` or
`unchecked`. This distinction prevents an invalid proof from being propagated
as conclusion falsity.

Each `Cxxx` conclusion has one `review.conclusion_results` row supported by an
exact checked move. Its component judgments, obligation-pointer use,
dependency-use closure, and issues are conclusion-specific. For `established`
or `conditional`, that move must reach the exact conclusion claim. For
`refuted`, `not_established`, or `unclear`, it must preserve the actual failure
or mismatch. Its step status must agree with the conclusion judgment. Use
`review.conclusion_step_id` only as the single-conclusion support-step alias;
leave it empty for a multi-conclusion result. The unit-level `statement_status`
is the weakest conclusion judgment.

An `established` or `refuted` statement requires `contract_fidelity: verified`.
A `conditional` statement requires `contract_fidelity: verified` or
`conditionally_verified`. This prevents a strong statement judgment about an
uncertain normalized target.

An invalid argument establishes a defect in the proof, not the falsity of the
theorem. Use `refuted` only when an exact counterexample or contradiction
establishes that one recorded conclusion itself is false. Its support move must
record the matching `counterexample` or `contradiction` failure kind, issue
link, and evidence, with `failure.target` exactly equal to that conclusion's
claim.

## Method-interface judgments

For a triggered estimated interface, keep the proof-unit judgments above unchanged and record these additional relations in `METHOD_INTERFACE_REGISTRY.json`:

- `interface_specification_status`: `clear`, `ambiguous`, `incomplete`, or `not_checked`;
- `derivation_status`: the status of the mathematical derivation, kept separate from prose clarity;
- `target_relation.verdict`: `match`, `conditional_match`, `mismatch`, `not_assessable`, or `not_checked`;
- `implementation_relation.inspection_status`: `inspected`, `available_not_checked`, `unavailable`, `out_of_scope`, or `not_applicable`;
- separate code comparisons to `documented_estimator` and `required_target`, each with verdict `consistent`, `inconsistent`, `not_assessable`, `not_checked`, or `not_applicable`;
- `implementation_relation.execution_provenance.status`: `matched`, `not_matched`, `not_checked`, or `not_applicable`.

`conditional_match` requires an explicit named condition supported by the source. Do not use it for an unspecified manuscript meaning. If two plausible readings select different targets and the source does not choose between them, use `not_assessable` and record both interpretations.

Ambiguity can be load-bearing and severe. It does not, by itself, establish which target or implementation is wrong. A `mismatch` requires authoritative evidence that fixes both compared objects. Static code inspection can establish only what the inspected snapshot computes. It does not establish that the same code, run configuration, preprocessing, inputs, and output linkage produced reported experiments.

Keep the two code comparisons separate. Code can be consistent with the documented estimator while inconsistent with the theorem-required target because the documented estimator itself is wrong. Classify that as `estimator_target_mismatch`, not a coding defect. Use `implementation_mismatch` when the code is inconsistent with the documented estimator.

When the documented estimator itself remains ambiguous, code may still be compared directly with the required target, but the code-to-documentation verdict is ordinarily `not_assessable`. Do not let code silently choose the manuscript's intended meaning.

Execution provenance affects the proof assessment only when execution linkage is required for the declared claim. A missing link is then inconclusive, while an established required non-match is a defect. Neither state invalidates an abstract theorem that explicitly assumes an oracle nuisance condition and does not claim that the implementation establishes it.

## Severity

- **S0 Fatal:** the main theorem or central claim does not follow in the stated form, with no local repair established.
- **S1 Major:** a load-bearing assumption, dependency, or inference is missing or wrong, but a plausible repair may exist.
- **S2 Moderate:** a local gap, ambiguity, scope mismatch, or incomplete justification affects confidence but may not change the main result.
- **S3 Minor:** a typo, label, notation, or exposition defect does not change the mathematical argument.

Severity measures consequence, not certainty or repair difficulty.

S0 and S1 issues are load-bearing by definition. Any open or deferred S0 or S1 issue, and any lower-severity issue explicitly marked load-bearing, prevents a `no_defect_found` assessment.

For challenge coverage, the effective critical set is the manifest
`critical_units` union every in-scope unit in `affected_results` for an open,
deferred, or resolved load-bearing S0 or S1 issue. A resolved severe issue
continues to promote its current affected units so the repaired state receives
a fresh issue-aware challenge. S2 and S3 issues do not promote units through
this rule.

## Confidence

- **high:** exact evidence plus reconstructed reasoning or a concrete counterexample.
- **medium:** strong evidence remains dependent on interpretation or an unchecked fact.
- **low:** a plausible concern requiring further analysis.

High severity with low confidence is a priority for checking, not a proven failure.

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
  `candidate` or `verified_sufficient`, and `required_rechecks`;
- scope set to `unit` or `global`;
- whether the issue is load-bearing.

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

Each suggested-change `target_ref` uses `kind: source_span` with exact
`file`, `start_line`, `end_line`, and `sha256`. Use `action` equal to
`repair_step`, `strengthen_assumption`, `weaken_claim`,
`correct_statement`, `repair_dependency`, `clarify_scope`, or
`presentation_edit`.

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
python "<skill-root>/scripts/proofcheck.py" archive-issue --root <audit-root> --issue-id I-001
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
interface, and global-check backlinks. Keep it in `covered_issue_ids` for
every currently affected S0 or S1 unit, and run a fresh post-repair challenge
against the current source and ledger. Do not reuse the archived challenge.

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

## Verification burden

"Verified" requires positive support. The following are insufficient:

- the step is familiar;
- a similar theorem is standard;
- the manuscript compiles;
- symbolic software returns the expected expression on examples;
- no counterexample was found;
- the authors cite a relevant-looking paper;
- a downstream theorem would be true if the step held.

When evidence is incomplete, downgrade the status rather than filling the gap from mathematical taste.

## Computational evidence hierarchy

Record the encoded claim, assumptions, domain, tool and version, exact command, deterministic seed or precision when relevant, and output for every computational check.

1. An independently checkable exact certificate may verify only the precisely encoded sub-obligation. Check the translation, supported logic, side conditions, and certificate verifier. An SMT result of `unknown` supplies no support.
2. Exact symbolic algebra may discharge a specific identity only after assumptions, branches, and domains are encoded and checked. Heuristic simplification alone is not proof.
3. Validated interval arithmetic can certify a bounded numerical inclusion or counterexample when both premises and failure are enclosed rigorously.
4. Ordinary numerical tests, simulation, property testing, and random search are falsification tools. A found candidate must be checked exactly or with validated bounds. Finding no counterexample leaves proof status unchanged.

Never promote evidence beyond the claim actually encoded.

## Independent critical-path evidence

For every effective-critical result, require a challenger pass that does not see
the primary verdict or proposed repair. Set `covered_issue_ids` to the sorted
distinct open, deferred, or resolved load-bearing S0 or S1 issues whose
`affected_results` contain that unit; use an empty list for a unit that is
critical only by manifest declaration. For each covered issue, give the
challenger the exact source-locked target and mathematical contract, then
require an independent assessment of that target and its downstream relevance.
Listing the issue ID without challenging its substance is not coverage. Record
`source_snapshot_sha256`,
`challenged_ledger_sha256` computed from the canonical ledger without
`independent_check`, `challenge_artifact_sha256`, and `generated_utc`.
Also preserve the independence level as fresh-context same model, different
model, or independent human, together with the primary verdict, challenger
verdict, reconciled verdict, disagreements, resolution, and artifact. A stale
hash, missing or extra issue ID, or same-context reread cannot support
independent confirmation. `agreed` requires identical challenger and reconciled
verdicts equal to the final unit status, with no disagreements. `resolved`
requires a reconciled verdict equal to the final unit status, at least one
recorded disagreement, and a substantive resolution.

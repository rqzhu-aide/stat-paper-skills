# Proof-Check Plan

## Scope

- Paper:
- Source files and revision:
- Audit depth: triage, focused, or full
- Target results:
- Explicit exclusions:
- Available external sources:
- Overall assessment at completion: no defect found, defects found, or inconclusive

Triage is planning-only and cannot be finalized. For Focused or Full work,
designate at least one critical unit, normally the target result or main
theorem. For Full work, include every proof-required inventory unit in scope.
Audit a missing or defective proof as a finding rather than excluding its result.
For Focused work, set nonempty `target_units` and make the in-scope set exactly
the targets plus their transitive internal prerequisites.

## Central claim and proof strategy

- Main mathematical claim:
- Core proof mechanism:
- Highest-risk link:

## Source and parser limitations

- Included files:
- Macros or generated content requiring manual inspection:
- PDF-only or missing-source limitations:

## Proof-unit inventory

| Unit | Statement location | Proof range | Direct dependencies | Use sites | Planned depth | Status |
|---|---|---|---|---|---|---|

For every in-scope unit, complete the normalized obligation contract in its ledger before checking proof steps.

## Reviewed inventory overrides

Use only when the parser omitted a genuine unit or proof location, when a
forwarding proof association requires rendered-source confirmation, or when a
candidate must be replaced or explicitly rejected. Mirror each row in
`AUDIT_MANIFEST.json`. Bind a manual unit with `reviewed_unit_sha256`. For a
rejection, use a null reviewed proof and a reviewed association with status
`rejected`, method `reviewed_rejection`, the same target, and no evidence
occurrences. Source-lock and rescan any changed proof span, and reconcile its
exact occurrences, dependencies, and citations.

| Unit | Kind: manual unit, proof location, or proof association | Parser candidate | Reviewed span or association | Reason | Rendered-source evidence |
|---|---|---|---|---|---|

## Critical path

List prerequisites before dependent results.

## Dependency-closure registry review

- Closure contract version: 3
- Review status:
- Source snapshot SHA256:
- Inventory SHA256:
- Exact in-scope units:
- Review evidence:

### Internal uses

| Dependent unit | Use ID | Dependency | Dependency conclusion ID | Invoking steps | Needed form | Dependency conclusion | Conclusion contract SHA256 | Compatibility status | Effective status | Issue IDs |
|---|---|---|---|---|---|---|---|---|---|---|

For every row, complete all eight `compatibility_checks`: quantifiers and
domains, probability model, hypotheses, definitions, conclusion, uniformity,
regime, and constant dependencies.

### External results and uses

| External result | Source status | Source evidence hash and locator | Dependent unit | Use ID | Invoking steps | Citation keys | Needed form | Applicability status | Issue IDs |
|---|---|---|---|---|---|---|---|---|---|

Record each external source once and each manuscript use separately.

## Cross-reference anomaly review

Review exactly every broken reference and duplicate label. Orphan labels do not
require rows.

| Kind | Key | Exact locations | Status | Evidence | Affected units | Issue IDs |
|---|---|---|---|---|---|---|

Use only `passed`, `defect`, or `inconclusive`.

## Independent challenger plan

| Critical unit | Primary checker | Blinded challenger | Independence level | Challenger verdict | Reconciled verdict | Artifact |
|---|---|---|---|---|---|---|

## Required ledgers

- [ ] Assumptions
- [ ] Notation
- [ ] Constants and rates
- [ ] Probability events
- [ ] External results

## Global consistency matrix

| Aspect | Status | Evidence | Affected units | Issue IDs |
|---|---|---|---|---|
| source_resolution |  |  |  |  |
| assumption_and_definition_propagation |  |  |  |  |
| notation_domain_and_dimension |  |  |  |  |
| constants_and_rates |  |  |  |  |
| probability_events_and_conditioning |  |  |  |  |
| quantifiers_uniformity_and_regime |  |  |  |  |
| use_site_sufficiency |  |  |  |  |
| issue_propagation |  |  |  |  |

Use only `passed`, `not_applicable`, `defect`, or `inconclusive`.

## Scale and stabilization risk review

- Fixed floor versus shrinking covariance, eigenvalue, standard-error, or calibration scale:
- Covariance symmetry and positive semidefiniteness; strictly positive denominator scales or explicit degeneracy handling:
- Ridge, clipping, floor, truncation, or stabilization perturbation at the theorem scale, propagated to approximation and coverage claims:

## Method-interface trigger review

- Trigger decision: required or not required
- Reason:

Use a record only for a load-bearing estimated or implemented interface that meets the trigger in `SKILL.md`.

| Interface | Population target | Fitting laws | Evaluation site | Downstream use | Estimator to target | Code to documentation | Code to target | Execution provenance | Issue IDs |
|---|---|---|---|---|---|---|---|---|---|

## Issue-resolution evidence preservation

Before repairing an open or deferred issue, complete and finalize the
unresolved audit, then run:

```bash
python "<skill-root>/scripts/proofcheck.py" archive-issue --root <audit-root> --issue-id I-001
```

Do not modify the source or canonical audit records before the archive
succeeds. For a resolved issue, preserve the archived top-level
`origin_ref` for identity, keep current contracts and propagation in
`contract_refs` and `affected_results`, and place current provenance
in `current_resolution`. Recheck the historical-current unit and
dependency-use unions, record every retired use, run fresh issue-aware
challenges, and reconcile every required report deliverable.

## Completion gates

- [ ] Exact line coverage for every in-scope unit
- [ ] Every ordered `Cxxx` conclusion has exact source spans, scalar applicability pointers, normalization evidence, and one support-closure judgment
- [ ] Obligation normalization checks complete; mandatory fields are substantive,
  explicit absence occurs exactly with `not_applicable`, and verified or conditional contracts contain no unclear check
- [ ] Every obligation premise resolves to one scalar string and its claim equals that string exactly
- [ ] Every dependency is used and each dependency premise matches its `needed_form`
- [ ] Every prior-step `needed_form` exactly equals the earlier step's restatement
- [ ] Every result use has one audit-globally unique `Dxxx` ID, every internal use names one `Cxxx` dependency conclusion, and each result record exactly mirrors `review.direct_dependencies`
- [ ] No declared dependency has status `not_applicable`
- [ ] No substantive claim, check, or evidence field contains a bare absence or unresolved placeholder
- [ ] Every normalized obligation field is free of unresolved placeholders; exact `unclear` has the matching `unclear` disposition
- [ ] Every parser reference occurrence has exactly one disposition keyed by occurrence ID, target, and command; every premise-bearing role has exact bidirectional links
- [ ] Common definition bodies, inline `\verb`, and common verbatim-like environments cannot satisfy active-label anchors
- [ ] Unsupported or dynamically generated macro, verbatim, or label cases resolved manually in the source-resolution pass
- [ ] Every successful or conditional inference move has an input
- [ ] Every zero-input failed or unclear move has a status-matched failure kind, step issue link, and substantive evidence
- [ ] Every inference move lies in the conclusion's load-bearing closure
- [ ] Each conclusion support move is linked; successful claims exactly reach its `Cxxx` target and failures preserve the mismatch with an issue
- [ ] Each conclusion's dependency-use list and obligation-pointer use equal its exact backward support closure
- [ ] A refuted statement has a counterexample or contradiction failure whose target exactly equals the normalized conclusion
- [ ] Established and refuted statements have verified contract fidelity; conditional statements have verified or conditionally verified fidelity
- [ ] Exact risk-check coverage for every substantive step
- [ ] Joint side-condition discharge records every premise or earlier established-move contribution, rule, and evidence; conditional causes are closed
- [ ] Current source and external-evidence hashes
- [ ] Full depth includes every proof-required inventory unit
- [ ] Focused depth has nonempty target units and exact transitive dependency closure
- [ ] Closure registry review matches the source snapshot, inventory hash, and exact scope
- [ ] Internal uses are an exact one-to-one match to direct internal dependencies
- [ ] Every internal use binds exact invoking steps, needed form, dependency conclusion, and conclusion contract SHA256
- [ ] Every internal and external use has all eight compatibility aspects and a derived status
- [ ] Every external use has exact citation keys, prerequisite maps, and current evidence spans
- [ ] Every `external_restatement` has one source-bound override, exact statement-only ledger coverage, one designated external use, and a matching missing-proof warning review
- [ ] Broken references and duplicate labels have exact reviewed records
- [ ] Dependency cycles, stale or unused records, and status mismatches are absent
- [ ] Method-interface trigger and registry reviewed
- [ ] Exact global consistency matrix and adversarial pass complete
- [ ] Fresh-context challenge and reconciliation for every effective-critical unit, including every current unit promoted by an open, deferred, or resolved load-bearing S0 or S1 issue
- [ ] Every locked source_lines row contains its exact line text and matching SHA256; every source_unit.source_sha256 matches the newline-joined text of its exact range
- [ ] Every review.use_sites entry is one canonical file:line reference occurrence; every locked downstream use span, SHA256, and quote is exact
- [ ] Every generated finding reproduces the canonical locked quote, exact premises, and recorded failure evidence without paraphrase
- [ ] Downstream effects weaken dependency closure and proof support only to the level established; they do not refute a downstream conclusion without independent evidence
- [ ] Every method-interface record reports both implementation inspection status and inspection_mode
- [ ] Every critical challenge reports disagreements, resolution, artifact path, current artifact hash, and freshness fields
- [ ] Every agreed challenge has identical challenger, reconciled, and final unit verdicts with no disagreements; every resolved challenge has a reconciled verdict equal to the final unit status, recorded disagreements, and substantive resolution
- [ ] Every declared user-facing report exactly reconciles all canonical scalar metadata and semantic sections, including Computational evidence, using active Markdown without raw HTML
- [ ] The final-report Declared external deliverables scalar and table exactly reconcile with manifest report_deliverables
- [ ] Canonical issue finding status and affected-result propagation agree
- [ ] Each downstream consequence reuses its root issue ID only in canonical propagation records and does not copy it into an otherwise valid proof step
- [ ] Every resolved issue was archived before repair and has a hash-current `historical_origin` bound to a passed prior finalization
- [ ] Every resolution archive has byte-exact manifest, issue-log, final-report, inventory, dependency-registry, method-interface-registry, and required-ledger members under `prior_artifacts`, and `prior_sources` exactly matches the prior source snapshot
- [ ] Every archived ledger, method-interface, or global-check failure projection is recomputed from its sealed canonical origin record
- [ ] Every resolved issue has a clean structured `current_resolution`, exact retired-use records, and complete historical-current recheck unions
- [ ] Every resolved S0 or S1 issue remains in the fresh current challenges for all currently affected units
- [ ] `PROGRESS.json` exactly reconciles scope, statuses, snapshot, and open S0/S1 issues
- [ ] `proofcheck.py status` preflight reports `finalizable_now: true` and no current gate errors
- [ ] Final report exactly reconciles canonical scope, unit, dependency, external, issue, and protocol fields
- [ ] Explicit unchecked scope
- [ ] `completion.final_report_ready` is true before changing the report title to `Final Proof-Check Report` and removing the nonfinal notice
- [ ] `proofcheck.py finalize` passes
- [ ] `audit/06_reports` contains no undeclared Markdown report, and the canonical report contains neither the `NONFINAL SCAFFOLD` notice nor the nonfinal working title
- [ ] `proofcheck.py status --require-finalized` returns zero with `audit_complete: true` and `delivery_status: FINAL`
- [ ] `proofcheck.py delivery-check` returns zero with `delivery_status: FINAL` and `usable_finalization: true`

# NONFINAL Proof-Check Working Report

> **NONFINAL SCAFFOLD:** This working template is not a completed audit report.
> Keep this title and notice until `completion.final_report_ready` is true.
> Then rename the title to `Final Proof-Check Report`, remove this notice, and
> run the full finalization and delivery sequence.

Treat this report as a projection of canonical JSON. Generate all exact scalar
fields, ID sets, status tables, dependency rows, issue views, challenge rows,
method-interface rows, and deliverable rows from canonical records whenever the
bundled tooling supports them. Author only the short interpretive judgment,
confidence, and limitations text that cannot be derived mechanically.

## Verdict

- Overall assessment code:
- Overall judgment:
- Target results:
- Checked scope:
- Source revision:
- Skill version: 1.2
- Artifact schema version: 5
- Evidence contract version: 5
- Closure contract version: 4
- Method-interface schema version: 1
- Source snapshot ID:
- Finalization record: audit/06_reports/FINALIZATION.json
- Highest-consequence issue:
- Final confidence:
- Independence level of the critical-path challenge:

Use exactly `no_defect_found`, `defects_found`, or `inconclusive` for the
assessment code. Keep the judgment conditional on the checked source and
recorded assumptions. Do not call this a formal proof certificate.

For every canonical ID list, sort IDs, separate them with a comma and one
space, and write `none` for an empty set. Use only these independence values:
`none`, `fresh_context_same_model`, `different_model`, or
`independent_human`.

## Audit boundary and limitations

- Files and results checked:
- Results not checked:
- External results checked:
- External results not checked:
- Tooling, extraction, or rendering limitations:
- Declared external deliverables:

## Main theorem chain

| Result | Unit status | Contract fidelity | Argument status | Statement status | Dependency closure | Use-site sufficiency | Evidence |
|---|---|---|---|---|---|---|---|

## Conclusion judgments

Include one row per ordered `Cxxx` conclusion in every in-scope ledger.

| Result | Conclusion | Contract fidelity | Argument status | Statement status | Dependency closure | Use-site sufficiency | Support | Dependency use IDs | Issue IDs |
|---|---|---|---|---|---|---|---|---|---|

## Dependency closure

Include one row per canonical internal or external dependency use.

| Dependent | Use ID | Dependency | Dependency conclusion | Kind | Source status | Applicability status | Effective status | Issue IDs |
|---|---|---|---|---|---|---|---|---|

## Issue index

This canonical section is rewritten from validated records by
`issues --write-report-views --final`. Do not edit it manually. If the issue
log is empty, the generator writes exactly `No issues.`

| Issue | Severity | Load-bearing | Confidence | Lifecycle | Finding | Invalidation kind | Origin ref | Contract refs | Affected results |
|---|---|---|---|---|---|---|---|---|---|

## Detailed findings

This canonical section is rewritten by `issues --write-report-views --final`.
The generator emits one block per issue in severity order, then by issue ID.

### I-001 [S1] summary

#### 1. Exact failure site and contract

Generate the failure site, failed move, exact premises, and recorded failure
evidence by dereferencing `origin_ref`.
Generate the normalized conclusion and assumptions from `contract_refs`. The
quote must come from the locked source span.

For a resolved issue, obtain the exact failure row from its validated
historical archive, not from a repaired current move. Obtain the contract rows,
propagation, current effects, and repair closure from current canonical
records.

| File and lines | Span SHA256 | Exact locked quote | Result | Step and move | Claim | Rule attempted | Premises | Failure evidence | Failure kind |
|---|---|---|---|---|---|---|---|---|---|

| Contract ref | Normalized claim or assumption | Scope, model, and regime | Evidence |
|---|---|---|---|

#### 2. Downstream consequences

Generate the origin and every exact transitive dependent from the dependency
registry and conclusion statuses. Every downstream row needs a locked use-site
quote. For a non-load-bearing issue, do not invent downstream proof
invalidation.

| Affected result | Relation | Use ID | Dependency conclusion | Use-site file and lines | Use-site SHA256 | Exact use-site quote | Propagated effect |
|---|---|---|---|---|---|---|---|

#### 3. Severity and validity effect

| Severity | Load-bearing | Confidence | Invalidation kind | Current unit effect | Current conclusion effect | Overall assessment effect |
|---|---|---|---|---|---|---|

For an S0 or S1 issue, the generator also renders the canonical repair-search
conclusion and one row per attempted repair strategy.

| Strategy | Attempt | Outcome | Evidence |
|---|---|---|---|

#### 4. Suggested changes and recheck

Copy the issue's structured `suggested_changes`. Keep diagnosis and repair
separate. Do not claim sufficiency before the required rechecks pass.

| Target | Action | Repair scope | Assumption cost | Claim cost | Proposal | Verification status | Required rechecks |
|---|---|---|---|---|---|---|---|

Derive full closure from the union of archived and current affected results,
dependency uses, critical challenges, and `report_deliverables`. Record
every retired dependency use with its archived edge hash and recheck evidence.
An issue is not resolved merely because source text changed.

| Required units | Rechecked units | Required dependency uses | Rechecked dependency uses | Required challenges | Reconciled challenges | Required deliverables | Reconciled deliverables | Closure status |
|---|---|---|---|---|---|---|---|---|

## Independent critical-path challenges

Include every declared or issue-promoted critical unit. A challenge covering an
open, deferred, or resolved S0 or S1 issue must list that issue in
`covered_issue_ids` and must be fresh for the current source snapshot and
challenged ledger. Its challenge-context hash and per-issue assessments must
match the exact current challenge packet. Do not reuse a pre-repair challenge
for a resolved issue. Render `Issue assessments` as a compact JSON array sorted
by `issue_id`. Within each object, use this exact key order: `issue_id`,
`target_contract_sha256`, `assessment`, `target_assessment`,
`downstream_assessment`. Render `Disagreements` as a compact JSON array in
canonical ledger order. Escape a literal pipe inside either Markdown cell as
`\|`.

| Result | Challenge status | Independence | Covered issue IDs | Issue assessments | Challenger verdict | Reconciled verdict | Disagreements | Artifact | Source snapshot SHA256 | Challenged ledger SHA256 | Challenge context SHA256 | Artifact SHA256 | Generated UTC | Resolution |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Method-interface findings

Use one row per canonical method-interface issue. Preserve estimator-target,
implementation, inspection-mode, code-comparison, and execution-provenance
statuses exactly.

| Issue | Finding class | Interface ID | Estimator-target status | Implementation inspection | Inspection mode | Code to documented estimator | Code to required target | Execution provenance | Affected layer |
|---|---|---|---|---|---|---|---|---|---|

If none are in scope, write exactly `None.`

## Declared external deliverables

This section is optional. Include it only when the manifest's
`report_deliverables` list is nonempty. Its row IDs must equal the
mandatory `Declared external deliverables` scalar exactly.

| Deliverable ID | Role | Path | SHA256 | Issue IDs | Overall verdict |
|---|---|---|---|---|---|

## Computational evidence

For each computational check, record the claim, assumptions, domain, tool and
version, exact command, seed or precision, output, and narrow conclusion.
Distinguish exact certificates from falsification-only tests.

## Unchecked scope

State every material proof unit, dependency, external theorem, source region,
implementation component, or deliverable not checked.

## Assurance boundary

This is a non-formal audit. A passing finalization gate means that the required
source, scope, atomic evidence, dependency, issue propagation, challenge,
recheck, progress, report, and deliverable records passed mechanical closure
checks. Mathematical correctness still depends on reviewer judgment. This does
not provide the soundness guarantee of a proof-assistant kernel.

# Final Proof-Check Report

## Verdict

- Overall assessment code:
- Overall judgment:
- Target results:
- Checked scope:
- Source revision:
- Skill version:
- Artifact schema version:
- Evidence contract version:
- Closure contract version:
- Method-interface schema version:
- Source snapshot ID:
- Finalization record: audit/06_reports/FINALIZATION.json
- Highest-consequence issue:
- Final confidence:

Set `Overall assessment code` to exactly `no_defect_found`, `defects_found`, or
`inconclusive`, matching the manifest and evidence. Set `Closure contract
version` to `2`. State the corresponding judgment in prose. Do not describe
this report as a machine-checked proof certificate.

For `Target results`, `Checked scope`, `Results not checked`, `External results checked`,
`External results not checked`, and `Highest-consequence issue`, write the exact
canonical IDs in sorted order, separated by a comma and one space, with no
trailing punctuation. Write exactly `none` for an empty set. Use `none` for
`Tooling, extraction, or rendering limitations` only when the canonical scope
records no limitation. Use exact independence enum values only:
`none`, `fresh_context_same_model`, `different_model`, or `independent_human`.

## Audit boundary and limitations

- Files and results checked:
- Results not checked:
- External results checked:
- External results not checked:
- Tooling, extraction, or rendering limitations:
- Independence level of the critical-path challenge:

## Main theorem chain

| Result | Unit status | Contract fidelity | Argument status | Statement status | Dependency closure | Use-site sufficiency | Evidence |
|---|---|---|---|---|---|---|---|

## Conclusion judgments

Include exactly one row for every ordered `Cxxx` conclusion in every in-scope
ledger. Match the conclusion ID, support `step_id/move_id`, component judgments,
dependency-use closure, and issues exactly. The exact claim remains canonical in
the ledger's obligation record.

| Result | Conclusion | Contract fidelity | Argument status | Statement status | Dependency closure | Use-site sufficiency | Support | Dependency use IDs | Issue IDs |
|---|---|---|---|---|---|---|---|---|---|

## Dependency closure

Include exactly one row per canonical internal or external use.

| Dependent | Use ID | Dependency | Dependency conclusion | Kind | Source status | Applicability status | Effective status | Issue IDs |
|---|---|---|---|---|---|---|---|---|

## Independent critical-path challenge

Include exactly one row per critical unit. For disagreements, use `none` or
join the exact ordered ledger entries with `; `. Use `none` when resolution is
empty.

| Result | Challenge status | Independence level | Challenger verdict | Reconciled verdict | Disagreements | Resolution | Artifact |
|---|---|---|---|---|---|---|---|

## Issue summary

Copy the canonical full-field Issues table from generated
`ISSUE_SUMMARY.md`. If the issue log is empty, write exactly `No issues.` Do
not substitute a link or create separate manual issue rows.

## Method-interface findings

Use one exact row per canonical method-interface issue. In the final cell, write
`Evidence: <ordered evidence joined by ; > Consequences: <ordered downstream_consequences joined by ; >`
from `ISSUE_LOG.json`.

| Issue ID | Finding class | Interface ID | Estimator-target status | Implementation inspection | Code to documented estimator | Code to required target | Execution provenance | Affected layer | Evidence scope and consequence |
|---|---|---|---|---|---|---|---|---|---|

If none are in scope, write exactly `None.`

## Proposed repairs

Keep repairs separate from findings. State whether a repair has been proved sufficient or is only a candidate.

## Computational evidence

For each computational check, record the encoded claim, assumptions, domain, tool and version, exact command, seed or precision, output, and the narrow conclusion it supports. Distinguish exact certificates from falsification-only tests.

## Unchecked scope

State every material proof unit, dependency, external theorem, or source region not checked.

## Assurance boundary

This is a non-formal audit. A passing finalization gate means that the required
source, scope, evidence, dependency-use, compatibility, global-consistency,
interface, issue-propagation, progress, report, and challenger records passed
the mechanical closure checks. Their mathematical content still depends on
reviewer judgment. This does not provide the soundness guarantee of a
proof-assistant kernel.

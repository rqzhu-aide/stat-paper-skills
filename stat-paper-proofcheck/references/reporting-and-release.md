# Reporting and Release

This file is the canonical contract for generated report projections, finalization, delivery checks, and final assurance language. Challenger semantics are defined only in [challenge-protocol.md](challenge-protocol.md).

## Report directory and declared deliverables

Reserve the top level of `audit/06_reports/` for `FINAL_REPORT.md`,
`ISSUE_SUMMARY.md`, and complete manifest-declared user-facing reports. Move
drafts, partial reports, and working notes elsewhere. An undeclared Markdown
file there is a report-integrity error.

When delivering a report outside the canonical `FINAL_REPORT.md`, declare it in
the optional manifest `report_deliverables` list. Each row contains an `Rxxx`
`id`, `role: user_facing_report`, `path`, `sha256`, `issue_ids`, and
`overall_verdict`. The path and hash must be current. The issue set, verdict,
and canonical report sections must match `FINAL_REPORT.md` exactly. This
includes `Verdict` when present, `Audit boundary and limitations`, `Main theorem
chain`, `Conclusion judgments`, `Dependency closure`, `Issue index`, `Detailed
findings`, `Independent critical-path challenges`, `Method-interface findings`,
`Computational evidence`, `Unchecked scope`, and `Assurance boundary`. A
different title and extra orientation prose are allowed. Do not declare a
draft, partial export, or summary as a delivered report.

Keep the scaffolded `NONFINAL SCAFFOLD` notice and title
`NONFINAL Proof-Check Working Report` until the canonical report and generated
issue views are complete and `completion.final_report_ready` is true. Then use
the title `Final Proof-Check Report`, remove the notice, and run the status,
issue-reconciliation, finalization, and delivery sequence. Finalization rejects
either nonfinal marker.

## Final report contract

Use `assets/templates/FINAL_REPORT.md`. Report:

Treat the report as a reviewed projection of canonical records, not a second
authored evidence store. Generate protocol metadata, exact ID sets, unit and
conclusion statuses, dependency rows, issue views, challenger rows,
method-interface rows, and deliverable rows directly from their canonical
records whenever the bundled tooling provides that projection. Author only
the concise overall interpretation, confidence, and limitations that require
judgment. Do not load every completed ledger into a separate reporting model
call merely to copy fields into Markdown.

1. overall verdict, exact target results, and exact checked scope;
2. source revision, closure contract version, and tooling limitations;
3. main theorem chain, with the exact unit-level status and component judgments
   for every in-scope result, plus one exact conclusion-judgment row per `Cxxx`
   conclusion;
4. the generated issue index and one exact detailed finding for every canonical
   issue;
5. external-result status through the dependency-closure table and exact set
   fields;
6. structured suggested changes and the full required recheck closure,
   separated from the diagnostic finding;
7. unchecked scope and final confidence.

Include the conclusion-judgments table with these columns exactly:

| Result | Conclusion | Contract fidelity | Argument status | Statement status | Dependency closure | Use-site sufficiency | Support | Dependency use IDs | Issue IDs |
|---|---|---|---|---|---|---|---|---|---|

Write `Support` as exact `step_id/move_id`. Include one row for every ordered
conclusion in every in-scope ledger.

Include the protocol identity fields and the required dependency-closure table
with these columns exactly:

| Dependent | Use ID | Dependency | Dependency conclusion | Kind | Source status | Applicability status | Effective status | Issue IDs |
|---|---|---|---|---|---|---|---|---|

Include one row for every canonical internal or external use. Match identifiers,
statuses, and issues exactly to `DEPENDENCY_REGISTRY.json` and the ledgers.

Include exactly one independent-challenge row for every unit required by
[challenge-protocol.md](challenge-protocol.md), and include only records that
pass that protocol's current binding and reconciliation gates. Copy challenge
status, independence level, challenger and reconciled verdicts, ordered
disagreements, resolution, artifact, hashes, `covered_issue_ids`, and
`issue_assessments` from the canonical ledger exactly. Render `Issue
assessments` as a compact JSON array sorted by `issue_id`, using key order
`issue_id`, `target_contract_sha256`, `assessment`, `target_assessment`,
`downstream_assessment`. Render `Disagreements` as a compact JSON array in
canonical ledger order. Escape a literal pipe inside either Markdown cell as
`\|`.

Use this exact challenge table:

| Result | Challenge status | Independence | Covered issue IDs | Issue assessments | Challenger verdict | Reconciled verdict | Disagreements | Artifact | Source snapshot SHA256 | Challenged ledger SHA256 | Challenge context SHA256 | Artifact SHA256 | Generated UTC | Resolution |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Also include a method-interface table with the canonical issue ID, finding
class, interface ID, estimator-target status, implementation inspection status,
inspection mode, both code-comparison verdicts, and execution-provenance
status. These fields, together with the canonical affected layer, must match
the registry and issue log exactly. State whether an
implementation result came from static inspection, execution, or both. Resolve
its exact evidence and consequences through the canonical detailed finding
rather than adding another evidence or consequence narrative to this table.

Set `Method-interface schema version` to exactly `1` and use this
exact method-interface table:

| Issue | Finding class | Interface ID | Estimator-target status | Implementation inspection | Inspection mode | Code to documented estimator | Code to required target | Execution provenance | Affected layer |
|---|---|---|---|---|---|---|---|---|---|

Treat these report fields as exact machine-reconciled sets: `Target results`, `Checked scope`,
`Results not checked`, `External results checked`, `External results not
checked`, `Declared external deliverables`, and `Highest-consequence issue`.
Write sorted IDs separated by a comma and one space, with no trailing
punctuation. Write exactly `none` for an empty set. Use `none` for `Tooling,
extraction, or rendering limitations` only when no such limitation exists. Use
only the exact independence enum values
`none`, `fresh_context_same_model`, `different_model`, or `independent_human`;
when more than one value applies, list the unique values in sorted
comma-separated form.

The `Declared external deliverables` scalar is mandatory and equals the
exact sorted manifest `report_deliverables` ID set, or `none`. The
`## Declared external deliverables` table is present exactly when that set
is nonempty, with one exact canonical row per declared deliverable.

Every declared user-facing report must retain all canonical scalar metadata
and every semantic section exactly, including `## Computational evidence`.
Only its title and additional orientation prose may differ. Required report
content must be active Markdown, not HTML comments, fenced or indented code, or
raw HTML. Active raw HTML is rejected because rendered visibility cannot be
reconciled reliably. Literal code, mathematical expressions, block quotations,
and exact locked-evidence cells do not count as authorial assurance claims.

Set `Overall assessment code` to exactly `no_defect_found`, `defects_found`, or
`inconclusive`, matching `AUDIT_MANIFEST.json`. The finalizer derives precedence
from the evidence: a recorded defect overrides inconclusive units, and
inconclusive units override a no-defect assessment. Set `Closure contract
version` to exactly `3`.

Generate issue counts in `ISSUE_SUMMARY.md` with
`proofcheck.py issues --write-summary`. At final reporting, add
`--write-report-views --final` as shown below. `--write-report-views` requires
`--final` and rewrites only the canonical `Issue index` and `Detailed
findings` sections of `FINAL_REPORT.md` from validated issue, ledger, and
dependency records. It leaves every other report section unchanged. Do not
type competing counts, finding rows, quotations, or repairs manually. Use these
stable report headings:

- `## Issue index`;
- `## Detailed findings`;
- one `### I-001 [S1] summary` heading per issue, using its actual ID,
  severity, and summary;
- `#### 1. Exact failure site and contract`;
- `#### 2. Downstream consequences`;
- `#### 3. Severity and validity effect`;
- `#### 4. Suggested changes and recheck`.

For an open or deferred issue, derive the exact locked failure span, quotation,
premises, rule, and failure evidence from its current `origin_ref`. For a
resolved issue, derive those failure fields only from the validated historical
archive. In all cases, derive the normalized statement, applicable assumptions,
and scope from current `contract_refs`. Derive every current downstream
row from the reviewed dependency graph and invoking `Dxxx` use, including
its exact locked use-site span, quotation, dependency conclusion, and validity
effect. Show severity, confidence, lifecycle, finding status,
`invalidation_kind`, and current invalidation effect. Render each
structured suggested change with its source-locked target, action, proposal,
verification status, and required rechecks, followed by the full recheck
closure across affected units, dependency uses, challenges, and declared
report deliverables.

The issue index and detailed findings are generated projections of
`ISSUE_LOG.json`, ledgers, the dependency registry, and locked source.
They do not define issues again. If a current reference or a validated
historical archive reference, hash, or quotation cannot be resolved exactly,
or the rendered issue set differs from the canonical log, fail finalization.
When the issue log is empty, write exactly `No issues.` in the index and
do not invent detailed findings.

Reconcile the main-theorem rows, dependency-closure rows, generated issue
views, exact set fields, protocol fields, and all `report_deliverables` against
the canonical JSON records. Do not duplicate the full external-use records,
global consistency matrix, or result-status sections; those remain canonical in
the main-theorem table, `DEPENDENCY_REGISTRY.json`, manifest completion checks,
and `ISSUE_LOG.json`.

Before release, write the final derived progress state through `checkpoint`,
then run the strict issue and finalization gates:

```bash
python "<skill-root>/scripts/proofcheck.py" checkpoint --root <audit-root> --clear-active-unit --next-action "Run final issue reconciliation and finalization."
python "<skill-root>/scripts/proofcheck.py" issues --root <audit-root> --write-summary --write-report-views --final
python "<skill-root>/scripts/proofcheck.py" sync-views --root <audit-root>
python "<skill-root>/scripts/proofcheck.py" finalize --root <audit-root>
python "<skill-root>/scripts/proofcheck.py" delivery-check --root <audit-root>
```

The final command writes `FINALIZATION.json` with pass or fail status, protocol
identity, closure contract version, source snapshot identifier, file-level
audit-artifact manifest, audit-state hash, and validation errors. Treat that
generated file as the persisted gate result.

`delivery-check` is the last, read-only release gate. Deliver a proofcheck
report as final only when its JSON output contains `delivery_status: FINAL`
and `usable_finalization: true`. A missing, failed, stale, foreign-path-bound,
or otherwise unusable finalization returns `NONFINAL` and a nonzero exit code.
This gate applies even if an earlier report exists or an informal reviewer
found a plausible defect.

Before finalization, `proofcheck.py status --root <audit-root>` always runs the
current gate as a preflight. Its default output gives a concise work-in-progress
summary; add `--verbose` for the complete current gate errors. It reports
`preflight_status` and `finalizable_now` even when `FINALIZATION.json` is
missing. A missing record is a normal work-in-progress state and does not alone
make the command fail.

Work-in-progress validation still checks every populated record. In particular,
it rejects stale source locks, broken links, and inferential steps that do not
contain exactly one atomic move. It relaxes only final completeness. A zero
status for a coherent partial audit does not make it complete or final.

After finalization, `proofcheck.py status --root <audit-root>` recomputes artifact
hashes and the full gate, including source files, external source-evidence
files, and other locked evidence outside the audit workspace. It reports record
status, freshness, exact changed artifact paths, current gate errors, and
whether the finalization is usable. A stale, failed, or invalid finalization
returns a nonzero status. Do not write status output inside a finalized audit
root because that would mutate the sealed state. After any audit, source,
evidence, registry, scope, or validator change, rerun finalization rather than
citing the old record.

## Final language

Use "verified within the stated scope" only when all completion gates pass, and immediately define this as a non-formal audit judgment. Prefer "no defect found under the stated non-formal protocol." Otherwise say exactly what was checked and use conditional, gap, incorrect, unclear, or not-checked language.

Do not state that a paper, appendix, or theorem is correct when the audit covered only selected proof units or when a load-bearing dependency remains unchecked.

Do not infer that a theorem is false merely because its written proof is invalid. Report argument status and statement status separately.

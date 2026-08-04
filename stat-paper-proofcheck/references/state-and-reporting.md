# State, Resumption, and Reporting

## Audit workspace

Use `proofcheck.py scaffold` to create a project outside the skill directory:

```text
proofcheck-audit/
  AUDIT_MANIFEST.json
  CHECK_PLAN.md
  EXECUTION_ORDER.md
  PROGRESS.json
  audit/
    01_index/
      theorem_inventory.json
      cross_reference_audit.json
    02_ledgers/
    03_dependencies/
      DEPENDENCY_REGISTRY.json
      METHOD_INTERFACE_REGISTRY.json
    04_local_checks/
    05_adversarial/
    06_reports/
      ISSUE_LOG.json
      ISSUE_SUMMARY.md
      FINAL_REPORT.md
      FINALIZATION.json
```

Do not store paper-specific work inside the installed skill.

`AUDIT_MANIFEST.json` is the machine-readable scope and completion contract. Before finalization, set its reviewed depth, overall assessment, targets, in-scope and critical units, in-scope method interfaces, explicit exclusions with reasons, source or parser limits, inventory overrides, and completion evidence. For Focused depth, `target_units` must be nonempty and `in_scope_units` must equal the targets plus their exact transitive internal dependency closure. An inventory override may add a parser-missed manual unit, correct or reject a proof location, or confirm, replace, or reject a proof association only when it records a reason and rendered-source evidence. A manual unit binds `reviewed_unit_sha256`. An explicit rejection uses a null reviewed proof and a reviewed association with status `rejected`, method `reviewed_rejection`, the same target, and no evidence occurrences. Source-lock and rescan every changed proof span, then reconcile its exact reference occurrences, dependencies, and citations. Do not edit the source snapshot to make drift disappear. Re-scaffold or deliberately update and recheck affected work after a source change.

The manifest records the skill version, artifact schemas, closure contract
version, validator hash, and source snapshot identifier. A validator change
invalidates that protocol identity until the audit is deliberately migrated or
rerun. Keep proof, dependency-closure, and method-interface contracts distinct
so a new registry or interface record does not silently reinterpret older proof
ledgers.

The current release remains skill version `1.0`; its finalizable protocol uses
artifact schema `4`, evidence contract `3`, and closure contract `2`.

Use `closure_contract_version: 2` in `DEPENDENCY_REGISTRY.json`. Its `review`
object must have `status: reviewed`, the exact manifest
`source_snapshot_sha256`, the current `inventory_sha256`, the exact ordered
`in_scope_units`, and substantive `evidence`. A changed source snapshot,
inventory file, or scope makes the review binding stale. Rebind it only after
rechecking the affected registry records.

An audit created before these protocol fields existed is a legacy artifact, not evidence that its checker violated later rules. Label it with the protocol and scope actually used. Re-scaffold or explicitly migrate and recheck it before making a current-protocol finalization claim.

The `source_discovery` record distinguishes recursively discovered LaTeX inputs, local class and package files, explicitly declared sources, and supplemental project-local `.fls` inputs. An outside-project recorder input remains excluded until it is explicitly promoted as an additional source with a reason and evidence. Treat an `.fls` trace as evidence from one compilation path, not as a completeness certificate.

`parser_warning_reviews` must be a one-to-one review of the exact current warning set. Use `confirmed_non_load_bearing` only with concrete evidence, `scope_limitation` when the unresolved reach is bounded and declared, and `unresolved` otherwise. An unresolved warning, or a limitation that may affect in-scope units, cannot support `no_defect_found`.

Manifest `cross_reference_reviews` must be a one-to-one review of the exact
current broken-reference and duplicate-label records. Orphan labels do not
require rows. Each record contains `kind`, `key`, exact `locations`, `status`,
substantive `evidence`, `affected_units`, and `issue_ids`. Use only `passed`,
`defect`, or `inconclusive`. The affected units and issues must agree with the
scope, canonical issue log, global source-resolution row, and final report.

## Checkpoint contract

At the end of every session or before a handoff, update `PROGRESS.json` with:

- `source_snapshot_sha256` equal to the current manifest snapshot;
- the current pass and active unit;
- completed, conditional, blocked, and not-started units;
- open S0 and S1 issue IDs;
- parser or source limitations;
- the exact next action.

Keep state factual. Do not mark a unit complete merely because a draft ledger
exists. At finalization, require `completed_units` to equal the in-scope set
exactly, `conditional_units` to equal the exact set of ledgers with
`unit_status: conditionally_verified`, `blocked_units` to be an empty object,
`not_started_units` to be empty, and `open_high_priority_issues` to equal the
sorted set of open or deferred S0 and S1 issue IDs. Reject duplicates, unknown
IDs, missing IDs, and stale snapshot bindings.
## Resume contract

On resumption:

1. Read `AUDIT_MANIFEST.json` and `PROGRESS.json`.
2. Run `proofcheck.py status --root <audit-root>`.
3. Check source hashes before trusting prior ledgers.
4. Check the dependency-registry review binding, obligation hashes, and locked
   external source-evidence hashes.
5. Read the active unit, its dependencies, and open issue records.
6. Continue from the exact next action rather than repeating completed work.

If source drift affects a checked unit, mark that unit stale and re-extract it. Preserve unaffected audit records. If the paper's theorem statement changes, re-evaluate downstream dependencies even when proof text is unchanged.

Because finalization locks the full include closure, any included-file change
invalidates the audit-wide source snapshot. Determine the affected units,
refresh the snapshot transparently, recheck all context and dependencies whose
meaning could have changed, and then renew the registry review binding.

External `source_evidence` files are locked independently by file hash. A
changed or missing evidence file makes its external record and every associated
use stale even when the manuscript snapshot is unchanged.

Method-interface records independently lock manuscript, pseudocode, code, and configuration spans. A code snapshot can support a code-to-target or code-to-documentation judgment without being part of the LaTeX include closure. If the inspected revision, configuration, preprocessing, or caller inputs are not tied to reported experiments, execution provenance remains not checked.

Before a writing or reviewer handoff, pass `METHOD_INTERFACE_REGISTRY.json`, `ISSUE_LOG.json`, and the source snapshot identifier with the manuscript. For every resolved method-interface issue, preserve its semantic contract. After an edit, treat a changed authoritative supporting span as stale, recheck the protected meaning and dependent claims, then update the contract. Do not retain `resolved` merely because another sentence appears similar.

## Blocked and conditional work

When a dependency or source is missing, mark the affected unit conditional or blocked, record what is needed, and continue only with independent units. Do not fill missing material from memory.

When user judgment is needed, isolate the smallest concrete choice and explain how each option changes the audit. Keep already established facts stable.

## Final report contract

Use `assets/templates/FINAL_REPORT.md`. Report:

1. overall verdict, exact target results, and exact checked scope;
2. source revision, closure contract version, and tooling limitations;
3. main theorem chain, with the exact unit-level status and component judgments
   for every in-scope result, plus one exact conclusion-judgment row per `Cxxx`
   conclusion;
4. the generated issue summary, which preserves `finding_status` and exact
   `affected_results`;
5. external-result status through the dependency-closure table and exact set
   fields;
6. proposed repairs, separated from findings;
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

Include exactly one independent-challenge row for every critical unit. Match
challenge status, independence level, challenger and reconciled verdicts,
ordered disagreements, resolution, and artifact to the unit ledger exactly.

Also include a method-interface table with the canonical issue ID, finding
class, interface ID, estimator-target status, implementation inspection status,
both code-comparison verdicts, and execution-provenance status. These eight
values must match the registry and issue log exactly. State whether an
implementation result came from static inspection, execution, or both. Set the
last table cell to the exact ordered issue evidence followed by the exact
ordered downstream consequences, using the format specified in the template.

Treat these report fields as exact machine-reconciled sets: `Target results`, `Checked scope`,
`Results not checked`, `External results checked`, `External results not
checked`, and `Highest-consequence issue`. Write sorted IDs separated by a comma
and one space, with no trailing punctuation. Write exactly `none` for an empty
set. Use `none` for `Tooling, extraction, or rendering limitations` only when no
such limitation exists. Use only the exact independence enum values
`none`, `fresh_context_same_model`, `different_model`, or `independent_human`;
when more than one value applies, list the unique values in sorted
comma-separated form.

Set `Overall assessment code` to exactly `no_defect_found`, `defects_found`, or
`inconclusive`, matching `AUDIT_MANIFEST.json`. The finalizer derives precedence
from the evidence: a recorded defect overrides inconclusive units, and
inconclusive units override a no-defect assessment. Set `Closure contract
version` to exactly `2`.

Generate issue counts with `proofcheck.py issues --write-summary`. Do not type
competing counts manually. Copy only the generated full-field Issues table into
the report's Issue summary section, or write exactly `No issues.` when the log
is empty. Reconcile the main-theorem rows, dependency-closure
rows, generated issue summary, exact set fields, and protocol fields against the
canonical JSON records. Do not duplicate the full external-use records, global
consistency matrix, issue-impact table, or result-status sections in the report;
those remain canonical in the main-theorem table,
`DEPENDENCY_REGISTRY.json`, manifest completion checks, and `ISSUE_LOG.json`.

Before release, set `PROGRESS.json` status to `complete`, apply the exact progress
partition rules above, and run:

```bash
python scripts/proofcheck.py issues --root <audit-root> --write-summary --final
python scripts/proofcheck.py finalize --root <audit-root>
```

The final command writes `FINALIZATION.json` with pass or fail status, protocol
identity, closure contract version, source snapshot identifier, file-level
audit-artifact manifest, audit-state hash, and validation errors. Treat that
generated file as the persisted gate result.

Before finalization, `proofcheck.py status --root <audit-root>` always runs the
current gate as a preflight. It reports `preflight_status`, `finalizable_now`,
and populated `current_gate_errors` even when `FINALIZATION.json` is missing.
A missing record is a normal work-in-progress state and does not alone make the
command fail.

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

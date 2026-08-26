# State, Resumption, and Reporting

## Audit workspace

Use `proofcheck.py scaffold` to create a project outside the skill directory:

```text
proofcheck-audit/
  AUDIT_MANIFEST.json
  CHECK_PLAN.md                 generated projection
  EXECUTION_ORDER.md            generated projection
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
    07_runtime/                 optional observational usage telemetry
```

Do not store paper-specific work inside the installed skill.

`AUDIT_MANIFEST.json`, `PROGRESS.json`, ledgers, registries, and
`ISSUE_LOG.json` are canonical. `CHECK_PLAN.md`, `EXECUTION_ORDER.md`, and
`audit/03_dependencies/dependency_graph.md` are concise deterministic views.
Generate or refresh them instead of editing them:

```bash
python "<skill-root>/scripts/proofcheck.py" sync-views --root <audit-root>
```

The generated views must be current for finalization. The `finalize` command
refreshes and seals them; run `sync-views` earlier when the projections are
useful during work. They never supply a missing scope, dependency, status, or
judgment. Keep temporary primary or challenge packets and compact annotation
inputs outside the audit root. They are context-transfer aids, not canonical
evidence or final deliverables. A primary packet is nevertheless a mandatory
binding input to `compile-annotations`; the source-locked skeleton and compiled
ledger remain inside `audit/04_local_checks`.

## Portable setup and environment boundary

Invoke `proofcheck.py` through the directory containing the loaded
`SKILL.md`, not through a path relative to the caller's current directory. Run
`doctor` before scaffold or resume when the source, output directory, working
directory, or platform has changed:

```bash
python "<skill-root>/scripts/proofcheck.py" doctor --mode new --paper <source> --output <audit-root> --input-kind latex --portable-sources
```

Use `--mode new` before scaffold and `--mode resume` for an existing audit.
New mode rejects any existing destination. Resume mode requires a readable
audit manifest and a supplied paper whose hash matches the recorded
authoritative paper. `doctor` leaves no probe residue. It checks that
Python 3.10 or later is running, the source is a supported regular file, its
required provenance is available, and the destination can be safely created
or written. A process-start failure
occurs before the skill can create a diagnostic record. Whether the failure is
reported by `doctor` or by the surrounding execution environment, stop and
label the requested audit output `NONFINAL` with reason
`environment_blocked`. Do not continue through an ad hoc review and present it
as a completed proofcheck run.

Use `--portable-sources` when the audit may move between folders or systems. It
copies the authoritative source closure into `audit/00_sources/`, locks the
copied bytes, and makes those bundled files authoritative. Original absolute
locations remain nonauthoritative provenance only. Portable LaTeX sources must
use relative local references, and `--project-root` must contain every file in
the authoritative source closure. If a relative include escapes that boundary,
scaffold fails without committing an audit; rerun with a broader common root.
Do not rewrite `\input`, `\include`, class, package, or bibliography paths to
make the bundle appear self-contained. Move the whole audit root,
not selected state files. After moving it, run `status` and `delivery-check`;
their hash and closure checks determine whether the bundle remains usable.

Canonical paths stored inside JSON use `/`, including on Windows, and relative
paths resolve from the audit root or the record-specific documented base.
Readers normalize legacy relative paths containing `\`. They reject a foreign
absolute path rather than interpreting it as a relative path or silently
rebinding it. Re-scaffold with `--portable-sources` when a legacy audit depends
on unavailable absolute locations.

Scaffold and state-changing commands commit complete files atomically. A
failed or interrupted commit must leave either the prior valid file or no
committed workspace, never a partially written canonical record. Recovery and
issue archives are byte copies with hashes; they must not depend on filesystem
hard-link support or shared inode identity. If interruption recovery cannot be
validated, keep the audit `NONFINAL` and report the exact stale or malformed
artifact.

`AUDIT_MANIFEST.json` is the machine-readable scope and completion contract. Before finalization, set its reviewed depth, overall assessment, targets, in-scope and critical units, in-scope method interfaces, explicit exclusions with reasons, source or parser limits, inventory overrides, and completion evidence. For Focused depth, `target_units` must be nonempty and `in_scope_units` must equal the targets plus their exact transitive internal dependency closure. An inventory override may add a parser-missed manual unit, correct or reject a proof location, confirm, replace, or reject a proof association, or designate an exact external restatement only when it records the required source-bound evidence. A manual unit binds `reviewed_unit_sha256`. An explicit rejection uses a null reviewed proof and a reviewed association with status `rejected`, method `reviewed_rejection`, the same target, and no evidence occurrences. An external restatement override uses `kind: external_restatement`, exact `unit_id`, `external_dependency_use_id`, `statement_sha256` equal to the hash of the exact reviewed formal statement span, substantive `reason`, and substantive `evidence`. Keep the unit proof-required and its proof null. Its ledger uses `coverage_mode: external_restatement`, repeats the designated use ID, and covers exactly the statement. That ID must name one external direct dependency of the unit and exactly one matching registry use. Citation keys equal the statement citations mapped to it, or the empty set when no citation command exists. Source-lock and rescan every changed proof span or statement-only restatement, then reconcile its exact reference occurrences, dependencies, and citations. Do not edit the source snapshot to make drift disappear. Re-scaffold or deliberately update and recheck affected work after a source change.

The manifest records the skill version, artifact schemas, closure contract
version, validator hash, and source snapshot identifier. When only the
validator implementation hash changes and all schema and contract versions
remain current, status reports `validator_revalidation_required`. Run:

```text
python "<skill-root>/scripts/proofcheck.py" revalidate-protocol --root <audit-root>
```

The command checks source freshness and current record readability before it
updates only the validator hash. It invalidates any prior finalization and does
not transfer a mathematical judgment. Resolve every current gate error and
finalize again. Validator hashing normalizes CRLF and CR text newlines to LF,
so equivalent checkouts retain one validator identity across platforms. A
schema or contract-version change still requires deliberate
migration and rechecking. Keep proof, dependency-closure, and method-interface contracts distinct
so a new registry or interface record does not silently reinterpret older proof
ledgers.

The current release remains skill version `1.0`; its finalizable protocol uses
artifact schema `5`, evidence contract `4`, and closure contract `3`.

Use `closure_contract_version: 3` in `DEPENDENCY_REGISTRY.json`. Its `review`
object must have `status: reviewed`, the exact manifest
`source_snapshot_sha256`, the current `inventory_sha256`, the exact ordered
`in_scope_units`, and substantive `evidence`. A changed source snapshot,
inventory file, or scope makes the review binding stale. Rebind it only after
rechecking the affected registry records.

Artifacts using schema `4`, evidence contract `3`, or closure contract `2`
are inspection-only. Their prior status is historical evidence under the older
contract, not a current finalization. Re-scaffold or explicitly migrate every
affected record, recheck its source, inference, dependency, issue, challenge,
and reporting evidence, and rerun the current gates before making a
current-protocol claim.

To create a schema-5 skeleton from one legacy schema-4 ledger, run:

```text
python "<skill-root>/scripts/proofcheck.py" migrate-ledger <legacy.ledger.json> --output <schema5.ledger.json>
```

The command never overwrites the legacy ledger. It creates a nonfinal
source-unit skeleton and resets the review verdicts, independent challenge, and
steps rather than transferring prior mathematical judgments. Final mode
remains blocked until a full manual atomic recheck reconstructs the ledger and
sets `migration.status` to `rechecked` with substantive
`migration.recheck_evidence` and a valid UTC `migration.rechecked_utc`.

When a report outside the canonical `audit/06_reports/FINAL_REPORT.md` will be
delivered to the user, declare it in the top-level optional manifest
`report_deliverables` list. Each row contains `id` in the form `R001`
(`R` plus three digits), `role: user_facing_report`, `path`,
`sha256`, `issue_ids`, and
`overall_verdict`. The path and hash must be current, `issue_ids` must equal
the canonical issue set exactly, and `overall_verdict` must equal the
canonical final report's `Overall assessment code`. The delivered file itself
must render the same canonical issue ID set. Its `Verdict` section, when the
canonical report has that heading, and its `Audit boundary and limitations`,
`Main theorem chain`, `Conclusion judgments`, `Dependency closure`, `Issue
index`, `Detailed findings`, `Independent critical-path challenges`,
`Method-interface findings`, `Computational evidence`, `Unchecked scope`, and
`Assurance boundary` sections must match the canonical report exactly. A
different title and extra orientation prose are allowed. Do not declare a
draft, partial export, or summary that does not meet this contract as a
delivered report.

Reserve the top level of `audit/06_reports/` for
`FINAL_REPORT.md`, `ISSUE_SUMMARY.md`, and complete manifest-declared
user-facing reports. Move drafts, partial reports, and working notes elsewhere.
An undeclared Markdown file in this directory is a report-integrity error and
makes `status` nonzero. The scaffolded `FINAL_REPORT.md` contains a visible
`NONFINAL SCAFFOLD` notice and the title `NONFINAL Proof-Check Working Report`.
Keep both until the canonical report and generated issue views are complete
and `completion.final_report_ready` is true. Then rename the title to
`Final Proof-Check Report`, remove the notice, and run the status,
issue-reconciliation, finalization, and delivery sequence. The finalization
gate rejects either nonfinal marker.

The `source_discovery` record distinguishes recursively discovered LaTeX inputs, local class and package files, explicitly declared sources, and supplemental project-local `.fls` inputs. An outside-project recorder input remains excluded until it is explicitly promoted as an additional source with a reason and evidence. Treat an `.fls` trace as evidence from one compilation path, not as a completeness certificate.

`parser_warning_reviews` must be a one-to-one review of the exact current warning set. Use `confirmed_non_load_bearing` only with concrete evidence, `scope_limitation` when the unresolved reach is bounded and declared, and `unresolved` otherwise. Use `external_restatement` only for the missing-associated-proof warning of the same explicitly overridden unit, with `affected_units` containing exactly that unit and substantive evidence. An unresolved warning, or a limitation that may affect in-scope units, cannot support `no_defect_found`.

Manifest `cross_reference_reviews` must be a one-to-one review of the exact
current broken-reference and duplicate-label records. Orphan labels do not
require rows. Each record contains `kind`, `key`, exact `locations`, `status`,
substantive `evidence`, `affected_units`, and `issue_ids`. Use only `passed`,
`defect`, or `inconclusive`. The affected units and issues must agree with the
scope, canonical issue log, global source-resolution row, and final report.

## Checkpoint contract

After validating every completed ledger, at the end of every session, and
before a handoff, write `PROGRESS.json` through the checkpoint command. Choose
exactly one active-unit option and supply a specific next action:

```bash
python "<skill-root>/scripts/proofcheck.py" checkpoint --root <audit-root> --active-unit <unit-id> --next-action "<specific action>"
python "<skill-root>/scripts/proofcheck.py" checkpoint --root <audit-root> --clear-active-unit --next-action "<specific action>"
```

The command derives `current_pass`, the completed, in-progress, and not-started
unit sets, and the conditional subset from canonical scope and ledger state. It
keeps the active unit and next action explicit and preserves only validated
blockers and source or parser limits. Do not hand-edit derived progress fields.

Use these exact `current_pass` milestones:

| Pass | Milestone |
|---|---|
| 0 | Reserved for pre-work or legacy bootstrap; a normal scaffold starts at pass 1. |
| 1 | Establishing scope and source is underway. |
| 2 | Scope and source are reviewed; proof-system mapping is incomplete. |
| 3 | Proof-system mapping is reviewed, but at least one scoped obligation is not fully source-locked and normalized. |
| 4 | All scoped obligations are normalized; local atomic checking is incomplete. |
| 5 | All local ledgers are complete; dependency, method-interface, global, or adversarial checks are incomplete. |
| 6 | Dependency, method-interface, global, and adversarial checks are complete; effective-critical challenges are incomplete. |
| 7 | Effective-critical challenges are complete; the final report is not declared ready. |
| 8 | The final report is declared ready; the strict candidate finalization gate alone controls `complete` versus `in_progress`. |

The checkpoint refuses source-snapshot or include-closure drift rather than
rewriting progress against stale source. On a successful checkpoint, it
migrates a legacy progress record that lacks `in_progress_units` by writing the
derived field. It rejects an active unit already present in the derived
`completed_units` set. At pass 8, it places the newly supplied `next_action`
into the candidate progress record
before running the strict gate, so that gate validates the new value. If the
gate fails, checkpoint records `status: in_progress`, never `complete`.

Keep the explicit state factual. Do not mark a unit complete merely because a
draft ledger exists. At finalization, require `completed_units` to equal the
in-scope set exactly, `conditional_units` to equal the exact set of ledgers
with `unit_status: conditionally_verified`, `blocked_units` to be an empty
object, `in_progress_units` and `not_started_units` to be empty, and
`open_high_priority_issues` to equal the sorted set of open or deferred S0 and
S1 issue IDs. Reject duplicates, unknown IDs, missing IDs, and stale snapshot
bindings.

Compute the effective critical set as manifest `critical_units` plus every
in-scope unit in `affected_results` for an open, deferred, or resolved
load-bearing S0 or S1 issue. Challenge completion and pass-7 readiness use this
effective set, not the manifest list alone. A resolved severe issue requires a
fresh post-repair challenge with its issue ID in `covered_issue_ids`.

## Resume contract

On resumption:

1. Run `proofcheck.py status --root <audit-root>` before loading substantive
   audit content.
2. Inspect the reported source and protocol freshness, active unit, bounded
   gate errors, and exact next action.
3. For an active or next unit, generate a current primary packet with
   `packet --root <audit-root> --unit-id <unit-id> --mode primary --output
   <packet.json>` outside the audit root and load that packet rather than the
   whole workspace. If its obligation is absent, normalize the fresh extracted
   skeleton or ledger before semantic checking and regenerate the packet.
4. Inspect `resume.wip.included`. Reuse partial semantic work only when it is
   true; otherwise recheck the affected work rather than reconstructing it
   from conversation or prose notes.
5. Load separately only external evidence or canonical issue records named by
   that packet and needed for the next action.
6. Continue from the recorded next action without rereading completed ledgers,
   report artifacts, or unrelated source.
7. If status reports source, obligation, dependency, external-evidence, or
   protocol drift, identify and recheck the bounded affected set before
   trusting its prior semantic judgments. Do not reuse a verdict across a
   changed binding merely because the unit ID or prose appears unchanged.

`status` is work-in-progress aware and concise by default. It distinguishes a
healthy incomplete audit from stale or malformed state and from an audit that
is finalizable now. Use `status --verbose` to show the full gate errors. Both
modes apply the same strict validation and finalization gates.

The packet is an optional minimal context projection for manual ledger work,
but it is mandatory for `compile-annotations`. It is not a substitute for
`status`. The compiler requires the exact current primary packet, rebuilds it
from canonical audit state, and rejects a modified or stale copy. Compile only
against a fresh `.skeleton.json` inside the audit root whose normalized
obligation the annotations actually address. Keep the packet outside the audit
root and bind the annotations to its exact `context_binding_sha256`.

To make a partial canonical ledger resumable, copy the primary packet's
`work_context_sha256` to the ledger's top level when saving the partial work.
This digest binds the protocol, source and obligation, manifest, reviewed
inventory, dependency registry, issue log, and their model-visible semantic
projections. A regenerated packet includes partial work only when the ledger
passes nonfinal local validation and this digest still matches. In that case,
`resume.wip` contains `included: true`, the exact partial-ledger hash, and the
full reusable semantic record with `source_units`, `steps`, and `review`.
Treat any other WIP projection as navigation only. Do not reuse its semantic
judgments after source, obligation, manifest, inventory, dependency, issue, or
protocol drift.

A zero exit from bare `status` means that the audit is coherent enough to
resume. It does not mean that the audit is complete. Read the top-level
`audit_complete`, `delivery_status`, and `finalization_gate_error_count`
fields. The nested progress candidate gate count is evaluated only when a
pass-8 completion candidate exists and is not the full gate count. Use
`status --require-finalized` when an orchestration step must fail unless a
current usable passed finalization exists. Use `delivery-check` for release.

If source drift affects a checked unit, mark that unit stale and re-extract it. Preserve unaffected audit records. If the paper's theorem statement changes, re-evaluate downstream dependencies even when proof text is unchanged.

Because finalization locks the full include closure, any included-file change
invalidates the audit-wide source snapshot. Determine the affected units,
refresh the snapshot transparently, recheck all context and dependencies whose
meaning could have changed, and then renew the registry review binding.

External `source_evidence` files are locked independently by file hash. A
changed or missing evidence file makes its external record and every associated
use stale even when the manuscript snapshot is unchanged.

Method-interface records independently lock manuscript, pseudocode, code, and configuration spans. A code snapshot can support a code-to-target or code-to-documentation judgment without being part of the LaTeX include closure. If the inspected revision, configuration, preprocessing, or caller inputs are not tied to reported experiments, execution provenance remains not checked.

## Optional usage telemetry

Usage telemetry is observational only. It is not proof evidence and does not
affect any mathematical or completion judgment. When the user requests it,
record exactly one event for each actual model call. Set `work_packets` to the
number of complete unit or external-result packet contexts processed in that
call. Record a retry, correction call, or challenger call as a separate event;
do not record deterministic `proofcheck.py` commands as model calls.

For example:

```bash
python "<skill-root>/scripts/proofcheck_usage.py" record --root <audit-root> --event-id call-001 --stage primary --work-packets 1 --unit-id <unit-id> --input-tokens 12000 --cached-input-tokens 8000 --output-tokens 3000 --reasoning-tokens 1500 --token-source measured --cache-outcome hit
python "<skill-root>/scripts/proofcheck_usage.py" summary --root <audit-root> --format markdown
```

Event IDs must be unique. Use `--token-source measured` for tool-reported
counts, `reported` for another stated count, and `unavailable` when no token
count exists. A measured or reported event needs at least one numeric token
field; an unavailable event must omit all token counts. Record
`--cache-outcome` as `hit`, `miss`, or `not_used` without inferring a hit from
a lower token count.

The helper writes `audit/07_runtime/RUN_USAGE.json`. Record events only before
a current usable finalization. When present, the file is sealed in the audit
artifact manifest. After usable finalization, run only the read-only `summary`
command. Absence of telemetry neither weakens nor strengthens the audit.

## Resolve an issue without erasing its evidence

Archive before repair. First identify every open or deferred issue whose
historical evidence could be changed by the repair. Complete and finalize the
audit while all of those issues and their exact failures still resolve. Then
archive each issue:

```bash
python "<skill-root>/scripts/proofcheck.py" archive-issue --root <audit-root> --issue-id I-001
```

Do not edit source, ledgers, dependencies, contracts, challenges, or reports
until every repair-affected issue has been archived. Because each archive
changes the issue log and makes the prior finalization stale, rerun
finalization before the next archive when needed. The command refuses a stale
or failed finalization and will not overwrite
`audit/06_reports/history/I-001-origin.json`.

The command adds `historical_origin` to the issue. That compact object
records the archive path and hash, prior source snapshot, and historical
required units, dependency uses, challenges, and report deliverables. The
archive itself binds byte-exact prior source and canonical audit artifacts to
the prior passed finalization. Its mandatory `prior_artifacts` members are
the manifest, issue log, final report, inventory, dependency registry,
method-interface registry, and required ledgers. Each uses `file`, `sha256`, and
`content_base64`. Its `prior_sources` list must equal the sealed
prior manifest's complete source-snapshot membership. The validator checks the
decoded bytes against both their stored hashes and the prior finalization or
source snapshot. It recomputes ledger-move failures from sealed ledgers,
method-interface failures from the sealed method-interface registry, and
global-check failures from the sealed manifest's global consistency pass.

After repair, retain the archived top-level `origin_ref` only as the
issue's historical identity. Keep `contract_refs` and
`affected_results` current. Record current repair provenance under
`current_resolution`, including its disposition, clean
`current_ref` or null removal, old-to-new mapping, locked evidence,
retired dependency uses, `verified_sufficient` status, and the complete
historical-current recheck union. Rebuild every affected ledger and dependency,
run fresh issue-aware challenges, regenerate reports, checkpoint, and finalize
again.

A `removed` disposition retires only the failed origin inside a retained,
cleanly rechecked affected result. It does not remove a theorem or unit from
audited scope. Handle whole-result retirement as a separate audit with an
explicitly reviewed new scope.

Use the complete field and retirement contract in
[evidence-status-and-issues.md](evidence-status-and-issues.md). Never create the
archive retroactively after a repair because the old exact source and failure
chain are no longer independently recoverable.

Before a writing or reviewer handoff, pass `METHOD_INTERFACE_REGISTRY.json`, `ISSUE_LOG.json`, and the source snapshot identifier with the manuscript. For every resolved method-interface issue, preserve its semantic contract. After an edit, treat a changed authoritative supporting span as stale, recheck the protected meaning and dependent claims, then update the contract. Do not retain `resolved` merely because another sentence appears similar.

## Blocked and conditional work

When a dependency or source is missing, mark the affected unit conditional or blocked, record what is needed, and continue only with independent units. Do not fill missing material from memory.

When user judgment is needed, isolate the smallest concrete choice and explain how each option changes the audit. Keep already established facts stable.

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

Include exactly one independent-challenge row for every effective-critical
unit. Match challenge status, independence level, challenger and reconciled
verdicts, ordered disagreements, resolution, and artifact to the unit ledger
exactly. An `agreed` challenge has identical challenger and reconciled verdicts
equal to the final unit status, with no disagreements. A `resolved` challenge
has a reconciled verdict equal to the final unit status, at least one recorded
disagreement, and a substantive resolution.
For each row, `covered_issue_ids` must equal the exact sorted triggering
open, deferred, or resolved S0 or S1 issue set, which is empty for a
manifest-only critical unit. The
recorded `source_snapshot_sha256`, `challenged_ledger_sha256`,
`challenge_context_sha256`, `challenge_artifact_sha256`, and `generated_utc`
must be current. `issue_assessments` must cover `covered_issue_ids` exactly and
must preserve each current target-contract hash and substantive target and
downstream assessment. Render `Issue assessments` as a compact JSON array sorted
by `issue_id`. Within each object, use this exact key order: `issue_id`,
`target_contract_sha256`, `assessment`, `target_assessment`,
`downstream_assessment`. Render `Disagreements` as a compact JSON array in
canonical ledger order. Escape a literal pipe inside either Markdown cell as
`\|`.

Before rendering this table, run `proofcheck.py bind-challenge --root
<audit-root> --unit-id <unit-id>` for every required challenger. The command
embeds the exact unit, context hash, challenger verdict, and canonical
assessment rows in the artifact and updates `challenge_artifact_sha256`. The
artifact binding and ledger must agree at both progress and finalization gates.

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

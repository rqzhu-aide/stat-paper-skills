# Workspace and Resume

This file is the canonical contract for portable setup, source state, checkpoints, resumption, and blocked work. Issue repair belongs to [issues-and-repairs.md](issues-and-repairs.md); release belongs to [reporting-and-release.md](reporting-and-release.md).

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

State-changing replacements commit complete files atomically. No-overwrite
publication uses a hard link or an exclusive rename when supported, with a
hash-verified exclusive-copy fallback on other filesystems. It never replaces
an existing path. If interruption leaves an incomplete newly created fallback
file, later validation rejects it; keep the audit `NONFINAL` and report the
exact malformed artifact. Recovery and issue archives are byte copies with
hashes and never depend on shared inode identity.

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

Report-directory integrity, deliverable declarations, and the transition from
the nonfinal report scaffold are defined in
[reporting-and-release.md](reporting-and-release.md).

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

Challenge completion and pass-7 readiness use the effective-critical set from
[challenge-protocol.md](challenge-protocol.md), not the manifest list alone.

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
but it is mandatory for compile-annotations. It is not a substitute for
status. The compiler rebuilds current canonical state, verifies both packet
binding hashes, and requires exact equality of the dependency-closed semantic
projection. Compile only against a fresh .skeleton.json whose normalized
obligation the annotations address. Keep packet and annotations outside the
audit root and bind annotations to context_binding_sha256.

The semantic binding covers protocol, source snapshot, exact unit source,
normalized obligation, unit inventory and candidate paths, direct dependency
contracts and external evidence, relevant issue triggers, dependency alignment,
and all risk aspects. A separate operational_binding records raw manifest,
inventory, registry, issue-log, progress, and semantic-artifact file hashes plus
readiness and resume state. Operational drift remains traceable but does not
by itself invalidate a mathematical judgment.

To make a partial canonical ledger resumable, copy work_context_sha256 from the
primary packet to the ledger. A regenerated packet includes partial work only
when the ledger passes nonfinal local validation and the dependency-closed work
context still matches. Then resume.wip includes the exact partial-ledger hash
and full reusable source_units, steps, and review. Recheck after relevant
source, obligation, dependency, external-evidence, issue-trigger, risk, or
protocol drift. Do not discard sound WIP merely because progress, next action,
or unrelated metadata changed.

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


## Blocked and conditional work

When a dependency or source is missing, mark the affected unit conditional or blocked, record what is needed, and continue only with independent units. Do not fill missing material from memory.

When user judgment is needed, isolate the smallest concrete choice and explain how each option changes the audit. Keep already established facts stable.

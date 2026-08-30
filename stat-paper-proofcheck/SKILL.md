---
name: stat-paper-proofcheck
metadata:
  version: "1.2"
description: Formal line-by-line proof audit for statistics, probability, machine-learning theory, econometrics, biostatistics, mathematics, and theoretical computer science, with mandatory source-line coverage, atomic inference checking, dependency closure, instantiated counterexamples, independent challenges, and evidence-backed final reports. This is heavyweight, multi-session work. Run it only when the user explicitly invokes /stat-paper-proofcheck (Codex, $stat-paper-proofcheck) or asks by name for a formal proofcheck audit. Never start it because a conversation merely involves a proof; answer casual proof questions directly and mention the command instead. Diagnose rather than silently repairing proofs.
---

# Statistical Paper Proofcheck

## Explicit invocation only

Start Triage, Focused, or Full only after the user invokes
`/stat-paper-proofcheck` or requests a formal proofcheck by name. Otherwise
confirm first. This gate does not stop workers, challengers, or canary checkers
inside an active audit; they read only assigned references and packets.

The Agent Skills spec allows no frontmatter gate, so the description above
instructs every host. Claude Code and Cowork enforce it mechanically via
`{"skillOverrides": {"stat-paper-proofcheck": "user-invocable-only"}}` in
settings JSON (or Space on the skill in the `/skills` menu); Codex reads
`agents/openai.yaml` (`allow_implicit_invocation: false`).

## Core standard

Determine whether each stated conclusion follows from the exact assumptions,
definitions, prior results, and written proof steps available at its point of
use. Cover every physical source line and reconstruct every substantive
transition as an independently checkable inference.

Check contract fidelity, argument validity, statement status, dependency
closure, and later-use sufficiency separately. Check domain, dimension, sign,
constant, rate, probability, quantifier, and limit risk for every substantive
step. An invalid proof does not by itself show that its conclusion is false.

Diagnose the written proof. Do not silently supply a missing argument, weaken a
claim, strengthen an assumption, or edit the manuscript unless the user
separately asks for revision after the audit.

## Load only the current role

Audit obligations accumulate in canonical state. Reference files do not
accumulate in every worker context. The coordinator enforces stages that a
worker does not load.

| Current role or trigger | Read |
|---|---|
| Triage only | This entrypoint and read-only parser outputs |
| New or resumed audit coordinator | [workspace-and-resume.md](references/workspace-and-resume.md) |
| Checker calibration session | [checker-calibration.md](references/checker-calibration.md); a canary checker reads only its packet |
| Inventory, dependency mapping, global consistency, or closure | [proof-system-audit.md](references/proof-system-audit.md) |
| Primary proof-unit checker | [line-by-line-protocol.md](references/line-by-line-protocol.md) and [evidence-and-verdicts.md](references/evidence-and-verdicts.md) |
| Probability, asymptotic, optimization, matrix, causal, machine-learning, lower-bound, or analytic risk | Only the matching section of [domain-risk-checks.md](references/domain-risk-checks.md) |
| Load-bearing cited theorem or external technical fact | [external-result-verification.md](references/external-result-verification.md) |
| Create, propagate, archive, repair, or resolve an issue | [issues-and-repairs.md](references/issues-and-repairs.md) |
| Fresh-context challenger | [challenge-protocol.md](references/challenge-protocol.md) and the exact challenge packet only |
| Final report or release | [reporting-and-release.md](references/reporting-and-release.md) |
| First unfamiliar JSON record | Search the relevant object in [AUDIT_RECORD_EXAMPLES.json](assets/templates/AUDIT_RECORD_EXAMPLES.json); do not load the whole file |
| Persistent schema or gate error | The matching record in the finalized example under [assets/reference-audit/](assets/reference-audit/README.md); load only that file |
| Challenge artifact | Start from [CHALLENGE_ARTIFACT.md](assets/templates/CHALLENGE_ARTIFACT.md), then run bind-challenge |

The legacy evidence-status-and-issues.md and state-and-reporting.md filenames
are compatibility routes only. The table above names the canonical files.

## Select audit depth

- Triage maps proof architecture, suspicious transitions, missing sources, and
  a verification plan. It makes no correctness claim and does not finalize.
- Focused completely checks target results and their exact transitive internal
  prerequisite closure.
- Full checks every proof-required result, the main theorem chain, global
  consistency, adversarial cases, and declared scope.

Use Focused or Full when the user asks whether a proof is correct. If source
material is incomplete, give a bounded nonfinal assessment and name unavailable
dependencies. Every Focused or Full audit has at least one critical unit and a
fresh-context challenge; every target unit is critical, and a Full audit
should also set the manifest's `verified_challenge_sample_rate` so a
deterministic sample drawn from all in-scope units is independently challenged.

## Nonnegotiable invariants

- Lock source and normalize the obligation before judgment.
- Canonical JSON is authoritative; Markdown and prose are reviewed views.
- Cover every physical line and every substantive move at atomic granularity.
- Preserve exact source, dependency, issue, and checked-scope identity.
- Downgrade missing, stale, ambiguous, or incompatible evidence.
- Deterministic tooling owns hashes, source partitions, exact mirrors, graphs,
  progress, and generated views. It never invents a mathematical judgment.
- The checker owns normalization, premises, moves, side conditions, all eight
  risk dispositions, failure evidence, verdicts, and issue classification.
- Normally process one complete proof unit per packet and model call. Never
  truncate source or dependency evidence to preserve a batch.
- Model tiers may split cost, not judgment: a lighter model may draft
  transcription-grade fields, but statuses, risk dispositions, failures,
  side conditions, conclusion rows, issues, severities, and challenges belong
  to the strongest available model. Every gate holds regardless of author.
- Reuse work only while dependency-closed semantic inputs remain current.
  Operational progress and unrelated metadata remain provenance, not reasons
  to discard sound mathematical work.

## Workflow

### 1. Establish environment, scope, and source

Resolve scripts from the directory containing SKILL.md. Prefer LaTeX. For
PDF-only work, follow [line-by-line-protocol.md](references/line-by-line-protocol.md).
For a new audit, run the nonmutating preflight:

    python "<skill-root>/scripts/proofcheck.py" doctor --mode new --paper "paper.tex" --output "proofcheck-audit" --input-kind latex --portable-sources

If execution fails or doctor reports unreadable source or an unwritable
destination, stop with environment_blocked and NONFINAL. Do not substitute an
informal judgment or attempt system security repair.

Then create durable Focused or Full state:

    python "<skill-root>/scripts/proofcheck.py" scaffold --paper "paper.tex" --output "proofcheck-audit" --input-kind latex --portable-sources

Use scaffold help for PDF transcription, extra sources, .fls input, or project
boundaries. An .fls trace is not proof of complete source closure.

For an existing audit, run `status --root "<audit-root>"` first and resume from
canonical state. If the source location, output location, working directory, or
platform changed, also run `doctor --mode resume` with the recorded paper and
audit root. Never scaffold over an existing audit.

### 2. Calibrate the checker

Before Focused or Full local checking, follow
[checker-calibration.md](references/checker-calibration.md): create packets
outside the audit root, obtain fixed responses from one fresh checker context,
and grade both styles:

    python "<skill-root>/scripts/proofcheck.py" canary-grade --response "<flawed-or-correct-id>.response.json" --response "<other-style-id>.response.json" --session-id cal-001 --root "proofcheck-audit" --checker-profile-id "<profile-id>" --checker-configuration-id "<configuration-id>" --checker-context-id "<fresh-context-id>" --reviewed-binding

Finalization requires a passing, balanced latest session; missing or failing
evidence blocks it. Binding IDs are reviewed declarations, not runtime proof.
Fully recheck and replace or recompile hash-recorded preexisting ledgers. Never
open keys in a checking context.

### 3. Map the proof system

Review formal units, proof associations, cross-references, parser warnings,
direct and transitive dependencies, and later use sites. Parser output is an
index, not verification. Focused scope is the target plus exact prerequisites;
Full scope includes every proof-required unit. Record canonical decisions, then:

    python "<skill-root>/scripts/proofcheck.py" sync-views --root "proofcheck-audit"

### 4. Lock and normalize each proof unit

Lock the complete proof and exact statement, then extract a skeleton:

    python "<skill-root>/scripts/proofcheck.py" extract --file "<resolved-paper-file>" --start 120 --end 168 --statement-start 120 --statement-end 128 --unit-id lem-main --output "proofcheck-audit/audit/04_local_checks/lem-main.skeleton.json"

Resolve the authoritative paper path from AUDIT_MANIFEST.json. Complete the
normalized obligation, ordered Cxxx conclusions, exact spans, and all eight
normalization checks.

### 5. Check every line and atomic move

Read in source order. Every physical line belongs to one source unit, every
substantive source unit has a checked step, and every inferential step contains
one move. Record exact claims, anchored inputs, rule, justification, side
conditions, adversarial checks, all eight risk dispositions with local
evidence, calibrated status, and issue IDs.

Generate the complete primary packet outside the audit root:

    python "<skill-root>/scripts/proofcheck.py" packet --root "proofcheck-audit" --unit-id lem-main --mode primary --output "<primary-packet.json>"

Create and complete the deterministic draft:

    python "<skill-root>/scripts/proofcheck.py" annotation-scaffold "proofcheck-audit/audit/04_local_checks/lem-main.skeleton.json" --packet "<primary-packet.json>" --output "<lem-main.annotations.json>"

Mechanical prefills include hashes, mirrors, IDs, source ranges, risk slots,
and literal transcriptions. Replace every null with paper-specific analysis.
After packet regeneration, rebind only if `calibration_receipt_sha256` is
unchanged, then reconfirm affected judgments. Otherwise archive the old ledger
under a non-`.ledger.json` name, regenerate the packet, create a fresh scaffold,
and fully re-review. Then preflight and compile:

    python "<skill-root>/scripts/proofcheck.py" annotation-check "proofcheck-audit/audit/04_local_checks/lem-main.skeleton.json" --annotations "<lem-main.annotations.json>" --packet "<primary-packet.json>" --json
    python "<skill-root>/scripts/proofcheck.py" compile-annotations "proofcheck-audit/audit/04_local_checks/lem-main.skeleton.json" --annotations "<lem-main.annotations.json>" --packet "<primary-packet.json>" --output "proofcheck-audit/audit/04_local_checks/lem-main.ledger.json"

Compilation requires the exact dependency-closed semantic projection, runs full
final local ledger validation, and publishes without overwrite. A passed compile
receipt is the local gate for that unchanged file. Manual, moved, or modified
ledgers still require:

    python "<skill-root>/scripts/proofcheck.py" ledger-check "<unit.ledger.json>" --final

### 6. Close dependencies and issues

Reconcile every reference candidate, internal or external result, citation, and
later use in the exact form needed. Propagate load-bearing issues through the
exact dependent closure. ISSUE_LOG.json is the only issue-definition source.

Create or review a method-interface record when a load-bearing estimated or
algorithmic object has feasible constructions targeting materially different population quantities;
the manuscript claims feasible end-to-end validity
rather than only assuming an oracle object; or the user requests
method-to-implementation verification. An oracle nuisance used only as an
explicit theorem assumption does not trigger inspection. Record reviewed
`scope.trigger` as `required` or `not_required` with a reason. When required,
use the estimated-interface section of
[domain-risk-checks.md](references/domain-risk-checks.md) and the method-interface
judgments in [evidence-and-verdicts.md](references/evidence-and-verdicts.md).
Keep specification, estimator-to-target correspondence, code correspondence,
and execution provenance separate.

### 7. Challenge effective-critical units

Follow [challenge-protocol.md](references/challenge-protocol.md). Use a fresh
packet without primary reasoning, fix the blinded assessment before
reconciliation, then run:

    python "<skill-root>/scripts/proofcheck.py" bind-challenge --root "proofcheck-audit" --unit-id <unit-id>

### 8. Checkpoint and resume

At each completed unit, session boundary, and handoff:

    python "<skill-root>/scripts/proofcheck.py" checkpoint --root "proofcheck-audit" --active-unit <unit-id> --next-action "<specific action>"
    python "<skill-root>/scripts/proofcheck.py" issues --root "proofcheck-audit" --write-summary
    python "<skill-root>/scripts/proofcheck.py" status --root "proofcheck-audit"

Bare status means coherent to resume, not complete. Resume from status and the
active unit packet. Reuse partial semantics only when resume.wip.included is
true. Archive every repair-affected issue before changing its source or records.

### 9. Finalize and release

Build reports from canonical records and generated projections, then run:

    python "<skill-root>/scripts/proofcheck.py" checkpoint --root "proofcheck-audit" --clear-active-unit --next-action "Run final issue reconciliation and finalization."
    python "<skill-root>/scripts/proofcheck.py" issues --root "proofcheck-audit" --write-summary --write-report-views --final
    python "<skill-root>/scripts/proofcheck.py" sync-views --root "proofcheck-audit"
    python "<skill-root>/scripts/proofcheck.py" finalize --root "proofcheck-audit"
    python "<skill-root>/scripts/proofcheck.py" delivery-check --root "proofcheck-audit"

Deliver only when delivery_status is FINAL and usable_finalization is true.
Otherwise label the report NONFINAL. FINALIZATION.json is gate evidence, not a
formal proof certificate and not evidence that the audit found no defect.

## Nonnegotiable boundaries

- Do not infer correctness from plausibility, familiarity, compilation, or
  failure to find a counterexample.
- Do not mark a step verified from an unchecked standard argument or a citation
  not verified in the needed form.
- Do not replace a missing argument with one the authors could have written.
- Do not collapse proof validity, statement truth, dependency availability, or
  later-use sufficiency.
- Do not turn ambiguity into mismatch without authoritative source-locked
  evidence fixing both objects.
- Do not treat symbolic or numerical checks as a substitute for a general
  proof, though they may expose exact subclaims or counterexamples.
- Do not strengthen a canonical finding in downstream prose without new
  evidence and revalidation.
- Do not hide unchecked lines, dependencies, source changes, parser warnings,
  limitations, unresolved issues, or nonfinal state.
- Prefer "no defect found under the stated non-formal protocol" to an
  unqualified claim that a paper or proof is correct.

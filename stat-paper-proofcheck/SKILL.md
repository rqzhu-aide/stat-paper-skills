---
name: stat-paper-proofcheck
metadata:
  version: "1.0"
description: Audit proofs in statistics, probability, machine-learning theory, econometrics, biostatistics, mathematics, and theoretical computer science with mandatory source-line coverage and atomic inference checking. Use for line-by-line theorem or lemma verification, full appendix correctness audits, proof dependency and assumption checks, constants and rate propagation, probability and quantifier audits, external-theorem applicability, adversarial counterexample searches, multi-session proof-check projects, or evidence-backed final reports. Includes cross-platform tooling for LaTeX indexing, cross-references, source-locked line ledgers, issue consistency, and resumable audit state. Diagnose rather than silently repairing proofs.
---

# Statistical Paper Proofcheck

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
| Inventory, dependency mapping, global consistency, or closure | [proof-system-audit.md](references/proof-system-audit.md) |
| Primary proof-unit checker | [line-by-line-protocol.md](references/line-by-line-protocol.md) and [evidence-and-verdicts.md](references/evidence-and-verdicts.md) |
| Probability, asymptotic, optimization, matrix, causal, machine-learning, lower-bound, or analytic risk | Only the matching section of [domain-risk-checks.md](references/domain-risk-checks.md) |
| Load-bearing cited theorem or external technical fact | [external-result-verification.md](references/external-result-verification.md) |
| Create, propagate, archive, repair, or resolve an issue | [issues-and-repairs.md](references/issues-and-repairs.md) |
| Fresh-context challenger | [challenge-protocol.md](references/challenge-protocol.md) and the exact challenge packet only |
| Final report or release | [reporting-and-release.md](references/reporting-and-release.md) |
| First unfamiliar JSON record | Search the relevant object in [AUDIT_RECORD_EXAMPLES.json](assets/templates/AUDIT_RECORD_EXAMPLES.json); do not load the whole file |
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
fresh-context challenge.

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
- Reuse work only while dependency-closed semantic inputs remain current.
  Operational progress and unrelated metadata remain provenance, not reasons
  to discard sound mathematical work.

## Workflow

### 1. Establish environment, scope, and source

Resolve scripts from the directory containing SKILL.md. Prefer LaTeX. For
PDF-only work, follow [line-by-line-protocol.md](references/line-by-line-protocol.md).
For a new audit, run the nonmutating preflight:

    python "<skill-root>/scripts/proofcheck.py" doctor --mode new --paper paper.tex --output proofcheck-audit --input-kind latex --portable-sources

If execution fails or doctor reports unreadable source or an unwritable
destination, stop with environment_blocked and NONFINAL. Do not substitute an
informal judgment or attempt system security repair.

Then create durable Focused or Full state:

    python "<skill-root>/scripts/proofcheck.py" scaffold --paper paper.tex --output proofcheck-audit --input-kind latex --portable-sources

Use scaffold help for PDF transcription, extra sources, .fls input, or project
boundaries. An .fls trace is not proof of complete source closure.

For an existing audit, run `status --root <audit-root>` first and resume from
canonical state. If the source location, output location, working directory, or
platform changed, also run `doctor --mode resume` with the recorded paper and
audit root. Never scaffold over an existing audit.

### 2. Map the proof system

Review formal units, proof associations, cross-references, parser warnings,
direct and transitive dependencies, and later use sites. Parser output is an
index, not verification. Focused scope is the target plus exact prerequisites;
Full scope includes every proof-required unit. Record canonical decisions, then:

    python "<skill-root>/scripts/proofcheck.py" sync-views --root proofcheck-audit

### 3. Lock and normalize each proof unit

Lock the complete proof and exact statement, then extract a skeleton:

    python "<skill-root>/scripts/proofcheck.py" extract --file <resolved-paper-file> --start 120 --end 168 --statement-start 120 --statement-end 128 --unit-id lem-main --output proofcheck-audit/audit/04_local_checks/lem-main.skeleton.json

Resolve the authoritative paper path from AUDIT_MANIFEST.json. Complete the
normalized obligation, ordered Cxxx conclusions, exact spans, and all eight
normalization checks. Finalizable contracts are artifact schema 5, evidence
contract 4, closure contract 3, and skill version 1.0.

### 4. Check every line and atomic move

Read in source order. Every physical line belongs to one source unit, every
substantive source unit has a checked step, and every inferential step contains
one move. Record exact claims, anchored inputs, rule, justification, side
conditions, adversarial checks, all eight risk dispositions with local
evidence, calibrated status, and issue IDs.

Generate the complete primary packet outside the audit root:

    python "<skill-root>/scripts/proofcheck.py" packet --root proofcheck-audit --unit-id lem-main --mode primary --output <primary-packet.json>

Create and complete the deterministic draft:

    python "<skill-root>/scripts/proofcheck.py" annotation-scaffold proofcheck-audit/audit/04_local_checks/lem-main.skeleton.json --packet <primary-packet.json> --output <lem-main.annotations.json>

Only hashes, exact mirrors, IDs, source line ranges, and risk slots are prefilled.
Nulls are unfinished judgments. Review source grouping and replace every null
with paper-specific analysis. Run aggregate preflight, then compile:

    python "<skill-root>/scripts/proofcheck.py" annotation-check proofcheck-audit/audit/04_local_checks/lem-main.skeleton.json --annotations <lem-main.annotations.json> --packet <primary-packet.json> --json
    python "<skill-root>/scripts/proofcheck.py" compile-annotations proofcheck-audit/audit/04_local_checks/lem-main.skeleton.json --annotations <lem-main.annotations.json> --packet <primary-packet.json> --output proofcheck-audit/audit/04_local_checks/lem-main.ledger.json

Compilation requires the exact dependency-closed semantic projection, runs full
final local ledger validation, and publishes without overwrite. A passed compile
receipt is the local gate for that unchanged file. Manual, moved, or modified
ledgers still require:

    python "<skill-root>/scripts/proofcheck.py" ledger-check <unit.ledger.json> --final

### 5. Close dependencies and issues

Reconcile every reference candidate, internal or external result, citation, and
later use in the exact form needed. Propagate load-bearing issues through the
exact dependent closure. ISSUE_LOG.json is the only issue-definition source.

Create or review a method-interface record when any condition holds:

- a load-bearing estimated or algorithmic object has feasible constructions
  targeting materially different population quantities;
- the manuscript claims consistency, applicability, or end-to-end validity for
  a feasible estimator, rather than only assuming an oracle object; or
- the user requests method-to-implementation verification.

An oracle nuisance used only as an explicit theorem assumption does not by
itself trigger implementation inspection. Always record reviewed
`scope.trigger` as `required` or `not_required` with an explicit reason. When
required, use the estimated-interface section of
[domain-risk-checks.md](references/domain-risk-checks.md) and the method-interface
judgments in [evidence-and-verdicts.md](references/evidence-and-verdicts.md).
Keep specification, estimator-to-target correspondence, code correspondence,
and execution provenance separate.

### 6. Challenge effective-critical units

Follow [challenge-protocol.md](references/challenge-protocol.md). Use a fresh
packet without primary reasoning, fix the blinded assessment before
reconciliation, then run:

    python "<skill-root>/scripts/proofcheck.py" bind-challenge --root proofcheck-audit --unit-id <unit-id>

### 7. Checkpoint and resume

At each completed unit, session boundary, and handoff:

    python "<skill-root>/scripts/proofcheck.py" checkpoint --root proofcheck-audit --active-unit <unit-id> --next-action "<specific action>"
    python "<skill-root>/scripts/proofcheck.py" issues --root proofcheck-audit --write-summary
    python "<skill-root>/scripts/proofcheck.py" status --root proofcheck-audit

Bare status means coherent to resume, not complete. Resume from status and the
active unit packet. Reuse partial semantics only when resume.wip.included is
true. Archive every repair-affected issue before changing its source or records.

### 8. Finalize and release

Build reports from canonical records and generated projections, then run:

    python "<skill-root>/scripts/proofcheck.py" checkpoint --root proofcheck-audit --clear-active-unit --next-action "Run final issue reconciliation and finalization."
    python "<skill-root>/scripts/proofcheck.py" issues --root proofcheck-audit --write-summary --write-report-views --final
    python "<skill-root>/scripts/proofcheck.py" sync-views --root proofcheck-audit
    python "<skill-root>/scripts/proofcheck.py" finalize --root proofcheck-audit
    python "<skill-root>/scripts/proofcheck.py" delivery-check --root proofcheck-audit

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

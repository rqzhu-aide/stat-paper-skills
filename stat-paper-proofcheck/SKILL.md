---
name: stat-paper-proofcheck
metadata:
  version: "1.5"
description: Rigorous line-by-line proof audit for statistics, probability, machine-learning theory, econometrics, biostatistics, mathematics, and theoretical computer science, with mandatory source-line coverage, atomic inference checking, dependency closure, instantiated counterexamples, independent checks of every in-scope unit, and evidence-backed final reports. This is heavyweight, multi-session work. Run it only when the user explicitly invokes /stat-paper-proofcheck (Codex, $stat-paper-proofcheck) or asks by name for a formal proofcheck audit. Never start it because a conversation merely involves a proof; answer casual proof questions directly and mention the command instead. Diagnose rather than silently repairing proofs.
---

# Statistical Paper Proofcheck

## Explicit invocation only

Start Triage, Focused, or Full only on `/stat-paper-proofcheck` invocation or a
formal proofcheck request by name; otherwise confirm first. Active workers read
only their assigned reference and packet.
Codex also uses `allow_implicit_invocation: false`; Claude Code and Cowork use
`{"skillOverrides": {"stat-paper-proofcheck": "user-invocable-only"}}`.

## Core standard

Check each conclusion against the exact assumptions, definitions, prior
results, and written steps available at its use. Cover every physical source
line and reconstruct every substantive inference.

Separate contract fidelity, argument validity, statement status, dependency
closure, and later-use sufficiency. Check domain, dimension, sign, constant,
rate, probability, quantifier, and limit risk for every substantive step.
An invalid proof need not have a false conclusion.

## Load only the current role

Load this entrypoint and only the current role's row.

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
| Final report, explicit legacy migration, or release | [reporting-and-release.md](references/reporting-and-release.md) |
| Unfamiliar JSON record | Search only the relevant object in [AUDIT_RECORD_EXAMPLES.json](assets/templates/AUDIT_RECORD_EXAMPLES.json) |
| Persistent schema or gate error | Load only the matching finalized-example record under [assets/reference-audit/](assets/reference-audit/README.md) |
| Reconciliation author | Use submit-reconciliation through [challenge-protocol.md](references/challenge-protocol.md) |

## Select audit depth

- Triage maps proof architecture, suspicious transitions, missing sources, and
  a verification plan, without correctness claims or finalization.
- Focused fully checks targets and their exact transitive internal prerequisites.
- Full checks every proof-required result, the main theorem chain, global
  consistency, adversarial cases, and declared scope.

Correctness questions require Focused or Full. For incomplete source, give a
bounded NONFINAL assessment naming
unavailable dependencies. `critical_units` controls priority only.

## Nonnegotiable invariants

- JSON is canonical; HTML and optional Markdown are generated views.
- Preserve exact source, dependency, issue, and checked-scope identity.
- Downgrade missing, stale, ambiguous, or incompatible evidence.
- Tooling owns hashes, source partitions, exact mirrors, graphs, progress, and
  generated views, never mathematical judgments.
- The checker owns normalization, mathematical judgments, failure evidence,
  and issue classification, including every atomic-move field below.
- Default to one complete proof unit per packet; never truncate evidence for a batch.
- Lighter models may draft transcription fields, not mathematical judgments.
- Reuse work only while dependency-closed semantic inputs remain current.

## Workflow

### 1. Establish environment, scope, and source

Resolve scripts from this skill directory. Prefer LaTeX; the primary protocol
covers PDF preparation. For a new audit:

    python "<skill-root>/scripts/proofcheck.py" doctor --mode new --paper "paper.tex" --output "proofcheck-audit" --input-kind latex --portable-sources
    python "<skill-root>/scripts/proofcheck_source_check.py" --paper "paper.tex" --input-kind latex
    python "<skill-root>/scripts/proofcheck.py" scaffold --paper "paper.tex" --output "proofcheck-audit" --input-kind latex --portable-sources

On `review_required`, follow [source-layout-diagnostics.md](references/source-layout-diagnostics.md) before calibration or bulk ledgers.

If preflight cannot read source or write output, report `environment_blocked`
and NONFINAL. Never scaffold over an existing audit. Resume with
`status --root "<audit-root>"`; also run doctor after relocation.

### 2. Calibrate and map the proof system

Calibrate before local checking. A profile/configuration change requires a new
passing balanced session and recheck; a context-only handoff does not. Keep
canary keys out of checking contexts.

Review inventory, proof associations, references, and candidate uses. Lock each
scoped statement and complete proof before normalization; check prerequisites
before dependents. Parser output is not mathematical evidence.

### 3. Check each complete unit

Use the primary protocol's packet, annotation scaffold, source-lookup, and
submit-unit commands. The checker authors judgments; tooling binds and validates
records. Complete one representative unit or short prerequisite chain with its
actual reference uses before expanding across the paper.

Normalize before judging validity. Record each substantive transition as an
atomic move with exact claims, inputs, rule, justification, side conditions,
adversarial evidence, all eight risk dispositions, status, and issue references.
Consumed setup facts need authorized origins; temporary hypotheses remain
attached to conditional claims until discharged.

Submission preserves prior evidence. Follow the primary renewal protocol for
changed inputs; run `ledger-check "<unit.ledger.json>" --final` after manual edits
or moves. Changed calibration requires full re-review.

### 4. Close dependencies and issues

Reconcile each exact internal/external use, required conclusion, applicability,
and locked context.
Derive later-use sufficiency from completed outgoing edges. ISSUE_LOG.json owns
findings: publish anchors after their origin ledger exists, then propagate
through exact uses. Complete primary, dependency, global, and issue closure;
pass `issues --before-challenge` before independent dispatch. Settle reference
roles and exact uses then to avoid invalidating completed challenges through
later record corrections.

Inspect method interfaces when implementations target different population
quantities, the paper claims more than an assumed oracle, or the user requests
method-to-implementation verification. Record `scope.trigger` as `required` or `not_required` with its reason.

### 5. Independently check every in-scope unit

Follow the challenge protocol with a complete blinded packet. Before
reconciliation, preserve per-conclusion judgments,
decisive reasons, and exact sources; recording retains the primary position separately:

    python "<skill-root>/scripts/proofcheck.py" record-challenge --root "proofcheck-audit" --unit-id <unit-id> --packet "<challenge-packet.json>" --response "<initial-response.json>"

Submit the authored reconciliation with `submit-reconciliation --root
"proofcheck-audit" --review "<review.json>"`. Recheck changed mathematics first;
unresolved disagreements remain NONFINAL. Never overwrite the initial response.
Historical audits retain their older challenge contract.

### 6. Checkpoint, report, and release

At unit completion and handoff, checkpoint the active unit and specific next
action, regenerate the issue summary, and read status. Status confirms resume
coherence, not completion. Archive repair-affected issues before changing their
source or records.

New reader reports are `proofcheck-report.html` beside the audit manifest;
`report --root "<audit-root>"` gives an honest NONFINAL working view. On current finalized audits, `report`,
`checkpoint`, and repeated `finalize` preserve delivered bytes; repair a working
copy. Rendering existing evidence needs no model call.

Finalize after clearing the active unit and completing all required work.
Deliver only if `delivery-check` returns `delivery_status: FINAL` and
`usable_finalization: true`. Passed finalization records completed evidence
checks, not formal certification or absence of defects.

## Nonnegotiable boundaries

- Do not infer correctness from plausibility, familiarity, compilation, or
  failure to find a counterexample.
- Do not mark a step verified from an unchecked standard argument or a citation
  not verified in the needed form.
- Do not replace a missing argument with one the authors could have written.
- Keep dependency availability separate from proof validity, statement truth,
  and later-use sufficiency.
- Do not turn ambiguity into mismatch without authoritative source-locked
  evidence fixing both objects.
- Do not treat symbolic or numerical checks as a substitute for a general
  proof, though they may expose exact subclaims or counterexamples.
- Do not strengthen a canonical finding in downstream prose without new
  evidence and revalidation.
- Do not hide unchecked lines, dependencies, source changes, parser warnings,
  limitations, unresolved issues, or nonfinal state.
- Prefer "no load-bearing defect found under the stated non-formal protocol" to an
  unqualified claim that a paper or proof is correct.

---
name: stat-paper-proofcheck
metadata:
  version: "1.0"
description: Audit proofs in statistics, probability, machine-learning theory, econometrics, biostatistics, mathematics, and theoretical computer science with mandatory source-line coverage and atomic inference checking. Use for line-by-line theorem or lemma verification, full appendix correctness audits, proof dependency and assumption checks, constants and rate propagation, probability and quantifier audits, external-theorem applicability, adversarial counterexample searches, multi-session proof-check projects, or evidence-backed final reports. Includes cross-platform tooling for LaTeX indexing, cross-references, source-locked line ledgers, issue consistency, and resumable audit state. Diagnose rather than silently repairing proofs.
---

# Statistical Paper Proofcheck

## Core standard

Determine whether each stated conclusion follows from the exact assumptions, definitions, prior results, and proof steps available at its point of use. Check constants, rates, probability levels, quantifiers, dimensions, domains, edge cases, and external results in the form actually needed.

Read every detailed proof unit in manuscript order. Cover every physical source line and reconstruct every substantive transition as an independently checkable inference. Do not skip a line because it looks routine.

Diagnose the written proof. Do not silently supply a missing argument or edit the manuscript to make the proof work. Record the stated argument, any failure, and any possible repair separately.

Keep contract fidelity, argument validity, statement status, dependency closure, and later-use sufficiency separate. An invalid proof does not by itself show that its conclusion is false.

Keep this skill self-contained. Do not invoke or depend on another reviewer, writing, or proof-check skill. Use other tools only to inspect in-scope sources, render documents, retrieve external publications, inspect implementation evidence, run exact computational checks, or execute the bundled validator.

Treat the result as a rigorous non-formal audit, not a kernel-checked proof certificate. Mechanical gates establish record completeness and internal consistency, not mathematical truth. Human judgment remains necessary for every high-consequence finding and final assessment.

## Load references only when needed

Read each selected reference completely before performing the stage that needs it. Routes are cumulative: a Full audit adds system and state references, then still uses the local protocol and evidence discipline for every checked unit.

| Current need | Read |
|---|---|
| Detailed proof-unit audit, source locking, PDF transcription, atomic checking, or local ledger validation | [line-by-line-protocol.md](references/line-by-line-protocol.md) |
| Verdicts, component judgments, severity, confidence, canonical issues, computational evidence, or challenger evidence | [evidence-status-and-issues.md](references/evidence-status-and-issues.md) |
| In a Focused or Full audit: inventory reconciliation, proof-association review, dependency closure, global consistency, or completion gates | [proof-system-audit.md](references/proof-system-audit.md) |
| Probability, asymptotic, optimization, matrix, empirical-process, causal, machine-learning, lower-bound, or analytic risk | Only the matching section of [domain-risk-checks.md](references/domain-risk-checks.md) |
| A cited theorem or external technical fact is load-bearing | [external-result-verification.md](references/external-result-verification.md) |
| Workspace setup, checkpoint, resume, source revision, handoff, finalization, or final report | [state-and-reporting.md](references/state-and-reporting.md) |
| First record of an unfamiliar JSON shape | Search the relevant top-level object in [AUDIT_RECORD_EXAMPLES.json](assets/templates/AUDIT_RECORD_EXAMPLES.json); do not load the entire file by default |
| Check plan, dependency view, execution order, or final report artifact | Use the corresponding file in `assets/templates/` only when creating that artifact |

For Triage, use read-only parser outputs to build a nonfinal architecture map and verification plan. Do not load full-system, reporting, or unrelated domain material. Apply the same narrow loading rule to an isolated local stage.

## Select the audit depth

- **Triage:** map the proof architecture, suspicious transitions, missing sources, and a verification plan. Do not make a correctness claim or run finalization.
- **Focused:** completely check one or more target results plus their exact transitive internal dependency closure, with source-line coverage.
- **Full:** check every proof-required result, the main theorem chain, global consistency, adversarial cases, and declared scope.

If the user asks whether a proof is correct, use Focused or Full depth. If source material is incomplete, give a bounded assessment and mark unavailable dependencies explicitly.

For a Focused or Full correctness judgment, resumable audit, or evidence-backed final report, create a durable audit workspace and run the applicable gates. A diagnostic review may stop earlier only when clearly labeled nonfinal.

Designate at least one critical unit for every Focused or Full audit, normally a target result or the main theorem, and require a fresh-context challenger pass.

## Workflow invariants

- Lock the source and normalize the stated claim before assigning a verdict.
- Treat canonical JSON records as authoritative; prose and Markdown are reviewed views.
- Work from fine-grained source and inference checks toward dependency and paper-level conclusions.
- Preserve exact dependency identity, source evidence, issue propagation, and checked versus unchecked scope.
- Downgrade the assessment when evidence is missing, stale, ambiguous, or incompatible.
- Never let a later explanation erase the location where an object, premise, or transition first failed.

## Workflow

### 1. Establish scope and source

Record the exact source files, revision or hashes, target statements, proof ranges, definitions, inherited assumptions, direct dependencies, later use sites, and audit depth. Normalize each target without strengthening or weakening it.

Prefer LaTeX source. For PDF-only work, follow the transcription and visual-comparison procedure in [line-by-line-protocol.md](references/line-by-line-protocol.md) and disclose the unavailable LaTeX-level checks.

Never project an excerpt-level conclusion onto an unseen paper or appendix.

For a durable Focused or Full audit, create the workspace outside the skill directory:

```bash
python scripts/proofcheck.py scaffold --paper paper.tex --output proofcheck-audit
```

Use `scaffold --help` for declared additional sources, an existing `.fls` trace, or a project boundary. Treat an `.fls` file as evidence from one compilation path, not as a completeness certificate. `scaffold` does not execute TeX.

### 2. Map the proof system

Before deep checking a broad source, inspect the static source closure, rendered paper, formal-unit inventory, proof associations, labels, cross-reference anomalies, dependencies, and parser warnings.

In Triage, inspect these outputs only to produce a nonfinal architecture map and verification plan. In Focused or Full depth, review them and follow [proof-system-audit.md](references/proof-system-audit.md) and [state-and-reporting.md](references/state-and-reporting.md) for exact reconciliation and override rules.

Treat parser output as an index, not verification. Do not delete or weaken parser-discovered facts. Source-lock and rescan any reviewed replacement proof span. A proof-required result with no genuine proof is a checked gap or unclear result, not an exclusion.

For Focused depth, set scope to the target units plus exactly their transitive internal prerequisites. For Full depth, include every proof-required inventory unit.

### 3. Lock and normalize each proof unit

Lock the complete proof and the exact formal statement. Keep a distant or cross-file statement as a separate locked statement span rather than widening the ledger across unrelated material.

Create a source-locked ledger, for example:

```bash
python scripts/proofcheck.py extract --file paper.tex --start 120 --end 168 --statement-start 120 --statement-end 128 --unit-id lem-main --output proofcheck-audit/audit/04_local_checks/lem-main.ledger.json
```

Use `extract --help` for a separate statement file. Follow [line-by-line-protocol.md](references/line-by-line-protocol.md) for the obligation contract, `Cxxx` conclusions, normalization evidence, exact field shapes, and placeholder restrictions.

The current finalizable protocol is skill version `1.0`, artifact schema `4`, evidence contract `3`, and closure contract `2`. Treat legacy artifacts as inspection-only until deliberately migrated and rechecked.

### 4. Verify sequentially at atomic granularity

First read the unit from its first line to its last to map definitions, assumptions, scope changes, dependencies, and the point where each conclusion is reached. Assign verdicts only after reconstructing the relevant evidence.

Partition every physical line into exactly one contiguous ledger step. Each substantive row must express one independently checkable move, except for a controlled indivisible source chain recorded under the strict rules in [line-by-line-protocol.md](references/line-by-line-protocol.md).

For every substantive move, perform:

1. **Literal check:** identify exactly what the source claims and whether all objects and scopes are defined.
2. **Inferential check:** derive the move from its recorded premises without importing an unstated fact.
3. **Adversarial check:** test weak assumptions, boundary and equality cases, signs, dimensions, events, and quantifier order.

Record exact premise origins, result uses, reference occurrences, citations, inference links, side-condition discharges, risk dispositions, support moves, and canonical issue IDs as specified in the local protocol. Recompute algebra, rates, probability accumulation, and limiting steps rather than relying on familiarity.

Use the calibrated unit and component judgments in [evidence-status-and-issues.md](references/evidence-status-and-issues.md). Preserve the difference between a proof gap, an invalid transition, source ambiguity, and an exact refutation of a conclusion.

### 5. Close dependencies and later uses

Give every internal or external result use one exact `Dxxx` identity. Bind each internal use to the precise dependency `Cxxx` conclusion and current contract, then check compatibility in the form actually needed. Derive availability conclusion by conclusion rather than from a unit-level summary.

Verify every load-bearing cited result from its exact source and for each separate manuscript use by following [external-result-verification.md](references/external-result-verification.md). An uninspected citation cannot support a verified dependency.

Check cycles, assumptions, definitions, notation, dimensions, constants, rates, probability events, quantifiers, regimes, downstream use sites, and issue propagation under [proof-system-audit.md](references/proof-system-audit.md). Apply only the relevant sections of [domain-risk-checks.md](references/domain-risk-checks.md).

#### Method-interface trigger

Create or review a method-interface record when at least one condition holds:

- a load-bearing estimated or algorithmic object has feasible constructions that can target materially different population quantities;
- the manuscript claims consistency, applicability, or end-to-end validity for a feasible estimator rather than only assuming an oracle object;
- the user requests method-to-implementation verification.

An oracle nuisance appearing only as an explicit theorem assumption does not by itself trigger implementation inspection. When no interface is triggered, record the reviewed `not_required` decision and reason. When triggered, use the estimated-interface sections of [domain-risk-checks.md](references/domain-risk-checks.md), [evidence-status-and-issues.md](references/evidence-status-and-issues.md), and [state-and-reporting.md](references/state-and-reporting.md). Keep manuscript specification, estimator-to-target correspondence, code correspondence, and execution provenance separate.

### 6. Challenge the critical path

For every critical unit, run a fresh-context challenger that sees the source and normalized obligation but not the primary verdict or proposed repair. Record the independence level, challenger verdict, disagreements, resolution, reconciled verdict, and artifact.

A same-context reread is not independent. If a challenger is unavailable, disclose the audit as single-pass and do not claim independent confirmation.

### 7. Validate records and maintain state

Validate each completed ledger:

```bash
python scripts/proofcheck.py ledger-check proofcheck-audit/audit/04_local_checks/lem-main.ledger.json --final
```

The local validator checks source coverage, hashes, record closure, exact links, statuses, and internal consistency. It does not establish mathematical truth or audit-wide dependency closure. Fix the record or downgrade the claim. Do not edit validator output to conceal a failure.

Keep `ISSUE_LOG.json` as the only issue-definition source. Propagate every open or deferred load-bearing issue through the exact dependent closure. At source changes, session boundaries, or handoff, update and check the state described in [state-and-reporting.md](references/state-and-reporting.md):

```bash
python scripts/proofcheck.py issues --root proofcheck-audit --write-summary
python scripts/proofcheck.py status --root proofcheck-audit
```

Use the `status` preflight to identify remaining gate errors. Do not trust stale source, evidence, registry, progress, or finalization hashes.

### 8. Finalize and report

After scope, ledgers, dependencies, issues, global checks, progress, and critical challenges are complete, run:

```bash
python scripts/proofcheck.py issues --root proofcheck-audit --write-summary --final
python scripts/proofcheck.py finalize --root proofcheck-audit
```

Treat `FINALIZATION.json` as persisted gate evidence, not as a proof certificate. A passing gate can close an audit that found defects or remained inconclusive; it does not imply `no_defect_found`.

Build the report from canonical records using [state-and-reporting.md](references/state-and-reporting.md) and [FINAL_REPORT.md](assets/templates/FINAL_REPORT.md). Preserve exact result, conclusion, dependency, issue, protocol, and checked-scope judgments. Keep proposed repairs separate from findings.

Do not call a proof checked unless all in-scope lines and substantive moves are covered, current dependencies close at their recorded status, source hashes are current, critical disagreements are reconciled, and scope is stated honestly. Prefer "no defect found under the stated non-formal protocol" to an unqualified claim that a proof is correct.

## Nonnegotiable boundaries

- Do not infer correctness from plausibility, familiarity, compilation, or failure to find a counterexample.
- Do not mark a step verified from an unchecked "standard" argument or a citation that was not verified in the needed form.
- Do not replace a missing argument with one the authors could have written.
- Do not collapse statement correctness, proof validity, dependency availability, or later-use sufficiency into one judgment.
- Do not collapse manuscript specification, estimator-target correspondence, implementation correspondence, or execution provenance into one judgment.
- Do not turn ambiguity into a mismatch without authoritative source-locked evidence fixing both objects.
- Do not treat symbolic or numerical checks as a substitute for a general proof, though they may expose exact subclaims or counterexamples.
- Do not strengthen a canonical finding in downstream prose without new evidence and revalidation.
- Do not hide unchecked lines, dependencies, source changes, parser warnings, limitations, or unresolved issues.

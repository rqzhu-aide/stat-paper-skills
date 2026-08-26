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

Resolve the bundled script from the directory containing this `SKILL.md`; do
not assume that the current working directory is the skill directory. Before
substantive work, run a nonmutating environment and source preflight:

```bash
python "<skill-root>/scripts/proofcheck.py" doctor --mode new --paper paper.tex --output proofcheck-audit --input-kind latex --portable-sources
```

If the execution environment cannot start the command, or if `doctor` reports
an unreadable source or unwritable destination, stop the proofcheck workflow.
Report the specific boundary as `environment_blocked`, label every requested
proofcheck deliverable `NONFINAL`, and do not substitute an informal proof
judgment. A retry may confirm a transient failure, but it must not weaken this
fail-closed rule. Do not attempt operating-system, sandbox, or global security
repair from this workflow.

For a durable Focused or Full audit, create the workspace outside the skill directory:

```bash
python "<skill-root>/scripts/proofcheck.py" scaffold --paper paper.tex --output proofcheck-audit --input-kind latex --portable-sources
```

Use `scaffold --help` for a PDF transcription, declared additional sources, an
existing `.fls` trace, or a project boundary. `--portable-sources` copies the
hash-locked authoritative source closure into the audit bundle so it can be
moved as one directory; omit it only when external source locations are an
intentional audit dependency. Portable LaTeX sources must use relative local
references, and `--project-root` must contain the full authoritative source
closure. If it does not, rerun with a broader project root; do not rewrite
source paths to force bundling. Treat an `.fls` file as evidence from one
compilation path, not as a completeness certificate. `scaffold` does not
execute TeX. A raw PDF is provenance, not line-audit text, and is rejected as
`--paper`; use a verified transcription plus `--publisher-pdf` as specified in
[line-by-line-protocol.md](references/line-by-line-protocol.md).

### 2. Map the proof system

Before deep checking a broad source, inspect the static source closure, rendered paper, formal-unit inventory, proof associations, labels, cross-reference anomalies, dependencies, and parser warnings.

In Triage, inspect these outputs only to produce a nonfinal architecture map and verification plan. In Focused or Full depth, review them and follow [proof-system-audit.md](references/proof-system-audit.md) and [state-and-reporting.md](references/state-and-reporting.md) for exact reconciliation and override rules.

Treat parser output as an index, not verification. Do not delete or weaken parser-discovered facts. Source-lock and rescan any reviewed replacement proof span. A proof-required result with no genuine proof is a checked gap or unclear result, not an exclusion. The only exception is an explicit `external_restatement` inventory override for a result that restates one externally verified result instead of giving a local proof. Keep that unit proof-required and in scope, use exact statement-only ledger coverage, and designate exactly one external dependency use as specified in [proof-system-audit.md](references/proof-system-audit.md).

For Focused depth, set scope to the target units plus exactly their transitive internal prerequisites. For Full depth, include every proof-required inventory unit.

### 3. Lock and normalize each proof unit

Lock the complete proof and the exact formal statement. Keep a distant or cross-file statement as a separate locked statement span rather than widening the ledger across unrelated material.

Create a source-locked ledger, for example:

```bash
python "<skill-root>/scripts/proofcheck.py" extract --file <resolved-manifest-paper-file> --start 120 --end 168 --statement-start 120 --statement-end 128 --unit-id lem-main --output proofcheck-audit/audit/04_local_checks/lem-main.ledger.json
```

Resolve `<resolved-manifest-paper-file>` from `AUDIT_MANIFEST.json` field
`paper_file` against the audit root. This is mandatory after
`--portable-sources`, because the bundled copy is authoritative. Use
`extract --help` for a separate statement file. Follow
[line-by-line-protocol.md](references/line-by-line-protocol.md) for the
obligation contract, `Cxxx` conclusions, normalization evidence, exact field
shapes, and placeholder restrictions.

The current finalizable protocol is skill version `1.0`, artifact schema `5`,
evidence contract `4`, and closure contract `3`. Artifacts using schema `4`,
evidence contract `3`, or closure contract `2` are inspection-only until
explicitly migrated and rechecked under the current contracts. Use
`python "<skill-root>/scripts/proofcheck.py" migrate-ledger <legacy.ledger.json> --output <schema5.ledger.json>`
only to create a nonfinal skeleton; complete the full manual atomic recheck
before finalization.

### 4. Verify sequentially at atomic granularity

First read the unit from its first line to its last to map definitions, assumptions, scope changes, dependencies, and the point where each conclusion is reached. Assign verdicts only after reconstructing the relevant evidence.

Partition every physical line into exactly one contiguous `source_unit`, then
reference those units from the inferential steps. Source units preserve source
layout; steps preserve mathematical atomicity. Each inferential step contains
exactly one move and declares `support_role` as `derivation` or `reuse`. Follow
the exact coverage, ordering, hashing, and support restrictions in
[line-by-line-protocol.md](references/line-by-line-protocol.md).

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

Treat the manifest critical units together with every in-scope result reached
by an open, deferred, or resolved load-bearing S0 or S1 issue as the effective
critical set. For every effective-critical unit, run an issue-aware fresh-context
challenger that sees the source and normalized obligation but not the primary
verdict or proposed repair. Record the exact triggering issue set, freshness
hashes, independence level, challenger verdict, disagreements, resolution,
reconciled verdict, and artifact.

Keep a resolved S0 or S1 issue in `covered_issue_ids` for the fresh
post-repair challenge. Resolution requires a current challenge of the repaired
state, not reuse of the pre-repair challenge.

A same-context reread is not independent. If a challenger is unavailable, disclose the audit as single-pass and do not claim independent confirmation.

### 7. Validate records and maintain state

Validate each completed ledger:

```bash
python "<skill-root>/scripts/proofcheck.py" ledger-check proofcheck-audit/audit/04_local_checks/lem-main.ledger.json --final
```

The local validator checks source coverage, hashes, record closure, exact links, statuses, and internal consistency. It does not establish mathematical truth or audit-wide dependency closure. Fix the record or downgrade the claim. Do not edit validator output to conceal a failure.

After every completed ledger, at every session boundary, and before handoff, write a deterministic checkpoint. Choose exactly one active-unit option and state the specific next action:

```bash
python "<skill-root>/scripts/proofcheck.py" checkpoint --root proofcheck-audit --active-unit <unit-id> --next-action "<specific action>"
python "<skill-root>/scripts/proofcheck.py" checkpoint --root proofcheck-audit --clear-active-unit --next-action "<specific action>"
```

Keep `ISSUE_LOG.json` as the only issue-definition source. Propagate every open or deferred load-bearing issue through the exact dependent closure. At source changes, session boundaries, or handoff, refresh the issue summary, checkpoint the current state, and inspect it as described in [state-and-reporting.md](references/state-and-reporting.md):

```bash
python "<skill-root>/scripts/proofcheck.py" issues --root proofcheck-audit --write-summary
python "<skill-root>/scripts/proofcheck.py" status --root proofcheck-audit
```

Before changing source or audit records to repair open or deferred issues,
identify the complete repair-affected issue set and seal every member's exact
failure and historical closure. The unresolved audit must first have a current
passed finalization:

```bash
python "<skill-root>/scripts/proofcheck.py" archive-issue --root proofcheck-audit --issue-id I-001
```

The command archives one issue and makes the prior finalization stale. When a
repair affects more than one issue, rerun finalization as required and archive
every affected issue before editing any shared source or audit record. Only
after the complete set is archived may the repair replace current source,
ledgers, dependencies, contracts, or propagation. Preserve the archived
`origin_ref` in the issue for identity, use `historical_origin` as
the immutable archive pointer, and describe current provenance in
`current_resolution`. Recheck the historical-current union of affected
units and dependency uses, record every retired use, run fresh resolved-issue
challenges, and reconcile declared report deliverables before setting the
issue to `resolved`.

Use the concise, work-in-progress-aware `status` preflight to identify the current state and next action. Add `--verbose` when full gate diagnostics are needed. Concise output does not weaken strict validation. Do not trust stale source, evidence, registry, progress, or finalization hashes.

Draft ledger validation relaxes final completeness only. It must still reject
malformed populated records, stale source locks, broken links, and an
inferential step that does not contain exactly one atomic move. A clean draft
check means only that the recorded work is structurally coherent so far. It is
not a verification judgment.

A zero exit from bare `status` means that the resumable state is coherent; it
does not mean that the audit is complete. Inspect the top-level
`audit_complete`, `delivery_status`, and `finalization_gate_error_count`
fields. Automation that requires completion must use
`status --require-finalized` or, for release, `delivery-check`. The nested
progress candidate gate count is not the full finalization-gate count.

If status reports `validator_revalidation_required` while the schema and
contract versions remain current, run
`python "<skill-root>/scripts/proofcheck.py" revalidate-protocol --root proofcheck-audit`.
This command checks current source and record readability before updating only
the validator implementation hash. It invalidates any prior finalization and
does not transfer a mathematical judgment. Rerun status, resolve every current
gate error, and finalize again.

Stored audit paths use portable `/` separators and resolve against the audit
root. The reader accepts legacy relative paths containing `\`, but never
guesses how to reinterpret a foreign absolute path. See
[state-and-reporting.md](references/state-and-reporting.md) before moving or
resuming an audit.

### 8. Finalize and report

After scope, ledgers, dependencies, issues, global checks, progress, and
effective-critical challenges are complete, write the final checkpoint and run:

```bash
python "<skill-root>/scripts/proofcheck.py" checkpoint --root proofcheck-audit --clear-active-unit --next-action "Run final issue reconciliation and finalization."
python "<skill-root>/scripts/proofcheck.py" issues --root proofcheck-audit --write-summary --write-report-views --final
python "<skill-root>/scripts/proofcheck.py" finalize --root proofcheck-audit
python "<skill-root>/scripts/proofcheck.py" delivery-check --root proofcheck-audit
```

Treat `FINALIZATION.json` as persisted gate evidence, not as a proof certificate. A passing gate can close an audit that found defects or remained inconclusive; it does not imply `no_defect_found`.

Deliver a proofcheck report only when `delivery-check` returns
`delivery_status: FINAL` and `usable_finalization: true`. Otherwise label the
report `NONFINAL`, even when an earlier finalization file or a plausible
diagnostic judgment exists.

Keep non-deliverable drafts and working notes outside `audit/06_reports`.
That directory may contain only the canonical Markdown reports and complete
user-facing reports declared in `report_deliverables`. The copied
`FINAL_REPORT.md` starts with the title `NONFINAL Proof-Check Working Report`
and a visible `NONFINAL SCAFFOLD` notice. Keep both while
`completion.final_report_ready` is not true. After the canonical report and
generated issue views are complete, set that field to true, rename the title
to `Final Proof-Check Report`, remove the notice, and run the full status,
issue-reconciliation, finalization, and delivery sequence. Leaving the notice
or the nonfinal title in place blocks finalization.

Build the report from canonical records using [state-and-reporting.md](references/state-and-reporting.md) and [FINAL_REPORT.md](assets/templates/FINAL_REPORT.md). Generate exact finding locations, mathematical contracts, failed moves with their premises and recorded failure evidence, downstream quotations, invalidation effects, and suggested changes from canonical issue references and locked source. Preserve exact result, conclusion, dependency, issue, protocol, and checked-scope judgments. Keep suggested changes separate from findings, and reconcile every manifest-declared user-facing report before delivery.

For a resolved issue, take the exact pre-repair failure only from its validated
history archive. Take contracts, propagation, current relation statuses, and
severity effects from the current canonical records. Never rewrite the
historical failure to resemble the repair.

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

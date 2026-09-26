---
name: stat-proof-check
metadata:
  version: "2.3.0"
description: Rigorous, non-formal proof audits of mathematical and statistical papers. Use only when the user explicitly invokes $stat-proof-check. Checks exact targets, substantive inferences, source coverage, and independent review. Diagnoses written arguments without silently repairing the manuscript.
---

# Statistical Paper Proofcheck

Run only on explicit invocation as `$stat-proof-check`. Preserve `allow_implicit_invocation: false` for
Codex and `{"skillOverrides": {"stat-proof-check": "user-invocable-only"}}`
for Claude Code and Cowork. An active audit may continue within its declared scope.

## Choose scope and workflow

- **Triage:** map the proof architecture, suspicious transitions, missing sources,
  and useful next examinations. Make no proof-correctness or completed-audit claim.
- **Focused:** fully examine the requested exact targets and the internal
  prerequisites needed by their arguments, including independent review and integration.
- **Full:** reconcile the proof-required inventory against the manuscript and
  supplements, then examine all in-scope written arguments, dependencies, global
  consistency, and required independent work.

Incomplete source or unfinished work requires an explicitly limited assessment.
Priority does not narrow coverage. Checking selected parts does not check a whole theorem.

For new audits and current databases, use [database-audit.md](references/database-audit.md).
SQLite is the authority; exports and HTML are views. A source-backed overview may
provide the starting statements and connections, but neither its selection nor a
source match supplies proof credit or an exhaustive audit inventory. Preserve
overview identities, selection, comparisons, and detailed audit records in shared use.

For an existing v1.5 folder, use [legacy-workflow.md](references/legacy-workflow.md)
until explicitly imported. Its ledger fields and commands do not apply to database work.

## Load the assigned role

| Role or need | Read |
|---|---|
| Coordinator starting or resuming database work | [database-audit.md](references/database-audit.md), [controller-workflow.md](references/controller-workflow.md), and [coordinator-protocol.md](references/coordinator-protocol.md) |
| Register or refine proof structure | [graph-records.md](references/graph-records.md) |
| Primary or independent mathematical checker | Assigned packet, its [primary](references/primary-checker.md) or [independent](references/independent-checker.md) brief and generated response guidance, [mathematical-checking.md](references/mathematical-checking.md), and [evidence-and-verdicts.md](references/evidence-and-verdicts.md) |
| Load-bearing external theorem or technical fact | [external-result-verification.md](references/external-result-verification.md) |
| Domain-specific inference | Only matching sections of [domain-risk-checks.md](references/domain-risk-checks.md) |
| Arrange reviewer qualification | Coordinator only: [database-qualification.md](references/database-qualification.md) |
| Reconcile independent judgments | [reconciler.md](references/reconciler.md) and generated exact-target guidance |

## Scientific standard

Check proofs by mathematical derivation. Do not run simulations, numerical
validation, parameter sweeps, random searches or empirical experiments. If a
substantive examination cannot verify a step, record the limitation as unable
to verify. Suggest optional numerical follow-up only for the user's separate
decision, without executing it.

Read the exact statements, applicable setup, complete proofs and continuations,
supplements, and relevant private macros. Confirm source boundaries before
claiming coverage; a complete set of registered excerpts may omit part of a proof.
For PDF sources, visually compare consequential formulas with their pages.

Normalize the exact target, including domains, ordered quantifiers, hypotheses,
constant dependencies, probability model, restrictions, and convergence mode.
Examine every substantive inference in scope. Show its actual calculation or
logical step, inputs, conditions, justification, and outcome. Register meaningful
intermediate equations or claims without requiring a node or risk form per line.

Keep separate the exact supplier application, the inference combining its inputs,
and final composition of the argument. A locally valid implication may depend on
unavailable or refuted premises. Scope and substitutions determine whether a fact
is available at its use; ownership, labels, and arrow color do not.

Save substantive reasoning, failures, discoveries, and unfinished questions
promptly. Batch coherent work and use generated response scaffolds. The model
discovers and examines the mathematics; the controller records and schedules it.

Preserve initial independent source-only review and its unchanged response before
reconciliation. Review additional substantive routes or changed conditions that
the reviewer did not examine, with their supplied reasoning explicitly identified.
Do not repeat review solely because equivalent routine detail received new IDs.

Separate source fidelity, local outcome, statement availability, and audit completion.
A completed audit may report gaps or refutations. A failed argument does not
refute its statement; a successful alternative does not erase the written defect.
Keep restricted repairs as separate targets and proposed arguments as separate
routes. Never edit the manuscript or silently replace its proof as part of checking.

Mechanical validity, familiar arguments, and failure to find a counterexample do
not establish mathematics. Report the precise examined scope and limitations;
prefer “no load-bearing defect found within the stated non-formal scope” to an
unqualified claim that a paper is correct.

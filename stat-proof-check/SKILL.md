---
name: stat-proof-check
metadata:
  version: "2.3.8"
description: Rigorous, non-formal proof audits of mathematical and statistical papers. Use only when the user explicitly invokes $stat-proof-check. Checks exact targets, substantive inferences, source coverage, and independent review. Diagnoses written arguments without silently repairing the manuscript.
---

# Statistical Paper Proofcheck

Run only when the user explicitly invokes `$stat-proof-check`.
Preserve this explicit-invocation policy in the host's skill settings when supported.
An active audit may continue within declared scope.

## Choose scope and workflow

- **Triage:** map proof architecture, suspicious steps, missing sources and next examinations.
  Make no correctness or completed-audit claim.
- **Focused:** examine requested exact targets and required internal prerequisites,
  including independent review and integration.
- **Full:** reconcile the manuscript/supplement inventory; examine all in-scope written
  arguments, dependencies, global consistency and required independent work.

Disclose unfinished work and source limits. Priority does not narrow coverage;
checking parts does not check the whole theorem.

Use [database-audit.md](references/database-audit.md) for setup and folder/collision rules.
Use `proof-check-<paper-name>/{audit.db,report.html,work/}`; deliver report/database links.
Start independently of proof-graphify from the manuscript; resume existing audits in place.
SQLite is authoritative; exports and HTML are views.

Follow the three stages in [controller-workflow.md](references/controller-workflow.md):

1. Prepare evidence, graph and primary examination across the declared scope.
2. Review independently, integrate and reconcile, finish global checks, and freeze the audit results.
3. Produce the Archify HTML from the frozen results.

Keep one primary owner per proof where useful and save coherent batches. Stage 2 normally waits
for Stage 1; an explicit ready-subset exception preserves unfinished scope. Completed mathematical
gaps can advance; unresolved source mismatches cannot. Retry presentation failures only in Stage 3.

Existing v1.5 folders use [legacy-workflow.md](references/legacy-workflow.md) until imported;
legacy ledger fields/commands do not apply to database work.

## Load the assigned role

| Role or need | Read |
|---|---|
| Coordinator | [database-audit.md](references/database-audit.md), [controller-workflow.md](references/controller-workflow.md), and [coordinator-protocol.md](references/coordinator-protocol.md) |
| Author proof structure | [graph-records.md](references/graph-records.md) |
| Primary/independent checker | Assigned packet, its [primary](references/primary-checker.md) or [independent](references/independent-checker.md) brief and generated response guidance, [mathematical-checking.md](references/mathematical-checking.md), and [evidence-and-verdicts.md](references/evidence-and-verdicts.md) |
| Load-bearing external theorem or technical fact | [external-result-verification.md](references/external-result-verification.md) |
| Domain-specific inference | Only matching sections of [domain-risk-checks.md](references/domain-risk-checks.md) |
| Arrange reviewer qualification | Coordinator only: [database-qualification.md](references/database-qualification.md) |
| Reconcile independent judgments | [reconciler.md](references/reconciler.md) and generated exact-target guidance |

## Scientific standard

Check by mathematical derivation. Do not run simulations, numerical validation,
parameter sweeps, random searches or empirical experiments. Record unverified steps
as unable to verify. Suggest numerical follow-up only for the user's separate decision.

Read exact statements, setup, full proofs/continuations, supplements and relevant macros.
Verify source boundaries beyond registered excerpts. Visually check consequential PDF formulas.

Normalize domains, ordered quantifiers, hypotheses, constant dependencies, probability
model, restrictions and convergence. For each substantive inference, show calculations,
inputs, conditions, justification and outcome. Register meaningful intermediate claims;
avoid a node or risk form per line.

Separate supplier application, joint inference and final composition. Valid implications
may have unavailable or refuted premises. Scope and substitutions determine availability
at a use; ownership, labels and arrow color do not.

Save reasoning, failures, discoveries and unfinished questions in coherent generated scaffolds.
Checkers examine mathematics; the controller records it.

Preserve the initial source-only review unchanged before reconciliation. Review unseen
substantive routes or changed conditions, explicitly identifying supplied reasoning.
New IDs for equivalent routine detail alone do not require reexamination.

Separate source fidelity, local outcome, statement availability and audit completion.
Completed audits may report gaps/refutations. Failed arguments do not refute their
statements; alternatives do not erase written defects. Keep restricted repairs as
separate targets and proposed routes separate. Never edit the manuscript
or silently replace its proof.

Mechanical validity, familiarity and failure to find counterexamples do not establish mathematics.
State examined scope/limitations; prefer “no load-bearing defect found within the stated
non-formal scope” over unqualified correctness.

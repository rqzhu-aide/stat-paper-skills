---
name: stat-paper-writing
metadata:
  version: "1.2"
description: Author-side drafting, restructuring, polishing, and presentation-audit for statistics, machine learning, econometrics, biostatistics, causal inference, and computational statistics manuscripts. Use for exposition, argument order, English, notation, terminology, register, supplied citations and cross-references, and main/supplement coordination. In mixed requests, use only for explicit writing or revision, never referee judgment. It does not validate proofs, sources, code, numerical results, novelty, or publication suitability.
---

# Statistical Paper Writing

## Author-side contract

Use only supplied claims, results, figures, definitions, citations, and interpretations. Never invent support, assumptions, mechanisms, findings, novelty, contribution identities, or consequences.

Make surgical changes and leave clear text alone. Preserve objects, targets, relations, quantifiers, negation, conditioning, convergence, oracle or feasible status, numbers, anchors, labels, cross-references, and boundaries. Keep protected tokens and macros literal unless normalization is authorized.

For formal material, check presentation and documentary consistency only. Never judge proof truth or completeness, assumption or rate correctness, source truth, code equivalence, numerical correctness, novelty, merit, or publication suitability. Preserve attribution. For formal proof correctness or completeness, recommend explicit `$stat-paper-proofcheck` invocation; do not start it implicitly.

The request controls intervention. An audit diagnoses and reports without rewriting. A polish or revision performs its checks privately and directly returns or applies every safe supported edit. Add no audit labels or avoidable questions. Combined audit and revision records findings first, then applies supported repairs; only Full audit freezes. Ask only when conflicts or missing support prevent safe text.

Honor scope: local work cannot redesign, and focus-only excludes other checks.

## Orient, then route by action

Before acting, recover the target's job, objects, support, dependencies, and evidence.

For a full audit, load [revision-audit.md](references/revision-audit.md) before orientation; load no repair guidance then.

Choose the action route before the section route:

| Action | Required guidance |
|---|---|
| Draft from supported material | One section guide; first add [support-and-author-decisions.md](references/support-and-author-decisions.md) only when inputs are sparse, incomplete, conflicting, or high risk |
| Prose or structural revision | [polishing-protocol.md](references/polishing-protocol.md) |
| Substantive revision involving logic and terminology or register | [polishing-protocol.md](references/polishing-protocol.md) and [wording-register.md](references/wording-register.md) |
| Proof prose revision, even one sentence | [polishing-protocol.md](references/polishing-protocol.md) and [theoretical-proofs.md](references/theoretical-proofs.md) |
| Local terminology, tone, evidence verbs, or software-manual register | [wording-register.md](references/wording-register.md) |
| Quick or section presentation audit | [quick-section-audit.md](references/quick-section-audit.md); add one section guide when its job is in scope, then [reporting-and-validation.md](references/reporting-and-validation.md) when reporting |
| Full writing and presentation audit | [revision-audit.md](references/revision-audit.md); use the Full audit only harness below |
| Deliberate planning | [argument-architecture.md](references/argument-architecture.md) |
| Manuscript-wide terminology or naming provenance | [terminology-audit.md](references/terminology-audit.md) |
| Combined audit and revision | Record findings first; freeze only a Full audit, then load guidance for authorized edits |

For drafting, structural revision, or section audit, use one active section guide. Change it with the active section; add a second concurrently only for two distinct jobs in that section. For local polish, add one only when the section job affects the edit.

| Section or object | Guide |
|---|---|
| Abstract, introduction, or related work | [introduction.md](references/introduction.md) |
| Method, estimator, algorithm, or construction | [method-description.md](references/method-description.md) |
| Definitions, assumptions, or theorem statements | [theoretical-statements.md](references/theoretical-statements.md) |
| Proof exposition, roadmap, lemma presentation, or proof organization | [theoretical-proofs.md](references/theoretical-proofs.md) |
| Simulation, computation, application, figure, table, or results prose | [numerical-experiments.md](references/numerical-experiments.md) |
| Discussion, limitations, or conclusion | [discussion.md](references/discussion.md) |
| Appendix or supplement architecture | [appendix-architecture.md](references/appendix-architecture.md) |

For paper-level abstract or introduction positioning, add [argument-architecture.md](references/argument-architecture.md). For an appendix, add another guide only for the affected module.

## High-risk trigger routing

Load [support-and-author-decisions.md](references/support-and-author-decisions.md) when the task contains any of these triggers:

- missing or proposed assumptions, identification conditions, causal interpretations, or unsupported clean claims;
- conflicting definitions, formulas, algorithms, symbols, role labels, or empirical or procedural verbs;
- unclear oracle, feasible, empirical, or computational objects or operations;
- edits changing independence, implication, quantification, causality, evidentiary force, or another supplied relation;
- citation claims requiring narrowing to supplied source text;
- construction-to-theorem claims involving splits, folds, aggregation, or held-out steps;
- repairs requiring author choice or support.

Conditional routes:

- [argument-architecture.md](references/argument-architecture.md) for paper-level restructuring, contribution hierarchy, rank, spine, or ledger;
- [terminology-audit.md](references/terminology-audit.md) for conventionality, attribution, positioning, or manuscript-wide names;
- [numerical-experiments.md](references/numerical-experiments.md) for applications or disputed roles;
- [style-modes.md](references/style-modes.md) only for a genuine order, depth, or organization choice;
- [polishing-examples.md](references/polishing-examples.md) only for unresolved high-risk calibration or requested examples.

Load no reference for completeness and no script source merely to run its command.

## Workflows

- **Drafting:** map claims to support, exclude missing content, follow the section guide, introduce local objects before collections, and distinguish population, oracle, feasible, asymptotic, and finite objects.
- **Revision:** build the [polishing-protocol.md](references/polishing-protocol.md) meaning lock privately, then revise directly from fine to coarse without overriding protected distinctions.
- **Planning:** return an anchored move map without editing. **Structural revision:** build a private meaning lock and edit directly using the section guide.
- **Quick or section audit:** follow only the applicable prefix of [quick-section-audit.md](references/quick-section-audit.md) and stop at the requested granularity.

### Full audit only

Use [scripts/writer_audit.py](scripts/writer_audit.py) only for a full manuscript presentation audit. Other routes must not initialize it.

Inventory the source, included TeX, bibliography, supplement, rendered output, figures, and in-scope artifacts before orientation. Repeat `--source` for every supplied file; the harness does not infer TeX closure.

    python "SKILL_DIR/scripts/writer_audit.py" init --audit-root "AUDIT_DIR" --skill-root "SKILL_DIR" --source "SOURCE" --action audit

Use `audit-and-revise` only with revision authority. Resume from the snapshot:

    python "AUDIT_DIR/protocol/scripts/writer_audit.py" status --audit-root "AUDIT_DIR" --json

Never scaffold over an existing audit. After orientation, use [quick-section-audit.md](references/quick-section-audit.md) for shared passes. Passes are checkpoints, not mandatory calls; reuse one anchored map and reopen only needed spans.

Record findings once. Read [reporting-and-validation.md](references/reporting-and-validation.md), then [full-audit-operations.md](references/full-audit-operations.md) for workspace, closure, and publication. Load [full-audit-data-contract.md](references/full-audit-data-contract.md) only when editing canonical records, binding artifacts, or preparing freeze/publication; never for initialization, orientation, status-only resume, or completed output. For audit-and-revise, freeze diagnosis before edits.

## Validate and deliver

After drafting or revision, compare source and result for protected mathematical and documentary content and recheck affected contracts. Compile or render editable source when possible and inspect the affected output; otherwise state the limitation.

For drafting, return the requested section or outline and a separate **Author information needed** list when missing inputs materially limit support or completeness.

For polishing, provide or apply the text. Mention only substantive changes, material relation removals, and unresolved author decisions unless a detailed log is requested.

For audits, follow [reporting-and-validation.md](references/reporting-and-validation.md). Report consequential findings, not routine stylistic preferences.

Before returning, keep U+2013 and U+2014 out of assistant-authored commentary and assistant-authored canonical audit or report fields. Preserve either character when it belongs to supplied or revised manuscript text, stated venue typography, or exact source-derived evidence or metadata. Never claim independent validation of mathematics, sources, code, numerical results, novelty, or scientific merit.

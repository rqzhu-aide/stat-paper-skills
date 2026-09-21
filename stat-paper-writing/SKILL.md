---
name: stat-paper-writing
metadata:
  version: "1.5.1"
description: Author-side drafting, restructuring, polishing, and presentation-audit for statistics, machine learning, econometrics, biostatistics, causal inference, and computational statistics manuscripts. Use for exposition, argument order, English, notation, terminology, register, supplied citations and cross-references, and main/supplement coordination. In mixed requests, use only for explicit writing or revision, never referee judgment. It does not validate proofs, sources, code, numerical results, novelty, or publication suitability.
---

# Statistical Paper Writing

## Author-side contract

Use supplied research. Preserve mathematical objects, assumptions, relations, scope, evidence strength, numbers, citations, labels, and protected tokens. Equivalent explanations may clarify supplied mathematics; do not invent support, findings, novelty, or consequences. Leave clear text alone.

An audit diagnoses without rewriting. A polish or revision checks privately and directly applies supported edits within scope. Combined audit and revision records findings before repairs. Ask only when missing support or competing scientific choices prevent safe text; continue independent work. The detailed decision rule is in [support-and-author-decisions.md](references/support-and-author-decisions.md).

Check presentation and documentary consistency. For proof correctness or completeness, recommend explicit `$stat-paper-proofcheck` invocation; do not start it implicitly.

Write for the intended research audience. Explain the paper-specific obstacle and supplied structural insight relative to closest work when relevant; retain needed definitions without reteaching familiar background. Do not force a comparison into a local edit.

## Read and route

Read the requested scope and its dependencies before editing. Reuse a compact source-anchored map of its objects, claims, and support. Honor local scope and explicit focus exclusions.

| Action | Guidance |
|---|---|
| Draft a section | One section guide below and the short [prose core](references/polishing-protocol.md#prose-core-for-drafting-and-revision), read once and reused |
| Draft or structurally revise a complete paper | [manuscript-workflow.md](references/manuscript-workflow.md): read and plan, work focused sections, reconcile |
| Prose or structural revision | [polishing-protocol.md](references/polishing-protocol.md); add [wording-register.md](references/wording-register.md) for substantive logic, terminology, or register work |
| Proof prose revision | Polishing protocol and [theoretical-proofs.md](references/theoretical-proofs.md), even for a local edit |
| Local terminology, tone, or evidence verbs | [wording-register.md](references/wording-register.md) |
| Quick or section presentation audit | [quick-section-audit.md](references/quick-section-audit.md), then [reporting-and-validation.md](references/reporting-and-validation.md) |
| Whole-manuscript presentation audit | [revision-audit.md](references/revision-audit.md) before orientation; full coverage does not require tracking |
| Deliberate planning or contribution positioning | [argument-architecture.md](references/argument-architecture.md); planning-only returns a move map, revision proceeds to edits |
| Manuscript-wide naming or provenance | [terminology-audit.md](references/terminology-audit.md) |

| Section or object | Guide |
|---|---|
| Title, abstract, introduction, related work | [introduction.md](references/introduction.md) |
| Method, estimator, algorithm, construction | [method-description.md](references/method-description.md) |
| Definitions, assumptions, theorem statements | [theoretical-statements.md](references/theoretical-statements.md) |
| Proof exposition and organization | [theoretical-proofs.md](references/theoretical-proofs.md) |
| Simulations, applications, figures, tables, results | [numerical-experiments.md](references/numerical-experiments.md) |
| Discussion and limitations | [discussion.md](references/discussion.md) |
| Appendix and supplement | [appendix-architecture.md](references/appendix-architecture.md) |

Use one active section guide; add another only for a distinct job. Local polish needs a section guide only when its job affects the edit. Add argument architecture for paper-level abstract or introduction positioning.

Load the support guide for missing or proposed assumptions, sparse support, conflicting representations, causal or identification claims, changed claim strength or citation scope, construction-to-theorem justifications, or unresolved scientific choices. Ordinary equivalent editing does not require that extra read.

Use [style-modes.md](references/style-modes.md) only for an unresolved choice of order or explanatory depth, and [polishing-examples.md](references/polishing-examples.md) for difficult disciplinary phrasing or claim-preservation choices. Reuse read guidance and plans; reopen changed spans and dependencies. Do not load references for completeness or script source merely to run it.

## Tracking is optional

Use the existing [writer_audit.py](scripts/writer_audit.py) package only when the user requests a persistent, resumable, or reproducible audit record. Read [full-audit-operations.md](references/full-audit-operations.md) then; it owns initialization, snapshots, freeze, and publication. A whole-paper audit alone does not select this package. Drafting and ordinary revision create no audit workspace.

Tracking changes recordkeeping, not diagnostic coverage. Only tracked audit-and-revise freezes diagnosis before editing. Ordinary audits use concise findings; routine pass logs are omitted unless requested.

## Validate and deliver

After writing, compare protected scientific and documentary content and recheck affected dependencies. Compile or render when possible and inspect affected output; state material limitations. Complete-paper reconciliation follows the manuscript workflow, including page flow, displays, citations, and main/supplement consistency.

Deliver the requested text or plan. Keep working notes private unless requested; mention substantive changes and material missing author information. Audits use the reporting guide and prioritize consequential findings.

Keep U+2013 and U+2014 out of assistant-authored commentary and audit fields; preserve them in supplied or revised manuscript text, venue typography, and exact source evidence. Never claim independent scientific validation.

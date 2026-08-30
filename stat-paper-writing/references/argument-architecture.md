# Argument Architecture

Use this guide when planning or deliberately restructuring a complete statistical paper, an introduction, or the transition from methods to formal results and evidence. In a default full audit, load it only after the neutral, fine-grained, local, section, and cross-section passes. If the user explicitly requests planning or restructuring, load it after the neutral orientation read.

## Contents

- [Central claim](#the-central-claim)
- [Contribution-to-support ledger](#contribution-to-support-ledger)
- [Reader-facing argument sequence](#reader-facing-argument-sequence)
- [Section architecture](#section-architecture)
- [Literature positioning](#literature-positioning)

## The central claim

Write a private one-sentence claim before revising:

> We address **target or problem X** using **idea Y**, which provides **benefit Z** under **boundary B**.

Every main section should advance one part of this sentence. Remove or move material that does not support it.

Choose one dominant paper-level argument spine. Sections may differ in information order and depth, but they should advance the same account of the contribution. If two spines remain plausible, draft a six-sentence introduction spine for each: target, existing capability, obstacle, key move, evidence contract, and boundary. Retain the version that requires fewer unsupported promises and introduces fewer concepts before their purpose is clear.

### Forward positioning

For author-side planning, restructuring, introductions, or abstracts, do not default to an A + B + C + D inventory. From supplied contribution identities, propose at most two candidate headline contributions. Compare each candidate with the stated existing capability and ask: if this component were removed, which headline capability or boundary change would disappear? Prefer the candidate with the clearest supported change in target, scope, assumptions, feasibility, inference, computation, or interpretation. Present subordinate components as enabling steps rather than coequal selling points.

Lead planning, drafting, introduction, and abstract deliverables with the strongest supported candidate thesis. Use diagnostics to strengthen or delimit that thesis, not as a default referee-style list of criticisms.

When the manuscript does not supply a hierarchy, label the result **Candidate primary contribution** and keep it outside the contribution ledger's supplied rank. Editorial candidate ranks remain outside the factual ledger. Link the candidate to exact formal or empirical support and its main boundary, then ask the author to confirm the hierarchy. Treat this as an author-side positioning proposal, not a verified novelty claim; do not call it novel, first, or boundary-pushing without supplied or independently verified evidence.

For a methods paper, distinguish the main forms of contribution:

- a new estimand or interpretation;
- an identity or representation;
- a feasible estimator;
- a computational reduction;
- a theoretical guarantee stated in the manuscript;
- a diagnostic or decomposition;
- empirical evidence about accuracy, robustness, or mechanism.

Do not allow a practical estimator, theoretical identity, and conceptual decomposition to compete as unrelated contributions. Explain their dependency.

## Contribution-to-support ledger

When a manuscript claims several contributions, or when their hierarchy or support is unclear, build this ledger after gathering cross-section evidence and before judging the whole-paper narrative. Use the six columns exactly as shown, in this order. Do not add, remove, rename, reorder, or substitute a column:

| Rank | Contribution | Method object or construction | Formal support | Empirical support | Boundary |
|---|---|---|---|---|---|
| 1, 2, ... | Exact stated contribution | Named target, identity, estimator, diagnostic, or algorithm | Named statement and written scope | Named table, figure, application, or numerical result | Stated limitation or unsupported link |

Rank contributions in the ledger only when the manuscript supplies a hierarchy or dependency. Record an explicitly equal hierarchy as **Co-primary**. Otherwise mark the rank as **Unclear** and identify the author decision needed. Keep an editorial candidate hierarchy under Forward positioning rather than entering it as a supplied rank. Enter only supplied support; use **Missing**, **Unclear**, or **Not claimed** rather than completing a cell by inference.

Editorial candidate ranks remain outside the factual ledger.

Create a row only when the manuscript or author supplies that contribution's identity. Do not infer contribution identities from a named estimator, theorem, experiment, or later section emphasis. If only an aggregate count is supplied, do not display a row-level ledger or turn the count into conjectured rows; request the missing contribution inventory instead.

This restriction also applies to prose findings and narrative consequences. Do not name an unsupplied theorem, theory component, experiment, or section topic as a contribution or possible primary contribution. Preserve any supplied named subset and refer to the remaining identities only as unnamed contributions.

A formal result about an oracle object does not document support for a feasible-estimator claim unless the manuscript states the link. Evidence about one component does not automatically support another. Make dependencies among contributions explicit.

Use the ledger as a diagnostic. Include it in the response when it materially clarifies a paper-level narrative failure; otherwise use it internally to guide revision. When displaying it, retain all six columns.

If the intended hierarchy is unresolved, a candidate positioning proposal may identify the strongest supported narrative, but ask the authors to confirm the contribution ranks before applying a paper-level reorganization. When visible formal or empirical support is distributed differently from a supplied rank, preserve the supplied rank and ask whether it should remain or be recalibrated. Do not direct the manuscript to center, rebuild around, demote, or remove a contribution until the supplied record establishes that choice.

## Reader-facing argument sequence

### 1. Statistical need

Name the inferential, predictive, or interpretive quantity that matters. Give the reader a reason to care before reviewing technical literature.

### 2. Precise gap

State what is missing as a capability, not merely as an absence of publications. Useful gaps include:

- the target is not identifiable or observable under available information;
- a stated method is computationally prohibitive at the required scale;
- an existing summary hides a mechanism needed for interpretation or diagnosis;
- a supplied result or representation applies only to an idealized object or does not state a property needed for inference, prediction, or decision-making.

Do not assert a gap that is not supported by the manuscript and supplied sources.

### 3. New route

Identify the structural feature the manuscript uses to make progress. Examples include reparameterization, orthogonality, sample splitting, invariance, conditional independence, convexity, sparsity, or an estimating equation.

### 4. Formal support

Organize stated formal results as a visible dependency chain. Each result should answer a question created by the preceding argument. Do not assess whether the results are mathematically valid.

### 5. Empirical support

Organize numerical evidence around the paper's stated claims, not around the availability of settings. Separate validation of an estimator from exploration of a scientific or algorithmic mechanism.

### 6. Meaning and boundary

End by explaining what the representation teaches, when the estimator is useful according to the supplied material, and which stated assumptions or missing components limit the conclusion.

## Section architecture

Use sections for intellectual tasks, not for individual formulas. A subsection should contain enough argument to justify its existence. If two adjacent subsections each contain one short paragraph and one equation, combine them unless they answer genuinely different questions.

Prefer transitions that expose dependency:

- "The identity defines an oracle target, but it is not directly estimable from observed data."
- "The first result states identification; the next controls the error attributed to estimation."
- "The approximation removes the stated computational barrier, but it creates an error term discussed in the next result."

Avoid transitions that merely announce content:

- "Next, we define ..."
- "The following section presents ..."
- "We now turn to ..."

Such phrases are acceptable only after the intellectual reason for the transition is clear.

## Literature positioning

Organize related work by unresolved question or methodological route, not author-by-author chronology. For every literature paragraph, make clear:

1. what the supplied sources establish;
2. what remains unavailable for the present target according to those sources;
3. how the proposed route differs;
4. what intellectual debt is retained.

Do not manufacture novelty by weakening prior work. When a decomposition or identity appears in supplied earlier literature, say so and locate the proposed contribution in observability, computation, generality, or interpretation only when supported.

If several affected sections still have genuine presentation problems after the argument spine is set, use [style-modes.md](style-modes.md) selectively. Do not assign modes to clear sections.

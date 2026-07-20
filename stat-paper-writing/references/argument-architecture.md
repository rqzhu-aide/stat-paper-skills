# Argument Architecture

Use this guide when planning or restructuring a complete statistical paper, an introduction, or the transition from methods to theory and evidence.

## The central claim

Write a private one-sentence claim before revising:

> We address **target or problem X** using **idea Y**, which provides **benefit Z** under **boundary B**.

Every main section should advance one part of this sentence. Remove or move material that does not support it.

Choose one dominant paper-level argument spine. Sections may use different presentation modes, but they should advance the same account of the contribution. A secondary route may support a local section without creating a competing introduction or contribution claim. If two spines remain plausible, draft a six-sentence introduction spine for each: target, existing capability, obstacle, key move, evidence contract, and boundary. Retain the version that requires fewer unsupported promises and introduces fewer concepts before their purpose is clear.

## Cross-section mode map, when needed

Create a mode map only when several sections have genuine problems of information order, explanatory depth, formal organization, or evidence-led organization. For those sections, use [style-modes.md](style-modes.md) and record `section -> reader difficulty -> primary mode -> optional local secondary mode`. Do not assign modes to sections that are already clear. Cross-section coherence comes from a stable target, terminology, notation, and claim chain, not from identical pacing in every section.

For a methods paper, distinguish the main forms of contribution:

- a new estimand or interpretation;
- an identity or representation;
- a feasible estimator;
- a computational reduction;
- a theoretical guarantee;
- a diagnostic or decomposition;
- empirical evidence about accuracy, robustness, or mechanism.

Do not allow a practical estimator, theoretical identity, and conceptual decomposition to compete as three unrelated contributions. Explain their dependency.

## Reader-facing argument sequence

### 1. Statistical need

Name the inferential, predictive, or interpretive quantity that matters. Give the reader a reason to care before reviewing technical literature.

### 2. Precise gap

State what is missing as a capability, not merely as an absence of publications. Useful gaps include:

- the target is not identifiable or observable under available information;
- a valid method is computationally prohibitive at the required scale;
- an existing summary hides a mechanism needed for interpretation or diagnosis;
- theory or a representation applies only to an idealized object or fails to preserve a property required for inference, prediction, or decision-making.

### 3. New route

Identify the structural feature that makes progress possible. Examples include reparameterization, orthogonality, sample splitting, invariance, conditional independence, convexity, sparsity, or an estimating equation.

### 4. Formal support

Organize formal results as a dependency chain. Each result should answer a question created by the previous section. Avoid a collection of disconnected properties.

### 5. Empirical support

Design numerical evidence around the paper's claims, not around the availability of settings. Separate validation of an estimator from exploration of the scientific or algorithmic mechanism.

### 6. Meaning and boundary

End by explaining what the representation teaches, when the estimator is useful, and which assumptions or missing components limit the conclusion.

## Section architecture

Use sections for intellectual tasks, not for individual formulas. A subsection should contain enough argument to justify its existence. If two adjacent subsections each contain one short paragraph and one equation, combine them unless they answer genuinely different questions.

Prefer transitions that expose dependency:

- "The identity defines an oracle target, but it is not directly estimable from observed data."
- "The first result establishes identification; the next controls the error introduced by estimation."
- "The approximation removes the computational barrier, but it creates an error term that must be controlled."

Avoid transitions that merely announce content:

- "Next, we define ..."
- "The following section presents ..."
- "We now turn to ..."

Such phrases are acceptable only after the intellectual reason for the transition is clear.

## Literature positioning

Organize related work by unresolved question or methodological route, not author-by-author chronology. For every literature paragraph, make clear:

1. what prior work established;
2. what remains unavailable for the present target;
3. how the proposed route differs;
4. what intellectual debt is retained.

Do not manufacture novelty by weakening the description of prior work. When a decomposition or identity exists in earlier literature, say so and locate the new contribution in observability, computation, generality, or interpretation.

## Architecture audit

Ask:

- Can a reader state the paper's central claim after the introduction?
- Does each section answer a question raised earlier?
- Are primary and secondary contributions visibly ranked?
- Does the theory justify the proposed method rather than merely coexist with it?
- Do the experiments test the claims made in the introduction?
- Does the discussion return to the same target and boundary?

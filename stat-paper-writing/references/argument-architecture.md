# Argument Architecture

Use for paper planning, structural revision, and introduction positioning. In a manuscript review, assess the whole-paper narrative after gathering local and cross-section evidence; use the same criteria diagnostically without drafting unless revision is requested.

## Central claim and editorial hierarchy

Form a compact account of the supplied target, structural idea, supported benefit, and boundary. One useful private sentence is:

> We address **target or problem X** using **idea Y**, which provides **benefit Z** under **boundary B**.

Use that account to judge what each section contributes, including necessary background, enabling results, and limitations. Avoid an A + B + C + D inventory when the supplied contributions form a dependency chain. Distinguish estimands, representations, feasible estimators, computation, guarantees, diagnostics, and empirical evidence.

For positioning, compare at most two plausible headline contributions already identified in the supplied material. Ask which capability or boundary change would disappear without each candidate. Prefer the clearest supported change in target, scope, assumptions, feasibility, inference, computation, or interpretation; describe enabling components in relation to it. Link the proposed emphasis to exact formal or empirical support and its boundary. This is editorial positioning, not a verified novelty judgment.

A restructuring request authorizes reversible ordering and emphasis among supplied contributions. If no hierarchy is specified, choose the supported organization that best explains the argument and identify the choice as editorial. Do not pause merely to confirm contribution ranks. Preserve explicit author priorities; ask only when reorganization requires a scientific claim change or resolution of competing author intentions. For those cases, use [support-and-author-decisions.md](support-and-author-decisions.md).

## Contribution and support map

When several contributions or unclear support complicate the narrative, keep a compact map of the supplied contribution identities, method objects, formal and empirical support, and boundaries. A private writing plan needs no fixed columns. Include a map in feedback only when it explains a consequential issue.

Separate a supplied rank from editorial emphasis. Record an unspecified rank as unclear rather than presenting the proposed order as the author's scientific priority. This does not prevent authorized reorganization. If visible support conflicts with an explicit priority, explain the mismatch and retain that priority pending clarification.

Do not invent contribution identities from a named estimator, theorem, experiment, or section topic. If the source supplies only a count, preserve any named subset and describe the rest as unspecified; request their identities only when needed for the task. Enter missing or unclear support honestly. An oracle result does not support a feasible-estimator claim unless the supplied account states the link, and evidence for one component does not automatically support another.

Tracked audits use the exact contribution-ledger fields in [full-audit-data-contract.md](full-audit-data-contract.md). Read that schema only when creating or editing tracked records, not for an ordinary writing plan.

## Reader-facing sequence

Build the argument around the questions the manuscript must answer, without requiring a fixed section order:

1. **Statistical need.** Name the inferential, predictive, or interpretive quantity and why it matters.
2. **Precise gap.** Explain the missing capability supported by the source material: an information constraint, computational obstacle, hidden mechanism, or guarantee stated only for an idealized object. An absence of publications is not itself an explanation.
3. **Proposed route.** Identify the supplied structural feature that makes progress, such as orthogonality, reparameterization, sample splitting, invariance, convexity, or an estimating equation.
4. **Formal support.** Present the stated result chain so each result answers a question raised by the argument. Do not independently certify it.
5. **Empirical support.** Organize numerical evidence around stated claims and comparison questions, distinguishing estimator performance from exploration of a mechanism.
6. **Meaning and boundary.** Explain the supported use or interpretation and the assumptions or missing components that limit it.

## Section architecture

Give sections intellectual jobs. Combine adjacent one-paragraph, one-equation subsections when they answer the same question; preserve useful landmarks in a long argument. Transitions should answer the question created by the preceding section.

Distinguish what a reader needs to understand from what a proof depends on. An analytical representation may belong after the procedure it analyzes. Retain an early oracle or theoretical setup when it explains the central idea; honor an explicitly requested architecture. For unresolved explanatory depth, use [style-modes.md](style-modes.md) selectively.

## Literature positioning

Organize related work by question or methodological route. Across the relevant passage, explain:

1. what the closest sources establish and which idea the paper inherits;
2. where direct reuse stops covering the present target or regime;
3. which supplied structural observation or analytical change addresses that obstacle;
4. what capability changes, under which restrictions or tradeoffs.

Develop this relationship where it explains a method choice, theorem, or empirical comparison. It need not be confined to a related-work inventory or repeated in every paragraph. For conditional calibration and citation placement, use [wording-register.md](wording-register.md).

Do not manufacture novelty by weakening prior work. Attribute an inherited decomposition or identity and locate the supplied contribution in what actually changes, such as observability, computation, generality, or interpretation.

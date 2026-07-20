# Statistical Review Framework

## Contents

- [Contribution and positioning](#1-contribution-identity-and-positioning)
- [Statistical target and method](#2-statistical-target-and-method)
- [Assumptions and theory](#3-assumptions-validity-and-theory)
- [Evidence and application](#4-numerical-evidence-and-application)
- [Exposition and reproducibility](#5-exposition-navigation-and-reproducibility)
- [Priority synthesis](#6-priority-synthesis)

## 1. Contribution identity and positioning

Ask whether a statistically trained reader can state one central contribution after reading the abstract and introduction.

Check:

- whether the paper defines a meaningful statistical, inferential, predictive, computational, or interpretive target;
- whether the gap is a missing capability rather than only an asserted absence of prior papers;
- whether an identity, estimator, algorithm, theorem, and application are presented as a dependency chain rather than competing contributions;
- whether novelty is located precisely in the target, representation, observability, computation, guarantee, evidence, or interpretation;
- whether the closest cited literature is described fairly and the claimed distinction is supported;
- whether external search identifies a closer publication that the manuscript omits or distinguishes incorrectly.

Flag a contribution-identity problem when the paper contains several technically valid pieces but no clear organizing statistical principle.

Do not declare a novelty claim established without adequate literature evidence. Use [novelty-verification.md](novelty-verification.md) when novelty is in scope, and state what remains unsearched or unavailable.

## 2. Statistical target and method

Reconstruct these layers separately:

1. population target or scientific quantity;
2. identification result or oracle object;
3. feasible estimator or procedure;
4. nuisance or plug-in approximation;
5. numerical implementation;
6. reported empirical output.

Check whether the paper moves correctly between them. Ask:

- What data and information does each layer use?
- Does the algorithm implement the stated estimator?
- Does the main theorem apply to the implemented object?
- Are sample splitting, cross-fitting, exclusions, conditioning, or reused fitted objects handled consistently?
- Are penalties, losses, weights, regularizers, and tuning choices given a statistical meaning?
- Are necessary choices distinguished from convenient defaults?
- Are computation, failure conditions, and tuning guidance adequate for use or reproduction?

Treat a mismatch between the headline target and the evaluated object as a high-priority concern.

## 3. Assumptions, validity, and theory

Group assumptions by role:

- scientific or identifying;
- statistical or asymptotic;
- computational;
- proof-dependent regularity.

Evaluate whether the headline conclusion depends on assumptions that are hidden, implausibly described as mild, difficult to diagnose, or incompatible with the application.

For the theorem story, ask:

- Which result is foundational, which is central, and which is a refinement?
- Does every main result answer a reader question created earlier?
- Are scopes, quantifiers, convergence modes, conditioning, and constants clear?
- Does the interpretation match the formal conclusion?
- Are oracle and feasible guarantees distinguished?
- Do proof sketches expose the main device and assumption use?
- Are limitations or failure regimes stated where the claim is made?

Separate theorem exposition from proof verification. An unclear proof is not automatically an incorrect proof. A proof-level objection must identify the exact unsupported step or dependency.

## 4. Numerical evidence and application

Map each central claim to its visible support:

| Claim | Required support | Evidence shown | Gap |
|---|---|---|---|

Evaluate:

- target and truth definition;
- relevant metrics and uncertainty;
- representative, boundary, and stress settings;
- fair competitors, information budgets, tuning, and computational budgets;
- robustness or sensitivity to consequential assumptions and analyst choices;
- separation of sampling variability, algorithmic randomness, and Monte Carlo error;
- negative or null results that define the method's boundary;
- reproducibility details needed to interpret the comparison.

For real-data applications, determine whether the analysis is an illustration, prediction study, estimation problem, decision analysis, or scientific investigation. Do not treat agreement on one observed dataset as accuracy validation when truth is unavailable.

Ask what scientific, statistical, or decision conclusion changes because of the method. If nothing consequential changes, the application may demonstrate operation without demonstrating value.

## 5. Exposition, navigation, and reproducibility

Assess whether the reader can recover:

- the central claim and its boundary;
- the role of every main section;
- a stable terminology and notation system;
- the purpose of each major display and theorem;
- the route from assumptions to guarantee to evidence;
- the division between main text and supplement.

Judge these questions first in manuscript order. Record delayed definitions or explanations at the point where the reader first needs them, even if later text eventually resolves the issue. Use [sequential-reading.md](sequential-reading.md) for a full first-reader pass.

Flag software-manual prose when it obscures statistical objects. Flag unexplained jargon, formula-first exposition, unranked contribution lists, disconnected theorem catalogues, and result-by-result narration.

Do not turn reviewer comments into comprehensive copyediting. Give examples only when they reveal a recurring problem or clarify the required revision.

## 6. Priority synthesis

Rank issues in this order unless the manuscript justifies another order:

1. correctness, validity, or target mismatch;
2. contribution identity and novelty positioning;
3. assumptions and theorem-method alignment;
4. evidence for the headline claim;
5. application meaning and practical calibration;
6. exposition, navigation, and local polish.

For each high-priority issue, distinguish the remedy:

- **Rewrite:** the necessary content exists but is poorly expressed or organized.
- **Reanalysis:** existing data or results need another analysis or comparison.
- **New evidence:** an experiment, dataset, control, sensitivity study, or benchmark is missing.
- **New theory:** the formal support required by the central claim is absent.
- **Verification:** a proof, citation, computation, or implementation must be checked.
- **Author decision:** the paper must narrow its claim, change its target, or choose a framing.

Prefer narrowing or clarifying a claim when that fully resolves the mismatch. Do not demand additional work merely to make the review look comprehensive.

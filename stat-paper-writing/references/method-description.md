# Method Description Guidance

## Job of the section

Explain what is constructed, why each component is needed, what information it uses, and how the implemented procedure relates to the statistical target.

## Diagnose the current draft

Look for:

- a formula before the problem it solves;
- target, oracle identity, feasible estimator, and implementation described as one object;
- notation introduced globally before a local construction is understood;
- optional choices presented as mathematical necessities;
- algorithm steps mixed with conceptual derivation;
- no interpretation of normalization, tuning, or dependence control;
- computational claims without dimensions, stopping rules, or failure states.

## Core architecture

Use the following order when applicable:

1. **Target:** Define the estimand, prediction, decision, or output.
2. **Available information:** State the data, fitted objects, nuisance estimates, and randomness used.
3. **Oracle or baseline:** Give the exact or familiar construction that clarifies the goal.
4. **Obstacle:** Explain why the oracle or baseline is unavailable or inadequate.
5. **Construction:** Introduce the minimum new object that repairs the obstacle.
6. **Formula or algorithm:** State the feasible procedure.
7. **Interpretation:** Explain the role, sign, units, and effect of each component.
8. **Operation:** State tuning, complexity, invariances, safeguards, and failure conditions.
9. **Boundary:** Clarify what is exact, approximate, heuristic, or optional.

Where useful, interpret a central construction at two distinct levels, such as statistical plus geometric, probabilistic, computational, or decision-level. Do not force multiple interpretations or replace a precise mechanism with analogy.

## Move from local to global

Define one observation-level, query-level, or pair-level object before stacking or aggregating it. Explain how local rules differ before introducing a matrix or global functional.

## Distinguish layers

Use separate notation and prose for:

- population target;
- optimization objective, optimizer, and returned estimator;
- identification or oracle identity;
- feasible estimator;
- nuisance or plug-in approximation;
- asymptotic approximation;
- finite-computation implementation.

State which theorem applies to which layer. Trace information flow when validity depends on sample splitting, cross-fitting, withheld outcomes, reused fitted objects, or algorithmic randomness.

## Algorithms

Before pseudocode, state inputs, outputs, target, and stored quantities. Present steps in execution order. Afterward, explain complexity, initialization, stopping, numerical safeguards, and cases where the algorithm cannot return a valid result.

Keep the statistical construction in the main text. Put software-specific indexing, storage, and extensive safeguards in the appendix.

## If a presentation mode is needed

- **Compact and direct:** State target, key construction, estimator, and implementation contract with minimal detours.
- **Explanatory and intuition-led:** Begin with the unavailable quantity or failure, trace the decisive dependence path, objective term, or information constraint in a nondegenerate regime, then formalize the construction.
- **Formal and structure-led:** Define objects, sigma-fields, conditioning regimes, parameter spaces, and exact versus approximate layers precisely.
- **Evidence-led and comparative:** Explain the method through the claims later tested, including which component should improve which metric or behavior.

## Review checklist

- What is the target?
- What information is observed and reused?
- What is newly fitted or randomized?
- Why is every term and normalization present?
- Which choices are necessary and which are convenient?
- Does the algorithm implement the stated estimator?
- What happens in a diagnostic boundary or limiting regime?
- Are cost and failure conditions explicit?

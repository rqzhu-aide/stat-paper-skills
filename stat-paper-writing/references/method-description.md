# Method Description Guidance

## Job of the section

Explain what is constructed, why each component is needed, what information it uses, and how the described procedure relates to the statistical target.

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
4. **Obstacle:** Explain why the manuscript says the oracle or baseline is unavailable or inadequate.
5. **Construction:** Introduce the minimum new object that addresses the stated obstacle.
6. **Formula or algorithm:** State the feasible procedure.
7. **Interpretation:** Explain the role, sign, units, and stated effect of each component.
8. **Operation:** State tuning, complexity, invariances, safeguards, and failure conditions supplied by the manuscript.
9. **Boundary:** Clarify what is described as exact, approximate, heuristic, or optional.

Where useful, retain two distinct interpretations of a central construction only when both are already present in the manuscript or supplied by the author, such as statistical plus geometric, probabilistic, computational, or decision-level. Do not invent a second interpretation, force multiple interpretations, or replace a precise mechanism with analogy. If an unsupplied interpretation might help, present it as an explicit proposal outside clean manuscript prose and request author confirmation.

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

State which formal result the manuscript associates with each layer. Describe information flow when the manuscript uses sample splitting, cross-fitting, withheld outcomes, reused fitted objects, or algorithmic randomness. Do not infer an unstated validity guarantee.

When supplied material explicitly classifies paired objects as oracle and feasible, state both classifications directly before discussing how the objects are constructed or used. A true-nuisance definition or cross-fitted construction supports the supplied classification, but does not replace its explicit role name.

## Algorithms

Before pseudocode, state inputs, outputs, target, and stored quantities. Present steps in execution order. Afterward, report supplied complexity, initialization, stopping, numerical safeguards, and failure conditions.

Keep the statistical construction in the main text. Put software-specific indexing, storage, and extensive safeguards in the appendix.

Compare formulas, pseudocode, and prose for the same named inputs, operations, tuning choices, and returned object. This is a documentary consistency check, not a determination that code implements the estimator.

When these representations conflict, or when a claimed computational property is not established by supplied artifacts, load [support-and-author-decisions.md](support-and-author-decisions.md). Do not infer authority, code equivalence, exactness, convergence, complexity, or the returned object from formality or convention.

## Review checklist

- What is the target?
- What information is observed and reused?
- What is newly fitted or randomized?
- Is the stated role of every term and normalization clear?
- Which choices are described as necessary and which as convenient?
- Do the formula, pseudocode, and prose name the same inputs, operations, outputs, and tuning choices?
- What happens in a stated boundary or limiting regime?
- Are cost and failure conditions explicit?
- Are claims about uninspected code behavior marked **Unverified dependency**?

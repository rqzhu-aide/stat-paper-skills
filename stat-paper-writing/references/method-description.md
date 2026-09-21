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

Let the reader reconstruct the procedure: its target and available information, the elementary prediction or estimate, aggregation or adjustment, and the returned result. Explain the supplied reason for the construction as its components become necessary. Introduce notation at its substantive use.

Choose the entry point by explanatory need. The concrete procedure may explain the idea; the closest existing method or an oracle representation may expose the obstacle. Explain why an inherited construction needs modification or a different analysis when supplied, without routine textbook setup. Do not open with a complete-sample average, generic functional, or proof decomposition merely because later analysis depends on it. In a theory-led paper, early analytical setup can be essential. Honor the author's chosen architecture.

Use a formula, algorithm, or short identity where it answers the current question. A result identifying what the estimator targets may belong here; detailed regularity regimes and proof devices usually belong with their analysis. Distinguish a broadly implemented procedure from a restricted version used in theory.

Explain the role, normalization, tuning, and stated effect of components without inventing a mechanism. For uncertain equivalence or interpretation, use [support-and-author-decisions.md](support-and-author-decisions.md). Do not force multiple interpretations or an analogy when the construction is already clear.

## Move from local to global

Define a local object before stacking or aggregating it. After relocating a formula, recheck first-use symbols and the retained explanation in its new context; unchanged mathematics does not make its introduction self-contained.

## Distinguish layers

Use separate notation and prose for:

- population target;
- optimization objective, optimizer, and returned estimator;
- identification or oracle identity;
- feasible estimator;
- nuisance or plug-in approximation;
- asymptotic approximation;
- finite-computation implementation.

Make clear which object a stated guarantee concerns when that connection becomes relevant. Describe sample splitting, cross-fitting, reused fitted objects, and randomization where they affect construction or scope. Do not infer an unstated guarantee or insert a formal-result reminder after every component.

Preserve supplied oracle and feasible classifications and make them explicit where the objects are introduced or compared. Labels should clarify their definitions and information requirements, not displace the construction. Do not infer empirical use from a role label alone.

## Algorithms

Establish what the algorithm computes before extensive tuning or stabilization details. State its data, arguments, returned object, and steps in execution order. Explain supplied initialization, numerical choices, complexity, and stopping behavior when they affect the estimator, interpretation, or reproducibility at the requested level.

Keep the statistical construction in the main text; place software indexing, storage, and lengthy safeguards in the appendix. Preserve choices that affect the estimator or interpretation in the main account, even if their full recipe appears later.

Compare formulas, pseudocode, and prose for the same named inputs, operations, tuning choices, and returned object. This is a documentary consistency check, not a determination that code implements the estimator.

For conflicting representations, missing consequential implementation details, or unsupported computational claims, use [support-and-author-decisions.md](support-and-author-decisions.md). Code equivalence, exactness, convergence, and complexity cannot be inferred from conventional wording.

## Review checklist

- In a methods paper, can the intended reader trace the data through the elementary prediction or estimate and its aggregation or adjustment to the returned result by the end of Method and Implementation, without extracting the construction from Theory or the supplement? A named standard procedure may suffice for this audience; a generic kernel or functional does not replace a supplied construction. Retain the theory-led entry point when it serves the paper's purpose.
- Are the target, observed and reused information, and fitted or randomized objects clear?
- Does each term or analytical representation arrive with a reason to use it?
- Which choices are described as necessary and which as convenient?
- Do the formula, pseudocode, and prose name the same inputs, operations, outputs, and tuning choices?
- What happens in a stated boundary or limiting regime?
- Are supplied cost and failure conditions clear where needed for the requested account?
- Are claims about uninspected code behavior marked **Unverified dependency**?

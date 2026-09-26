# Method Description Guidance

## Job of the section

Explain the construction, its target and information, and the intellectual choices connecting it to relevant prior work.

## Diagnose the current draft

Look for:

- a formula before the problem it solves;
- target, oracle identity, feasible estimator, and implementation described as one object;
- notation introduced globally before a local construction is understood;
- optional choices presented as mathematical necessities;
- algorithm steps mixed with conceptual derivation;
- no interpretation of normalization, tuning, or dependence control;
- inherited constructions cited without explaining consequential adaptations;
- computational claims without dimensions, stopping rules, or failure states.

## Core architecture

Let the reader reconstruct the target, available information, elementary prediction or estimate, aggregation or adjustment, and returned result. Explain the supplied rationale as components become necessary; introduce notation at substantive use.

Choose the entry point by explanatory need: the procedure, closest method, or oracle representation. Analytical dependencies alone do not justify opening with a generic functional or proof decomposition. Retain useful early setup in theory-led papers and honor the author's architecture.

At consequential choices, explain the inherited idea, what is retained or changed, the supplied reason, and supported consequence or tradeoff. Distinguish changes to target, information, assumptions, estimator, computation, and guarantee. A changed setting does not establish earlier-method failure. Develop relationships where they explain the construction or analysis, without a repeated template or second literature survey. Attribute reuse without inventing novelty.

Use supplied source passages first; unresolved consequential comparisons use [targeted source reading](wording-register.md#targeted-disciplinary-calibration). Bibliography entries alone cannot substantiate comparisons. When support or design rationale is missing, continue supported writing and identify material missing information separately; do not invent necessity, superiority, or optimality.

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

Make supplied oracle and feasible classifications explicit at introduction or comparison. Labels clarify definitions and information requirements; they do not replace the construction or establish empirical use.

## Algorithms

State the algorithm's data, arguments, returned object, and execution order. Explain supplied initialization, tuning, stabilization, complexity, and stopping behavior when consequential for the estimator, interpretation, or requested reproducibility.

Keep the statistical construction in the main text; place software indexing, storage, and lengthy safeguards in the appendix. Preserve choices that affect the estimator or interpretation in the main account, even if their full recipe appears later.

Compare formulas, pseudocode, and prose for matching inputs, operations, tuning, and returned object. This checks documentary consistency, not code equivalence.

For conflicts, consequential missing details, or unsupported computational claims, use [support-and-author-decisions.md](support-and-author-decisions.md). Conventional wording cannot establish code equivalence, exactness, convergence, or complexity.

## Review checklist

- By the end of Method and Implementation, can the intended reader trace data through the elementary estimate and aggregation to the returned result? A named standard procedure may suffice; a generic functional cannot replace a supplied construction. Retain useful theory-led organization.
- Are the target, observed and reused information, and fitted or randomized objects clear?
- Does each term or analytical representation arrive with a reason to use it?
- Can the reader identify what is inherited, what changes, and the supported reason where that relationship matters to the method?
- Which choices are described as necessary and which as convenient?
- Do the formula, pseudocode, and prose name the same inputs, operations, outputs, and tuning choices?
- What happens in a stated boundary or limiting regime?
- Are supplied cost and failure conditions clear where needed for the requested account?
- Are claims about uninspected code behavior marked **Unverified dependency**?

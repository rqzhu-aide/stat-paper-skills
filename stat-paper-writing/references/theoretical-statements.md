# Theoretical Statement Guidance

## Job of the section

Turn a reader question into a clearly presented formal result. The statement should identify its regime, assumptions, conclusion, and scope without carrying proof machinery or implementation commentary.

This guide checks wording and consistency, not whether the statement is mathematically true or whether its assumptions are sufficient.

## Classify the stated result

Determine its declared job before editing:

- definition or identification;
- exact identity;
- decomposition;
- boundary or impossibility result;
- approximation bound;
- consistency or rate;
- limit distribution or inferential guarantee;
- optimization or convergence result;
- computational approximation with the data held fixed.

Do not describe a computational limit as statistical consistency.

## Preflight paragraph

Before a central result, state:

1. the question it is said to answer;
2. why that question matters for the method;
3. the described role of the main assumptions;
4. the written conclusion in ordinary statistical language.

Do not begin an unfamiliar result with a dense block of notation.

## Statement construction

Include:

- probability model, parameter space, or conditioning regime stated by the manuscript;
- objects to which the result is said to apply;
- assumptions named for the conclusion;
- exact written mathematical conclusion;
- quantifiers, probability level, convergence mode, or uniformity scope;
- constants and their stated dependencies when relevant.

Exclude extended interpretation, tuning advice, proof-specific notation, and variants that are not part of the central statement.

## Explain assumptions by declared role

Use the manuscript's supplied account to distinguish:

- **scientific or identifying:** defines what can be learned;
- **statistical:** is said to control bias, variance, concentration, or asymptotics;
- **computational:** is said to ensure an optimization or approximation can be obtained;
- **proof-dependent regularity:** appears only in the supplied formal development.

Do not determine that a role is mathematically correct or that an assumption is necessary. Check that labels, scopes, and described roles are consistent across the statement and surrounding prose. Do not call assumptions mild, standard, or verifiable without supplied support.

If surrounding prose asserts a relation that the displayed statement does not explicitly document, treat the difference as a documentary conflict. Do not choose the display as authoritative or remove the relation unless supplied evidence or author confirmation identifies the controlling representation. After an authorized correction, name the changed relation and its documentary basis; do not claim that omission from the display proves the relation is false or not implied.

## Post-result interpretation

Use three moves:

1. **Translation:** Explain the written conclusion without restating the display.
2. **Consequence:** State what estimator, design choice, or next result the manuscript says it enables.
3. **Boundary:** State what the written result does not establish.

Make declared theorem dependencies visible. Move technical intermediate statements to the proof appendix when their role is documentary and the main result remains understandable.

## Review checklist

- Does the result have a clear declared job?
- Are assumption labels, roles, and scopes stated consistently?
- Is the target finite-sample, asymptotic, conditional, pointwise, uniform, or computational?
- Does surrounding prose refer to the same oracle or feasible object as the statement?
- Does the stated relation to prior results agree with the manuscript and supplied sources?
- Does the interpretation include both consequence and boundary?
- Are any questions that require mathematical validation or external source support marked **Unverified dependency**?

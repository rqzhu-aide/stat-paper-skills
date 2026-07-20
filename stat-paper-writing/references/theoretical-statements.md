# Theoretical Statement Guidance

## Job of the section

Turn a reader question into a precise formal result. The statement should identify its regime, assumptions, conclusion, and scope without carrying proof machinery or implementation commentary.

## Classify the result

Determine its job before writing:

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

1. the question it answers;
2. why that question matters for the method;
3. the conceptual role of the main assumptions;
4. the conclusion in ordinary statistical language.

Do not begin an unfamiliar result with a dense block of notation.

## Statement construction

Include:

- probability model, parameter space, or conditioning regime;
- objects to which the result applies;
- assumptions required for this conclusion;
- exact mathematical conclusion;
- quantifiers, probability level, convergence mode, or uniformity scope;
- constants and their dependencies when relevant.

Exclude extended interpretation, tuning advice, proof-specific notation, and variants that are not part of the central claim.

## Explain assumptions by role

Group assumptions as:

- **scientific or identifying:** defines what can be learned;
- **statistical:** controls bias, variance, concentration, or asymptotics;
- **computational:** ensures an optimization or approximation can be obtained;
- **proof-dependent regularity:** supports the available proof but is not claimed to be intrinsic to the method.

Say whether assumptions are standard, strong, verifiable, or used only for one step. Do not call them mild without support.

## Post-result interpretation

Use three moves:

1. **Translation:** Explain the conclusion without restating the display.
2. **Consequence:** State what estimator, design choice, or next result it enables.
3. **Boundary:** State what it does not establish.

Build visible theorem dependencies. Demote two-line algebra to prose and move technical intermediate lemmas to the proof appendix.

## If a presentation mode is needed

- **Compact and direct:** Use a short preflight, minimal statement notation, and one precise consequence.
- **Explanatory and intuition-led:** Use a mechanism-preserving regime, assumption perturbation, or decomposition to clarify the question and assumption roles before the statement, then interpret the operative term afterward.
- **Formal and structure-led:** Emphasize scopes, quantifiers, dependency order, and exact distinctions among result types.
- **Evidence-led and comparative:** Frame the result around the observable claim it supports and explain which experiment or comparison probes its implications.

## Review checklist

- Does the result have a clear job?
- Are all stated assumptions used, and are their roles and status clear?
- Is the target finite-sample, asymptotic, conditional, or computational?
- Does it apply to the implemented estimator or only an oracle?
- Does the stated relation to prior results agree with the manuscript and supplied sources, with external verification needs explicitly flagged?
- Does the interpretation include both consequence and boundary?

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

## Orient the reader

Before an unfamiliar central result, explain its question, main assumptions, and statistical conclusion at the intended research level. When a comparison is supplied, identify what object, regime, or guarantee changes and why it matters. Clarify paper-specific notation and restrictions without reteaching familiar definitions. Draw on preceding development rather than repeating a preamble for every result.

A short corollary may need only a transition; a central theorem may need substantial setup. Introduce analytical objects when their role in the question is clear. A theory-led paper may need this setup before any algorithm; do not impose construction-first exposition on it.

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

Explain an operative comparison or restriction, not merely the names of symbols in a condition. An equivalent restatement may use supplied definitions and regimes under [support-and-author-decisions.md](support-and-author-decisions.md); it does not establish necessity or sufficiency. Keep labels, scopes, and declared roles consistent. Do not call assumptions mild, standard, or verifiable without supplied support.

Where the supplied comparison permits, distinguish inherited conditions from strengthened, modified, or paper-specific restrictions, cite their provenance, and explain their roles. A wider regime for one parameter does not establish that the full assumption set is weaker.

For conflicting prose and formal statements, follow the documentary-conflict rule in [support-and-author-decisions.md](support-and-author-decisions.md).

## Post-result interpretation

Across the surrounding passage, provide the interpretation needed to understand the result:

1. **Translation:** State the statistical conclusion, naming the object and error or property established. Proof-operation labels such as replacement or transfer may belong in a proof roadmap; explain the underlying approximation or bound before relying on that shorthand.
2. **Consequence:** State what estimator, design choice, or next result the manuscript says it enables.
3. **Boundary:** State the material scope limits of the written result.

These functions need not form a separate paragraph after every result. Avoid translating a display twice or repeating a locally clear boundary. Make declared dependencies visible. Move technical intermediates and secondary variants to the appendix when that clarifies the main result; keep its governing conditions identifiable in the main text.

## Review checklist

- Does the result have a clear declared job?
- Are assumption labels, roles, and scopes stated consistently?
- Is the target finite-sample, asymptotic, conditional, pointwise, uniform, or computational?
- Does surrounding prose refer to the same oracle or feasible object as the statement?
- Does the stated relation to prior results agree with the manuscript and supplied sources?
- Are the consequence and material boundary clear in the surrounding passage?
- Are any questions that require mathematical validation or external source support marked **Unverified dependency**?

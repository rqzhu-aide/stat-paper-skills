# Numerical Experiment Guidance

## Job of the section

Present evidence for specific claims about targeting, mechanism, statistical performance, robustness, computation, interpretation, or failure boundaries.

This guide audits reporting and presentation. It does not recompute or certify numerical results.

## Start from claims

Create a claim-evidence map before revising settings:

| Claim | Reported comparison or truth | Metric | Stress or boundary setting |
|---|---|---|---|

Each main table or figure should answer one primary question, even when it reports several outcomes.

## Define the target and randomness

State what is fixed and what is resampled. Distinguish:

- fixed-design and random-design targets;
- data sampling and algorithmic randomization;
- finite computation and limiting algorithmic targets;
- Monte Carlo approximation error and estimator variability;
- oracle information and practically available information.

If the benchmark is simulated, report how it is defined and any supplied uncertainty.

## Design settings

Explain how each setting tests a stated claim or mechanism. Useful axes include sample size, dimension, sparsity, signal strength, dependence, noise, regularization, model misspecification, and computational budget.

When supplied, distinguish:

- a tractable setting with known truth that preserves the central mechanism;
- representative settings;
- a boundary where the mechanism vanishes or becomes exact;
- a stress setting where an assumption weakens.

Do not invent missing settings or motivations.

## Competitors and tuning

For every competitor, report the supplied target, implementation, tuning information, oracle inputs, randomness, and included computational cost. Check that prose claims about fairness agree with the documented information and tuning budgets.

Do not infer that a comparison is fair or unfair from missing details alone. Mark the concern **Unverified dependency** and name the missing information.

## Metrics and displays

Match stated metrics to claims. Report uncertainty summaries when supplied and note their absence when it materially limits interpretation. Report runtime with available hardware, stopping rule, memory, and statistical-quality information.

Prefer tables when exact summaries are primary and figures when patterns are primary. Captions should name the estimand, setting, uncertainty display, and graphical encoding.

## Real-data applications

State whether the manuscript presents the application as an illustration, predictive evaluation, estimation problem, decision analysis, or scientific investigation. Report supplied data provenance, eligibility rules, preprocessing, missingness, information-leakage safeguards, uncertainty, and consequential analyst choices.

When claiming practical or scientific value, state only an interpretation, analytical choice, scientific conclusion, or action that supplied material reports to differ from a justified baseline. If none is supplied, do not infer the application's role or relabel it as illustrative. Remove an unsupported qualifier only under the bounded-polishing rule in the main skill. If no supported clean wording remains, report **Unverified dependency:** and ask the author to identify the intended role and supporting evidence. Use illustrative language in clean manuscript prose only when the supplied material identifies the application as illustrative.

When truth is unavailable, do not present agreement in one observed data set as accuracy validation. Interpret differences in practical units, state what the design is said to identify, and separate predictive or associational evidence from causal conclusions.

## Results paragraphs

Use this order:

1. question addressed by the display;
2. principal observed pattern;
3. practical magnitude and supplied uncertainty;
4. stated connection to the method or formal result;
5. exception, missing uncertainty, or failure mode.

Separate observations from explanations. Avoid narrating one method at a time. If only summary means are supplied, report the comparison descriptively and do not add significance, uniformity, or robustness claims.

## Review checklist

- Does every central empirical claim point to visible reported support?
- Is the target or truth defined for the reported metric?
- Are randomness levels and replication counts stated?
- Are competitor information and tuning choices reported?
- Do captions and prose agree with table and figure values?
- Are null and negative results retained when they limit the claim?
- Do conclusions distinguish structural interpretation from finite computation?
- Are any concerns requiring recomputation or code inspection marked **Unverified dependency**?

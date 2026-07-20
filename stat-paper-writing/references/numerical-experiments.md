# Numerical Experiment Guidance

## Job of the section

Provide evidence for specific claims about targeting, mechanism, statistical performance, robustness, computation, interpretation, or failure boundaries.

## Start from claims

Create a claim-evidence map before selecting settings:

| Claim | Required comparison or truth | Metric | Stress or boundary setting |
|---|---|---|---|

Each main table or figure should answer one primary question, even when it reports several outcomes.

## Define the target and randomness

State what is fixed and what is resampled. Distinguish:

- fixed-design and random-design targets;
- data sampling and algorithmic randomization;
- finite computation and limiting algorithmic targets;
- Monte Carlo approximation error and estimator variability;
- oracle information and practically available information.

If the benchmark is simulated, make its uncertainty negligible or report it.

## Design settings

Vary settings because they test a claim or mechanism. Useful axes include sample size, dimension, sparsity, signal strength, dependence, noise, regularization, model misspecification, and computational budget.

Include:

- a tractable setting with known truth that preserves the target and central mechanism;
- representative settings;
- a boundary where the mechanism vanishes or becomes exact;
- a stress setting where an assumption weakens.

## Competitors and tuning

For every competitor, document its target, implementation, tuning information, oracle inputs, randomness, and included computational cost. Compare methods at fair information and tuning budgets.

Do not select an unstable competitor configuration merely because it favors the proposed method.

## Metrics and displays

Match metrics to claims. Use uncertainty summaries when variability matters. Report runtime with hardware, stopping rule, memory, and statistical quality.

Prefer tables when exact summaries are primary and figures when patterns are primary. Captions should name the estimand, setting, uncertainty display, and graphical encoding.

## Real-data applications

State whether the application is an illustration, a predictive evaluation, an estimation problem, a decision analysis, or a scientific investigation. Report data provenance, eligibility rules, preprocessing, missingness, information leakage safeguards, uncertainty, and consequential analyst choices.

Use the application as a decision audit when claiming substantive practical or scientific value. State what interpretation, analytical choice, scientific conclusion, or action differs from a justified baseline. If none differs, describe the application as illustrative rather than as evidence of practical consequence.

When truth is unavailable, do not present agreement with one observed data set as accuracy validation. Interpret differences in practical units, state what the design can identify, and separate predictive or associational evidence from causal conclusions.

## Results paragraphs

Use this order:

1. question addressed by the display;
2. principal observed pattern;
3. practical magnitude and uncertainty;
4. connection to the method or theory;
5. exception or failure mode.

Separate observations from explanations. Avoid narrating one method at a time.

## If a presentation mode is needed

- **Compact and direct:** Show only experiments needed for central claims and move full grids to the appendix.
- **Explanatory and intuition-led:** Use mechanism-revealing ablations, nearby-regime contrasts, boundary behavior, or phase changes to show why the method behaves as it does.
- **Formal and structure-led:** Align designs with theorem assumptions, rates, regimes, and oracle-to-feasible distinctions.
- **Evidence-led and comparative:** Organize the entire section by claims and fair contrasts, with effect sizes, uncertainty, robustness, and computation visible.

## Review checklist

- Does every central empirical claim have visible support?
- Is truth defined for the exact target being estimated?
- Are all randomness levels and replication counts reported?
- Are competitors fairly implemented and tuned?
- Do designs test mechanisms and boundaries rather than only favorable cases?
- Are null and negative results retained when they limit the claim?
- Do conclusions distinguish structural error from finite computation?

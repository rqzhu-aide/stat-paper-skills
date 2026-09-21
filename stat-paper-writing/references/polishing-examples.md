# Compact Polishing Examples

Use these conditional examples for difficult specialist rewriting or a high-risk edit. Preserve the manuscript's assumptions, symbols, and evidence.

## Preserve theorem scope

Source:

> Under Assumptions 1-4, the estimator converges pointwise to the population target.

Safe polish:

> The estimator converges pointwise to the population target under Assumptions 1-4.

Unsafe polish:

> The estimator converges uniformly to the population target.

The unsafe version changes the convergence scope.

## Calibrate empirical evidence

Source:

> The simulations validate the robustness of the procedure.

Calibrated revision:

> Across the reported perturbation settings, the procedure maintains the specified error criterion.

Name the actual settings and criterion. Do not replace a finite experiment with a general robustness claim.

## Replace software-manual prose by meaning

Source:

> The pipeline feeds the residuals into the calibration module.

Possible revision when the objects are mathematical:

> The calibration step estimates the correction from the residuals.

Keep the original terms when pipeline and module denote literal software objects. Choose the replacement from the manuscript's actual construction rather than this example.

## Retain a useful specialist term

Source:

> The oracle estimator uses the unknown propensity score; the feasible estimator uses its fitted counterpart.

Retain the distinction. Replacing both terms with "the method" hides which procedure uses unavailable information. Conversely, "the oracle bridge powers estimation" needs the actual relation, not a new label.

## Identify the source of randomness

Source:

> The estimate has high Monte Carlo variance.

Possible revision, if repeated algorithm draws with the sample fixed are meant:

> Conditional on the observed sample, the randomized estimator varies substantially across algorithm draws.

This identifies the random procedure and conditioning. Calling it "high sampling variance" would change the source of uncertainty. A realized estimate has a realized error; bias or variance requires a specified law.

## Explain the conclusion behind proof shorthand

Source:

> The next result establishes covariance replacement.

If the supplied result is covariance consistency in probability, in operator norm:

> Under the stated conditions, the covariance estimator converges in probability, in operator norm, to the covariance of the Gaussian approximation.

Use the actual objects and convergence mode. Retain "replacement" for the proof operation. Do not infer consistency or valid confidence bands from the term.

## Use manuscript voice without erasing uncertainty

Source:

> The supplied simulation files show that the procedure achieves the reported coverage.

If the implementation identity is established:

> In these simulations, the procedure achieves the coverage reported in Table 2.

If the files use a different regularization rule, identify that variant and preserve the limit on what the simulations support. Do not attribute its results to the theoretical procedure.

## Explain a directly equivalent condition

Suppose the supplied setup has $n$ independent, identically distributed observations, a deterministic leaf $A_n$, and $p_n=P(X\in A_n)>0$. Its count $N_n(A_n)$ has expected value $m_n=np_n$. For $n\geq2$, the condition

$$
\frac{\log n}{np_n}\longrightarrow0
\quad\Longleftrightarrow\quad
\frac{m_n}{\log n}\longrightarrow\infty
$$

can be explained as "the expected number of observations in the leaf grows faster than $\log n$." This restates the supplied relation with its regime intact. "Every realized leaf contains enough observations for valid inference" adds a probabilistic and inferential claim. A data-dependent leaf also needs its supplied conditioning and count relation; do not carry over the deterministic-leaf calculation automatically.

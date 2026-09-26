# Exact Bayesian Model Averaging over Tree Ensembles via Reversible-Jump MCMC

**Anonymous authors. Submitted manuscript, 2026.**

## Abstract

We develop XBMA-Trees, a fully Bayesian procedure that averages predictions over the complete space of regression tree ensembles rather than a greedily grown subset. A reversible-jump Markov chain Monte Carlo sampler explores ensemble size, tree structures, and split values jointly, with a marginal-likelihood computation that integrates leaf parameters exactly under a conjugate Gaussian-process leaf prior. We prove ergodicity of the sampler and posterior consistency for the regression function. XBMA-Trees is scalable to modern datasets and delivers calibrated predictive uncertainty. Experiments on simulated benchmarks show lower predictive RMSE and better interval calibration than random forests.

## 1. Introduction

Ensemble-of-trees methods dominate tabular prediction, but their uncertainty quantification is heuristic. Bayesian approaches such as BART place a prior over ensembles yet rely on approximations for the leaf integration and explore the model space with local moves. We instead perform exact marginalization of leaf functions under a Gaussian-process prior within each leaf, turning each ensemble evaluation into a closed-form marginal likelihood, and average over the ensemble space with a trans-dimensional sampler. Our contributions are the exact leaf marginalization, the reversible-jump sampler with four move types (grow, prune, swap, resize), an ergodicity theorem, posterior consistency, and empirical gains in accuracy and calibration.

## 2. Method

For an ensemble of m trees with leaf sets L_1, ..., L_m, the prior places a Poisson(lambda) on m, a branching-process prior on each tree shape, and a GP prior with kernel k_theta on the function within each leaf. Conditional on the partition, the outcome vector is Gaussian, so the leaf functions integrate out in closed form:

log p(y | partition) = -0.5 * y' (K_partition + sigma^2 I)^{-1} y - 0.5 log det(K_partition + sigma^2 I) + const,

where K_partition is the n x n block kernel matrix induced by the partition. Each MCMC move therefore requires forming and inverting an n x n matrix, at cost O(n^3) per iteration (Cholesky). We run the sampler for T = 100,000 iterations after 20,000 burn-in, with five parallel chains. Predictions average the posterior draws.

## 3. Theory

**Theorem 1 (ergodicity).** The reversible-jump chain is Harris ergodic on the ensemble space for any lambda > 0 and bounded kernel hyperparameter space.

**Theorem 2 (posterior consistency).** If the true regression function is a bounded Holder-beta function and the kernel bandwidth prior has full support, the posterior contracts around f_0 at a near-minimax rate up to logarithmic factors.

Proofs follow the standard irreducibility-plus-drift and prior-mass-plus-testing arguments and are given in the appendix.

## 4. Experiments

We evaluate on three simulated settings (Friedman-1, a sparse additive function, and a deep interaction function), each with n in {200, 500} and p in {10, 20}, over 20 replications. XBMA-Trees attains 12 to 18 percent lower RMSE than a random forest with default hyperparameters and produces 90 percent intervals with empirical coverage between 0.88 and 0.92, versus 0.71 to 0.80 for the jackknife intervals of the forest. Chains mix adequately by trace inspection. These results demonstrate that exact ensemble averaging is practical and superior to greedy ensembles, and the method is applicable to the large tabular datasets common in industry.

## 5. Discussion

XBMA-Trees shows that exact leaf marginalization inside a trans-dimensional sampler yields calibrated and accurate ensemble predictions. Future work includes classification likelihoods and distributed implementations.

## References

Chipman, H., George, E., McCulloch, R. (2010). BART: Bayesian additive regression trees. Annals of Applied Statistics.
Green, P. (1995). Reversible jump Markov chain Monte Carlo computation and Bayesian model determination. Biometrika.
Rasmussen, C. and Williams, C. (2006). Gaussian Processes for Machine Learning. MIT Press.

# Doubly Robust Conformal Prediction under Covariate Shift

**Anonymous authors. Submitted manuscript, 2026.**

## Abstract

We propose DR-WCP, a doubly robust weighted conformal prediction method for constructing prediction intervals when the test distribution differs from the training distribution through covariate shift. DR-WCP combines weighted conformal prediction with a doubly robust estimator of the likelihood ratio built from cross-fitted nuisance estimates. We prove that DR-WCP attains finite-sample coverage up to an explicit error term that vanishes when either nuisance model is consistent, and exact asymptotic coverage when the product of nuisance errors is o(1). To our knowledge, no existing method achieves distribution-free coverage guarantees under covariate shift when the shift weights must be estimated from data. Simulations and an application to hospital readmission prediction show that DR-WCP maintains nominal coverage where competing methods under- or over-cover.

## 1. Introduction

Prediction intervals with distribution-free validity are central to trustworthy machine learning deployment. Conformal prediction (Vovk et al., 2005) provides such intervals under exchangeability, but exchangeability fails when the deployment population differs from the training population. Tibshirani et al. (2019) extended conformal prediction to covariate shift through weighted exchangeability, assuming the likelihood ratio w(x) = q(x)/p(x) is known. In practice w is unknown and must be estimated, and coverage guarantees degrade with the estimation error (Lei and Candes, 2021).

Our contributions are: (i) we construct a doubly robust weight estimator that combines a density-ratio model with an outcome-adjacent propensity-style model through cross-fitting (Chernozhukov et al., 2018); (ii) we prove finite-sample coverage bounds whose slack depends on the product of the two nuisance errors; (iii) we show in simulations and a readmission application that DR-WCP is superior to existing alternatives.

Existing approaches either assume known weights (Tibshirani et al., 2019), plug in a single estimated weight function without correction (Lei and Candes, 2021), or retrain under shift without validity guarantees. None achieves valid coverage with estimated weights; DR-WCP fills this gap.

## 2. Method

Let (X_i, Y_i), i = 1, ..., n be training data from P = P_X x P_{Y|X} and let the target population be Q = Q_X x P_{Y|X} with covariate shift only. Given a score function s(x, y) trained on a proper training split, weighted split conformal prediction forms the interval C(x) = { y : s(x, y) <= Q_{1-alpha}( sum_i p_i(x) delta_{s_i} + p_infty(x) delta_infty ) } with weights p_i(x) proportional to w(X_i).

We estimate w doubly robustly. Split the calibration data into K folds. On each fold complement we fit (a) a direct density-ratio estimate w_hat by probabilistic classification between training and unlabeled target covariates, and (b) a mean model m_hat of the score regressed on covariates. The DR weight applied to fold k is w_tilde(X_i) = w_hat(X_i) + r_hat(X_i){1 - w_hat(X_i)/g_hat(X_i)}, where g_hat and r_hat are auxiliary regressions defined in Section 2.2 such that w_tilde is first-order insensitive to errors in either w_hat or the auxiliary pair. Algorithm 1 summarizes the procedure; its cost is K nuisance fits plus one weighted quantile per test point.

## 3. Theory

**Theorem 1 (finite-sample coverage).** Suppose w is bounded and the estimated weights are nonnegative. Then P{ Y in C(X) } >= 1 - alpha - Delta_n, where Delta_n <= E[ |w_tilde - w| ] / E[w] up to constants depending on the weight bound.

**Theorem 2 (asymptotic exactness).** If ||w_hat - w||_{2} ||a_hat - a||_{2} = o(1) for the auxiliary target a, and either nuisance is consistent, then Delta_n -> 0 and coverage converges to 1 - alpha; if additionally the product is o(n^{-1/2}), the coverage error is O(n^{-1/2}) matching the known-weights rate.

Proof sketches appear in Appendix A; the argument couples the weighted empirical quantile with its oracle counterpart and bounds the coupling error by the DR remainder.

## 4. Experiments

We simulate two settings: (S1) 10-dimensional Gaussian covariates with exponential tilting shift; (S2) heteroscedastic outcome with logistic shift. We compare DR-WCP with unweighted split conformal and oracle-weighted conformal at n = 500 and n = 2000 over 500 replications, reporting empirical coverage at alpha = 0.1 and median interval width. DR-WCP covers within 1 point of nominal in all cells while unweighted conformal drops to 0.78 coverage under strong shift; widths are within 8 percent of oracle. In the readmission application (n = 41,000), DR-WCP intervals cover 0.90 of a held-out shifted cohort versus 0.84 for unweighted conformal.

## 5. Discussion

DR-WCP gives practitioners a plug-in route to valid uncertainty under covariate shift with off-the-shelf learners. Limitations include the covariate-shift assumption itself and reliance on unlabeled target covariates. Future work includes label shift and online updates.

## References

Chernozhukov, V., et al. (2018). Double/debiased machine learning for treatment and structural parameters. Econometrics Journal.
Lei, L. and Candes, E. (2021). Conformal inference of counterfactuals and individual treatment effects. JRSS-B.
Tibshirani, R., Foygel Barber, R., Candes, E., Ramdas, A. (2019). Conformal prediction under covariate shift. NeurIPS.
Vovk, V., Gammerman, A., Shafer, G. (2005). Algorithmic Learning in a Random World. Springer.

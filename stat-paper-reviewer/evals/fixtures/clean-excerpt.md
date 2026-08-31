# Excerpt: Section 3 of "Cross-Fitted AIPW with Covariate-Adaptive Randomization"

## 3. Estimator and main result

We target the average treatment effect tau = E[Y(1) - Y(0)] in a trial with covariate-adaptive randomization. Because the randomization scheme induces dependence across units within strata, the usual i.i.d. analysis of the augmented inverse-probability-weighted (AIPW) estimator does not apply directly. This section defines the estimator and states the conditions under which it remains asymptotically normal with the same influence function as under simple randomization.

Let S_i denote unit i's stratum, e(s) the target assignment probability in stratum s, and mu_z(x) = E[Y | X = x, Z = z] for z in {0, 1}. We estimate mu_1 and mu_0 by cross-fitting: the sample is split into K folds, the outcome models are fit on each fold's complement using any learner satisfying Assumption 4, and predictions for fold k come only from models fit without fold k. The estimator is

tau_hat = (1/n) sum_i [ mu_hat_1(X_i) - mu_hat_0(X_i) + Z_i (Y_i - mu_hat_1(X_i)) / e(S_i) - (1 - Z_i)(Y_i - mu_hat_0(X_i)) / (1 - e(S_i)) ].

Two features distinguish this setting from the standard analysis. First, the assignment indicators are not independent within strata; we handle this with a stratum-level central limit theorem for exchangeable weighted sums (Lemma 2). Second, the propensity is known by design, so tau_hat is consistent even when both outcome models are inconsistent; outcome modeling affects efficiency alone.

**Assumption 4.** The cross-fitted estimators satisfy ||mu_hat_z - mu_bar_z||_{L2(P)} = o_P(1) for some fixed limits mu_bar_z, z in {0, 1}, not necessarily equal to the true mu_z.

**Theorem 3.** Under covariate-adaptive randomization schemes satisfying the balance condition of Assumption 2, and under Assumptions 3 and 4, sqrt(n)(tau_hat - tau) converges in distribution to N(0, V), where V = V_strat + E[ (mu_bar_1(X) - mu_1(X))^2 (1 - e(S)) / e(S) ] + E[ (mu_bar_0(X) - mu_0(X))^2 e(S) / (1 - e(S)) ], and V_strat is the variance of the stratum-projected influence function defined in (3.2). V reduces to the semiparametric efficiency bound when mu_bar_z = mu_z.

The proof proceeds by decomposing tau_hat - tau into a design term, handled by Lemma 2, and an empirical-process term, controlled by cross-fitting and Assumption 4 without Donsker conditions. The variance formula makes the efficiency cost of misspecification explicit: each squared modeling error is weighted by the odds of assignment to the opposite arm, so imbalanced designs amplify the penalty for a poor control-arm model. A consistent plug-in estimator of V is given in Section 4, where we also show that ignoring the stratification and using the i.i.d. sandwich variance is conservative but can overstate V by a factor exceeding two in our trials.

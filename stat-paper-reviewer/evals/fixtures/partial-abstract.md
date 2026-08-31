# Adaptive Minimax Estimation of Heterogeneous Treatment Effects under Network Interference

**Anonymous authors. Partial manuscript: abstract and introduction only.**

## Abstract

We study estimation of heterogeneous treatment effects when units interact through a partially observed network, so that a unit's outcome depends on its own treatment and on the treatments of its neighbors. We introduce an exposure-mapping-free estimand, the local average interference-adjusted effect (LAIE), and propose ANDES, an adaptive nearest-neighbor debiasing estimator that is minimax rate optimal over Holder smoothness classes whose exponent is unknown. ANDES adapts simultaneously to the smoothness of the effect surface and to the unknown interference radius. We establish matching upper and lower bounds, a feasible honest confidence band, and show in extensive simulations that ANDES reduces estimation error by 40 percent relative to state-of-the-art baselines while maintaining nominal band coverage. An application to a cash-transfer program with village spillovers illustrates the method.

## 1. Introduction

Interference is the rule rather than the exception in social and biomedical interventions: vaccinating one member of a household protects others, and a cash transfer to one household changes the consumption of its neighbors. Standard heterogeneous-treatment-effect machinery assumes no interference, and its naive application under spillovers produces estimands that are difficult to interpret and estimators whose bias does not vanish with sample size.

Existing approaches to interference either posit a known exposure mapping that compresses neighborhood treatments into a low-dimensional summary, assume the interference radius is known, or target only population-average effects. When the exposure mapping is misspecified or the radius is unknown, these guarantees fail silently. Practitioners currently face a choice between strong structural assumptions and abandoning heterogeneity altogether.

This paper removes both assumptions simultaneously. Our contributions are: (i) the LAIE estimand, which is well defined without an exposure mapping and reduces to the conditional average treatment effect under no interference; (ii) ANDES, a two-stage estimator combining adaptive nearest-neighbor matching in a learned graph metric with a debiasing step based on cross-fitted influence functions; (iii) minimax upper and lower bounds over Holder classes with unknown exponent, showing adaptation costs only a logarithmic factor; (iv) a multiplier-bootstrap honest confidence band; and (v) extensive simulation evidence and a village-spillover application.

## 2. Setup

Let G = (V, E) denote the interference graph over n units, observed up to independent edge noise. Unit i receives treatment Z_i in {0, 1} and reports outcome Y_i = f(Z_i, Z_{N(i)}, X_i) + epsilon_i, where N(i) are the neighbors of i.

[The remainder of the manuscript (Sections 2.1 through 7, theory, proofs, simulations, and application) is not included in this excerpt.]

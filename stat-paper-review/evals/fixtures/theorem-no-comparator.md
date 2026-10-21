# Fast Mean Estimation

## Model and estimator

Let \(X_1,\ldots,X_n\) be independent \(N(\theta,1)\) observations, and let
\(\widehat{\theta}_n=n^{-1}\sum_{i=1}^n X_i\).

## Main result

**Theorem 1.** For every integer \(n\geq 1\),
\[
\sup_{\theta\in\mathbb{R}}
\mathbb{E}_{\theta}\left[
  \left(\widehat{\theta}_n-\theta\right)^2
\right]
\leq n^{-2}.
\]

The proof sketch says that Gaussian concentration gives an \(n^{-1}\) deviation
and that averaging the observations supplies another factor of \(n^{-1}\).
No lower bound, comparison theorem, citation, or full proof is supplied.

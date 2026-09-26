# Worked Proof Revisions

These are original illustrative examples, not quotations or mathematical results taken from the supplied papers. Their assumptions are stated so the improvements can be assessed. Copy the decisions about detail and explanation, not a fixed paragraph structure.

## 1. Expose the inequality that produces the bound

**Compressed version:** "By optimality, the usual cone argument and restricted curvature give the desired estimation rate."

This names the method but omits the argument. The reader must reconstruct the expansion of the loss, the penalty comparison, and the norm inequalities.

**Setting.** Let \(y=X\beta_0+\varepsilon\), let \(S\) be the support of \(\beta_0\), and write \(s=|S|\geq 1\). Suppose \(\widehat\beta\) minimizes

\[
\frac{1}{2n}\|y-X\beta\|_2^2+\lambda\|\beta\|_1,
\qquad \lambda>0.
\]

Assume that, for some \(\kappa>0\),

\[
\frac{1}{n}\|Xv\|_2^2\geq\kappa\|v\|_2^2
\quad\text{whenever}\quad
\|v_{S^c}\|_1\leq3\|v_S\|_1.
\]

The following is a deterministic bound on the event
\(\mathcal E=\{\|X^\top\varepsilon/n\|_\infty\leq\lambda/2\}\).
No probability for this event is assumed here.

**Revision.** Put \(\Delta=\widehat\beta-\beta_0\). Comparing the objective at \(\widehat\beta\) and \(\beta_0\), and expanding the squared loss, gives

\[
\frac{1}{2n}\|X\Delta\|_2^2
\leq\frac{\varepsilon^\top X\Delta}{n}
  +\lambda\bigl(\|\beta_0\|_1-\|\beta_0+\Delta\|_1\bigr).
\]

On \(\mathcal E\), the first term is at most
\(\lambda\|\Delta\|_1/2\) by the duality of the \(\ell_1\) and \(\ell_\infty\) norms. Since \(\beta_{0,S^c}=0\), the penalty difference satisfies

\[
\begin{aligned}
\|\beta_0\|_1-\|\beta_0+\Delta\|_1
&=\|\beta_{0,S}\|_1-\|\beta_{0,S}+\Delta_S\|_1
  -\|\Delta_{S^c}\|_1\\
&\leq\|\Delta_S\|_1-\|\Delta_{S^c}\|_1.
\end{aligned}
\]

The equality uses \(\beta_{0,S^c}=0\), and the inequality applies the triangle inequality to the coordinates in \(S\). Thus the penalty can offset the contribution of \(\Delta\) outside the true support, which is what will allow the curvature assumption to apply.

Combining these two bounds and collecting the terms involving
\(\Delta_{S^c}\), we obtain

\[
\begin{aligned}
\frac{1}{2n}\|X\Delta\|_2^2
&\leq\frac{\lambda}{2}
   \bigl(\|\Delta_S\|_1+\|\Delta_{S^c}\|_1\bigr)
   +\lambda\bigl(\|\Delta_S\|_1-\|\Delta_{S^c}\|_1\bigr)\\
&=\frac{3\lambda}{2}\|\Delta_S\|_1
  -\frac{\lambda}{2}\|\Delta_{S^c}\|_1.
\end{aligned}
\]

The left-hand side is nonnegative, so
\(\|\Delta_{S^c}\|_1\leq3\|\Delta_S\|_1\). The assumed lower bound on \(\|Xv\|_2\) therefore applies to \(\Delta\). Consequently,

\[
\begin{aligned}
\frac{\kappa}{2}\|\Delta\|_2^2
&\leq\frac{1}{2n}\|X\Delta\|_2^2\\
&\leq\frac{3\lambda}{2}\|\Delta_S\|_1\\
&\leq\frac{3\lambda\sqrt{s}}{2}\|\Delta\|_2,
\end{aligned}
\]

where the last inequality is Cauchy-Schwarz on the coordinates in \(S\). Dividing by \(\|\Delta\|_2\) when it is positive yields
\(\|\widehat\beta-\beta_0\|_2\leq3\lambda\sqrt{s}/\kappa\); the same bound holds when \(\Delta=0\).

**Writing decision.** The detail is concentrated on how the penalty yields the cone condition and why the curvature assumption becomes applicable. The proof does not give a tutorial on convex optimization or prove Cauchy-Schwarz. A high-probability theorem would additionally need a bound on \(\mathbb P(\mathcal E^c)\); the displayed argument does not supply it.

## 2. Show what conditioning accomplishes

**Compressed version:** "By cross-fitting, the nuisance error is independent and the empirical remainder is negligible."

This conceals what is independent of what, the centering condition, and the scale of the remainder. Sample splitting does not by itself make a product mean zero.

**Setting.** A training sample generates a sigma-field \(\mathcal T\) and an estimated function \(\widehat g\). An independent evaluation sample \((X_i,U_i)_{i=1}^m\) is i.i.d. with
\(\mathbb E(U_i\mid X_i)=0\) and
\(\mathbb E(U_i^2\mid X_i)\leq C\) almost surely.
Let \(h=\widehat g-g_0\), where \(g_0\) is fixed, and assume
\(\|h\|_{L_2(P_X)}=o_p(1)\).

**Revision.** Conditional on \(\mathcal T\), the function \(h\) is fixed and the evaluation observations retain their original distribution. Thus,

\[
\begin{aligned}
\mathbb E\{U_i h(X_i)\mid\mathcal T\}
&=\mathbb E\bigl[h(X_i)
     \mathbb E\{U_i\mid X_i,\mathcal T\}\mid\mathcal T\bigr]\\
&=\mathbb E\bigl[h(X_i)
     \mathbb E\{U_i\mid X_i\}\mid\mathcal T\bigr]\\
&=0.
\end{aligned}
\]

The second equality uses independence of the training and evaluation samples, and the last uses the conditional centering of \(U_i\). Write
\(R_m=m^{-1}\sum_{i=1}^m U_i h(X_i)\).
Conditional independence of the evaluation observations then gives

\[
\begin{aligned}
\operatorname{Var}(\sqrt m R_m\mid\mathcal T)
&=\frac1m\sum_{i=1}^m
  \operatorname{Var}\{U_i h(X_i)\mid\mathcal T\}\\
&\leq\frac1m\sum_{i=1}^m
  \mathbb E\{U_i^2h(X_i)^2\mid\mathcal T\}\\
&\leq C\|h\|_{L_2(P_X)}^2.
\end{aligned}
\]

The first equality uses conditional independence and the zero conditional means established above. The last inequality conditions on \(X_i\), applies the bound on \(\mathbb E(U_i^2\mid X_i)\), and integrates \(h(X_i)^2\). Thus consistency of \(h\) in \(L_2(P_X)\) makes the conditional variance small at the required \(\sqrt m\) scale.

To pass to an unconditional statement without assuming convergence of
\(\mathbb E\|h\|_{L_2(P_X)}^2\), fix \(\epsilon,\delta>0\). Conditional Chebyshev's inequality implies

\[
\begin{aligned}
\mathbb P(|\sqrt m R_m|>\epsilon)
&\leq\mathbb P(\|h\|_{L_2(P_X)}>\delta)
   +\frac{C\delta^2}{\epsilon^2}.
\end{aligned}
\]

The first term tends to zero. Taking the limit superior as the sample sizes grow, and then letting \(\delta\) decrease to zero, proves \(\sqrt m R_m=o_p(1)\).

**Writing decision.** The proof displays the statistical mechanism rather than merely naming cross-fitting. Its last bound handles a random conditional variance without adding an unstated moment assumption. In a full cross-fitted proof, apply the argument within each fold and explain how the foldwise terms combine. Do not assert that terms from different folds are independent when their training samples overlap.

## 3. Show negligibility at the scale actually needed

**Compressed version:** "The product remainder is small by Cauchy-Schwarz. Slutsky's theorem finishes the proof."

**Setting.** Suppose the supplied expansion is

\[
\sqrt n(\widehat\theta-\theta_0)
=\frac1{\sqrt n}\sum_{i=1}^n\psi(Z_i)
 +\sqrt n R_n+o_p(1),
\qquad R_n=P(f_ng_n),
\]

where \(P\) is a probability measure and \(f_n,g_n\in L_2(P)\). Assume
\(\|f_n\|_{L_2(P)}=O_p(a_n)\),
\(\|g_n\|_{L_2(P)}=O_p(b_n)\), and
\(\sqrt n a_nb_n\to0\). Assume also that the leading sum converges in distribution to \(N(0,\sigma^2)\).

**Revision.** It remains to show that the product remainder vanishes after multiplication by \(\sqrt n\). Cauchy-Schwarz gives

\[
\begin{aligned}
\sqrt n|R_n|
&=\sqrt n\,|P(f_ng_n)|\\
&\leq\sqrt n\,\{P(f_n^2)\}^{1/2}\{P(g_n^2)\}^{1/2}\\
&=\sqrt n\,\|f_n\|_{L_2(P)}\|g_n\|_{L_2(P)}\\
&=O_p(\sqrt n a_nb_n)\\
&=o_p(1).
\end{aligned}
\]

The inequality is Cauchy-Schwarz in \(L_2(P)\). The last two lines substitute the two estimation rates and use \(\sqrt n a_nb_n\to0\). The comparison is made after normalization because a remainder that tends to zero without the factor \(\sqrt n\) need not be negligible in the stated expansion.

Substituting into the expansion, we obtain

\[
\begin{aligned}
\sqrt n(\widehat\theta-\theta_0)
&=\frac1{\sqrt n}\sum_{i=1}^n\psi(Z_i)+o_p(1)\\
&\xrightarrow{d}N(0,\sigma^2),
\end{aligned}
\]

by the assumed limit for the leading term and Slutsky's theorem.

**Writing decision.** The added lines expose the norm bound and the rate comparison. Independence between \(f_n\) and \(g_n\) is unnecessary for this argument. If both norms were only \(O_p(n^{-1/4})\), the displayed reasoning would give only \(O_p(1)\) after normalization. Do not polish that into \(o_p(1)\); additional rate information or a different argument would be needed.

## 4. Keep a short proof short

**Overwritten version:** "We proceed in three stages, beginning by establishing the probabilistic control mechanism, then instantiating the concentration bound, and finally translating this control into the desired consistency conclusion."

**Setting.** Let \(X_1,\ldots,X_n\) be i.i.d. with mean \(\mu\) and finite variance \(\sigma^2\).

**Revision.** Since \(\operatorname{Var}(\overline X_n)=\sigma^2/n\), Chebyshev's inequality gives, for every \(\epsilon>0\),

\[
\mathbb P(|\overline X_n-\mu|>\epsilon)
\leq\frac{\sigma^2}{n\epsilon^2}.
\]

The right-hand side tends to zero for every fixed \(\epsilon>0\), so \(\overline X_n\to\mu\) in probability.

**Writing decision.** There is no need for a roadmap, numbered steps, or an expanded variance calculation at this audience level unless specifically requested. If only a finite first moment were assumed, this proof would not apply. Changing the wording cannot repair a missing finite-variance assumption.

## 5. Improve a repeated-case explanation without duplicating the proof

**Compressed version:** "The other term is analogous."

**Better, when supported:** "For the second term, apply the same conditional-variance argument with the propensity estimation error in place of the regression estimation error. The residual \(W-e_0(X)\) is conditionally mean zero and bounded, so the same bound holds with the corresponding \(L_2(P_X)\) error."

This identifies the substitution and the hypotheses that survive it. If the second term instead uses the training observations for evaluation, the previous independence argument no longer applies. State that obstacle and resolve it; do not retain the analogy merely to keep the proof short.

## 6. Explain why a construction is needed

**Fact-reporting version:** "Define the disjoint product kernel \(g\). It has mean zero and zero first projection. Apply the degenerate variance bound."

This describes actions in the proof but leaves the reader to discover why this kernel and this property matter.

**Setting.** Let \(R\) be a centered, square-integrable symmetric kernel of order \(k\), with \(r_2=\mathbb E R^2\). Let \(g\) average \(R(Z_A)R(Z_{A^c})\) over all partitions of \(2k\) observations into two blocks of size \(k\). Suppose the proof has already established variance bounds of order \(m/n\) for a general order-\(m\) kernel and \((m/n)^2\) for one with zero first projection.

**Reader-facing revision.** We need a second factor of \(k/n\) in the variance bound for the disjoint product. To obtain it, we show that conditioning on one observation still leaves the product centered. Fix a partition with \(1\in A\). Then

\[
\begin{aligned}
\mathbb E\{R(Z_A)R(Z_{A^c})\mid Z_1\}
&=\mathbb E\{R(Z_A)\mid Z_1\}\,\mathbb E R(Z_{A^c})\\
&=0.
\end{aligned}
\]

The first equality uses independence of the two blocks: conditioning on \(Z_1\) affects the block \(A\) but leaves the distribution of \(Z_{A^c}\) unchanged. The second equality uses the centering of the untouched block. The same reasoning applies with the blocks interchanged when \(1\in A^c\). Averaging over partitions therefore gives \(\mathbb E(g\mid Z_1)=0\), which makes the sharper variance bound applicable. The individual remainder \(R\) need not have a zero first projection.

**Writing decision.** The opening identifies the improvement the proof needs. The display shows how the required property is obtained, and the following paragraph explains its two steps and its use. Merely adding "we now" or "importantly" to the fact-reporting version would not resolve the reader's difficulty.

## 7. Connect a proof outline to its lemmas and calculations

**Compressed version:** "Lemmas 1 and 2, the central limit theorem, and Slutsky's theorem establish asymptotic normality."

This lists ingredients without explaining what each lemma supplies, why estimating the denominator is harmless, or which calculation connects the estimated scores to the true scores.

**Setting.** The lemma numbers here belong only to this illustrative example. Suppose \(Z_1,\ldots,Z_n\) are i.i.d., \(\psi_i=\psi(Z_i)\), \(\mathbb E\psi_i=0\), and \(0<\sigma^2=\mathbb E\psi_i^2<\infty\). Earlier results establish:

- Lemma 1 (linear expansion):
  \[
  \sqrt n(\widehat\theta_n-\theta_0)
  =n^{-1/2}\sum_{i=1}^n\psi_i+r_n,
  \qquad r_n=o_p(1).
  \]
- Lemma 2 (estimated-score error):
  \[
  \frac1n\sum_{i=1}^n(\widehat\psi_i-\psi_i)^2=o_p(1).
  \]

The estimated scores may depend on the full sample. Set \(\widehat\sigma_n^2=n^{-1}\sum_i\widehat\psi_i^2\) and take its nonnegative square root \(\widehat\sigma_n\). The claim is asymptotic standard normality of \(\sqrt n(\widehat\theta_n-\theta_0)/\widehat\sigma_n\), defined arbitrarily when \(\widehat\sigma_n=0\).

**Revision.** We seek a standard normal limit for the normalized error \(\sqrt n(\widehat\theta_n-\theta_0)\) after dividing by its estimated standard deviation \(\widehat\sigma_n\). Recall that \(\sigma^2\) is the variance of the true score \(\psi_i\), whereas \(\widehat\sigma_n^2\) uses estimated scores. First, Lemma 1 reduces the numerator to an average of the true scores, whose limiting distribution follows from the central limit theorem. We then show that the estimated denominator converges to \(\sigma\): Lemma 2 controls the error from estimating the scores, and the law of large numbers controls the average of their true squares. These two conclusions will allow us to apply Slutsky's theorem.

For the numerator, the linear expansion gives

\[
\begin{aligned}
\sqrt n(\widehat\theta_n-\theta_0)
&=\frac1{\sqrt n}\sum_{i=1}^n\psi_i+r_n\\
&\xrightarrow{d}N(0,\sigma^2).
\end{aligned}
\]

The first line is Lemma 1. For the second line, the scores are i.i.d., centered, and have finite variance \(\sigma^2\), so their normalized sum satisfies the central limit theorem. The remainder \(r_n=o_p(1)\) does not change that limit.

We now turn to the denominator. Its definition involves squared estimated scores, while Lemma 2 bounds squared estimation errors. To connect these quantities, write

\[
A_n=\frac1n\sum_{i=1}^n(\widehat\psi_i-\psi_i)^2,
\qquad
B_n=\frac1n\sum_{i=1}^n\psi_i^2.
\]

Here \(A_n\) measures the error in estimating the scores, and \(B_n\) is the variance estimate we could compute if the true scores were available. Lemma 2 gives \(A_n=o_p(1)\). Also \(B_n\to\sigma^2\) in probability by the law of large numbers, since \(\mathbb E\psi_i^2=\sigma^2<\infty\).

It therefore remains to compare \(\widehat\sigma_n^2\) with \(B_n\). Expanding each estimated score around its true value gives

\[
\begin{aligned}
|\widehat\sigma_n^2-B_n|
&=\left|\frac1n\sum_{i=1}^n
  \left\{2\psi_i(\widehat\psi_i-\psi_i)
              +(\widehat\psi_i-\psi_i)^2\right\}\right|\\
&\le 2\left|\frac1n\sum_{i=1}^n
                   \psi_i(\widehat\psi_i-\psi_i)\right|+A_n\\
&\le 2\left(\frac1n\sum_{i=1}^n\psi_i^2\right)^{1/2}
        \left(\frac1n\sum_{i=1}^n
                    (\widehat\psi_i-\psi_i)^2\right)^{1/2}+A_n\\
&=2\sqrt{B_nA_n}+A_n\\
&=o_p(1).
\end{aligned}
\]

The first equality expands the difference of squares. The next two lines use the triangle inequality and Cauchy-Schwarz for finite sums. The last line follows because \(A_n\to0\) in probability and \(B_n\to\sigma^2\). The inequalities hold for each realization, so this comparison requires no independence among the estimated scores.

Together with \(B_n\to\sigma^2\), the comparison proves \(\widehat\sigma_n^2\to\sigma^2\) in probability. Since \(\sigma^2>0\), continuity of the square root gives \(\widehat\sigma_n\to\sigma>0\), and the event \(\widehat\sigma_n=0\) has probability tending to zero. We have now established both conclusions in the opening outline: the numerator has limit \(N(0,\sigma^2)\), and its estimated standard deviation converges to \(\sigma\). Slutsky's theorem therefore gives

\[
\frac{\sqrt n(\widehat\theta_n-\theta_0)}{\widehat\sigma_n}
\xrightarrow{d}N(0,1).
\]

**Writing decision.** The outline belongs in the proof and explains the contribution of each supplied lemma. The denominator argument recalls what is being estimated before introducing auxiliary notation. Its expansion has the detail of a graduate homework solution because it supplies the connection that a bare citation to Lemma 2 would hide. Standard tools are applied explicitly without reproving them, and the final paragraph shows how the major steps establish the claim.

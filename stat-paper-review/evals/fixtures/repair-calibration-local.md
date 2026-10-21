# Excerpts from separate manuscripts

These are independent cases. Assess each only from its supplied material; do not combine them into one paper or infer overall scientific quality.

## A. Index in a displayed definition

The setup defines an evaluation sample of size m, indexed by i = 1,...,m. Equation (4) defines its average as m^{-1} sum_{i=1}^n Z_i. The immediately following equality, every subsequent calculation, and the algorithm use m terms with denominator m. The training sample has size n and supplies no Z_i observations. The intended evaluation-sample average is otherwise unambiguous.

## B. Justification for an expectation

The setup gives integrable random variables X and Y, each with mean zero, and explicitly allows dependence. A proof says: "By independence, E(X+Y)=E(X)+E(Y)=0." No other step uses independence or a product expectation. The result needs only this zero expectation.

## C. Calculation within a valid target bound

The stated assumptions are E(A_n^2) <= 1/n and E(B_n^2) <= 1/n; dependence is unrestricted. The lemma claims E[(A_n+B_n)^2] <= 4/n. Its proof incorrectly writes (A_n+B_n)^2 = A_n^2+B_n^2 and concludes a bound of 2/n. Later arguments use only the lemma's stated 4/n bound. There is no stronger constant or independence claim elsewhere.

## D. Practical selection of tuning

The theorem studies each deterministic tuning value in a prescribed range. The implementation selects tuning by cross-validation within that range. The authors explicitly limit the theorem to fixed tuning and make no theoretical guarantee for the selection rule. Numerical studies evaluate the actual cross-validated procedure with matched tuning budgets for competitors; the stated practical conclusions concern these studied settings. The selection rule is reproducible, but robustness to the tuning range and number of folds has not been examined.

## E. Delayed explanation

The main proof invokes conditional centering without explaining it at that point. The referenced appendix supplies the exact conditional-mean identity from the stated assumptions and clearly identifies the held-fixed training data. The relevant proof sketch has no further identified gap. Reading the main proof therefore requires a detour to the appendix.

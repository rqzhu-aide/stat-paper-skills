# Detailed mathematical checking

Use the assigned packet, role brief and relevant [domain checks](domain-risk-checks.md).
Show substantive inferences; routine lines need no separate node.

## Mathematical text and JSON

Use `$...$`/`\(...\)` inline or `$$...$$`/`\[...\]` display.
Preserve raw excerpts; undelimited math stays plain. Serialize Python raw strings to JSON,
which doubles backslashes (`"$\\theta$"`).

For new transcriptions, use already source-established standard notation, e.g. `\bx=\mathbf{x}`.
Do not search macros solely for display or guess `\T`. Unsupported notation stays literal.
Display notes require no audited-target rewrite or re-examination; actual source mismatches
or uncertain meaning still need scientific treatment.

## Establish the source and exact target

Read the complete statement, setup, definitions, proof, continuations, supplement, and relevant macros.
Visually verify consequential PDF symbols, subscripts, powers, signs, inverses, and domains
(PyMuPDF `page.get_pixmap()` can render pages). State inaccessible or ambiguous material before
claiming source fidelity or complete coverage.

Normalize without changing the assertion. Preserve:

- Objects, types, domains, ordered quantifiers, and which quantities are fixed or random.
- Explicit and inherited hypotheses, including numerical caps and conjunctions.
- Probability space, sampling law, conditioning, dependence, and equality notion.
- Exact conclusion parts, normalization, regime, and convergence mode.
- Pointwise or uniform scope and each permitted dependency of hidden constants.

For example, \(\mathbb E|X|^q\le M\) is stronger than finite \(q\)-th moment
when a bound must be uniform in the specified \(M\). Likewise,
\[
\forall\theta\;\exists C_\theta\;\forall n:\quad
|R_n(\theta)|\le C_\theta n^{-1}
\]
does not supply a single constant uniform over \(\theta\).
Keep exact targets separate from overview synopses. Compare saved targets and setup with source;
review notes cannot repair inaccurate assertions.

## Reconstruct inspectable transitions

For
\[
\Gamma,A_1,\ldots,A_m\Longrightarrow C,
\]
examine the decisive written transition using actual inputs, substitutions, scope,
operation, rule, side conditions, and source location. Show its calculation or logical derivation
and outcome in reasoning;
a familiar final formula or “standard algebra” does not justify an invalid transition.

Split where a new premise, operation, event, measure, quantifier, regime, or scope
needs a distinct justification. Expose a useful intermediate bound, equation,
construction, limit, disputed assertion, or reusable claim. Keep routine consecutive
algebra together when the displayed chain makes each transition inspectable.

For example, with \(a,b>0\),
\[
\frac{u}{a}-\frac{v}{b}
=\frac{b(u-v)+v(b-a)}{ab},
\qquad
\left|\frac{u}{a}-\frac{v}{b}\right|
\le\frac{|u-v|}{a}+\frac{|v|\,|b-a|}{ab}.
\]
This explains the bound and exposes the positive-denominator requirements. A later
claim of a uniform constant also needs uniform lower bounds on the denominators
and the stated control of \(v\). Record those requirements at the step that uses them.

Distinguish three questions, even when one response answers all three:

| Examination | Mathematical question |
|---|---|
| Application | Does this supplier give the exact form needed after substitution, under this scope? |
| Derivation | Do the inputs jointly imply this next assertion, with its side conditions? |
| Composition | Does the entire route establish the exact target and every required part, with legitimate scope exit? |

Two valid applications do not imply a valid joint inference. If
\(\Pr(E_i^c)\le\delta\) for \(i=1,2\), then
\[
\Pr(E_1\cap E_2)\ge1-\Pr(E_1^c)-\Pr(E_2^c)\ge1-2\delta.
\]
A claim of \(1-\delta\) requires a different allocation or further reasoning.
Record the correct applications separately from the defective combination.

## Premises, definitions, and witnesses

A theorem's asserted conclusion is not its own premise. Use its hypotheses,
meaning-determining definitions, authorized setup, or actually available earlier
results. Ordinary algebraic and logical rules belong in the justification; a
nontrivial theorem used as a rule still needs source verification and applicability.

Definitions introduce notation, not unproved mathematical properties. Defining
\(\hat\theta\in\arg\min_{\theta\in\Theta}f(\theta)\) does not establish nonempty
argmin, uniqueness, or measurability. If a later step needs one of these properties,
give it an obligation or identify an authorized assumption that supplies it.
For example, \(\inf_{x>0}x=0\) has no minimizer in its stated domain.

Respect witness dependence. From \(\forall x\,\exists y:P(x,y)\), a witness
may depend on \(x\); the statement does not imply \(\exists y\,\forall x:P(x,y)\).
Track which earlier variables a witness may depend on and whether it can be
chosen measurably or independently of later randomness when those properties
are used. Fixing a sample-dependent optimizer after a fixed-parameter probability
bound requires further justification.

Check variable freshness for universal introduction and capture-free substitution.
An arbitrary \(x\) must remain arbitrary when generalized. An existential witness
cannot escape into the conclusion or another open assumption where the elimination
rule forbids it.

## Local scope, cases, and induction

Keep a temporary hypothesis attached to its branch. Under \(x\ge0\), the claim
\(x=|x|\) is available; it is not thereby available for \(x<0\) or unconditionally.
At a use, check the supplier's hypotheses, substitutions, and the actual implication
between its scope and the consumer's scope. A kind such as assumption or an
owner relationship cannot authorize the transfer.

For a proof of \(A\Rightarrow B\), retain the local assumption \(A\) until the
implication-introduction step discharges it. For contradiction, use the exact
negation of the target and identify the contradiction actually reached.
Do not add a needed restriction only to free-text check conditions and then claim
the original unconditional target.

Exhaustive cases require all branches under their respective assumptions and an
argument that the branches cover the target domain. Do not conjoin incompatible
branch assumptions into a global premise. Alternative proofs are different:
one complete admissible route can establish a statement while another remains
defective and reportable.

For induction, check the domain and well-founded order, the base cases, the
quantified conditional step, and the induction rule assembling the result.
The induction hypothesis is not an unconditional fact. A cycle of dependencies
without an independent foundation supplies no proof.

## Constants, rates, probability, and limits

Recompute the algebra and asymptotic comparison under the exact regime. Identify
constants depending on dimension, distribution, confidence, or tuning parameters.
If a theorem lets \(p=p_n\) grow, a fixed-\(p\) bound does not automatically remain
valid. Divide by a vanishing normalization only with a corresponding bound on
the numerator and an admissible nonzero denominator.

Distinguish exact, almost-sure, distributional, and asymptotic equality.
In particular, \(O_p(1)\) does not mean \(o_p(1)\), and pointwise convergence
does not give uniform convergence. State the norm and convergence mode at the
step that changes them.

Track accumulated probability losses and the actual events on which all inputs
hold together. Check conditioning, independence, filtration, random indexing,
and data-dependent choices. When exchanging limits, integrals, expectations,
derivatives, suprema, or infima, name the applicable justification and verify
its needed regularity in this problem.

## Origins, completion, and repairs

Distinguish the written argument, reconstruction of routine details, and proposed
repairs. Do not silently substitute corrected expressions for printed ones. A borrowed
internal bound can survive a false owner theorem; examine its own inputs.

Complete the route backward from its final target, checking conjunctions, cases,
quantifiers, and discharged scopes. Separately inspect all in-scope written material,
including unused defective routes. Do not call the audit complete just because
one route establishes the target or every registered excerpt has coverage.

Use [evidence-and-verdicts.md](evidence-and-verdicts.md) for outcome and
counterexample standards. Preserve defects when supplying a repair. A new route
for the unchanged statement has its own provenance; a restricted statement has
its own target. A candidate repair remains provisional until the claimed
mathematics and required independent review are completed.

Optional: [multi-step probability authoring example](probability-example.md).

# Observations from the Supplied Proofs

These notes study exposition in selected complete proofs, not the correctness of the papers or the authorship of any passage. Page numbers refer to the supplied PDF versions; printed and PDF page numbers agree at the cited locations. The three examples support different levels of density. None supplies a universal template or a numerical equation-to-text target.

## Nie and Wager: make the statistical reasoning explicit

Source: [Quasi-Oracle Estimation of Heterogeneous Treatment Effects](../examples/1712.04912v4.pdf), August 2020 draft.

Read for these notes: Lemmas 5, 6, 8, and 2. Representative rendered pages inspected: 29, 30, 35, and 36.

| Location | Observed choice | How to use it |
|---|---|---|
| Lemma 6, p. 30, (32) and the following calculation | A multistep comparison precedes a separate triangle-inequality calculation. The text identifies which transition uses (32). | Show the intermediate comparison that makes the next inequality possible. Place the reason next to its use. |
| Lemma 8, p. 36, calculation preceding (39) | Conditional centering is shown through successive expectations, measurable-factor extraction, and the residual mean-zero property. Conditional independence is then explained in prose. | Replace an unsupported appeal to cross-fitting with the actual conditional calculation. |
| Lemma 5, pp. 28-29, (28)-(31) | The proof identifies the process, conditional setting, metric, and increment condition needed for generic chaining. It later states the remaining moment bound. | Explain how a named tool fits this problem and mark the transition to the remaining task. |
| Lemma 8, pp. 34-35 | The feasible loss is expanded and cancellations are exposed before five summands are named and treated separately. | Let a decomposition motivate the organization. Name terms when different arguments or later references make the names useful. |
| Lemma 8, p. 35 | After Cauchy-Schwarz, the text interprets the factors as estimation errors, supplies their rates, and explains the deterministic part of the bound. | Connect a formula to its statistical role and distinguish deterministic control from stochastic order. |
| Lemma 8, p. 37, after (40) | The proof explicitly moves from fixed tuning values to simultaneous control. | Explain a change in quantification; do not treat it as a stylistic substitution. |
| Lemma 2, pp. 39-42, including (43)-(44) | The proof identifies the target linear form of the regret bound and displays supporting concavity calculations. | Explain the purpose of a technical calculation before carrying it out. |

**Overall impression.** The proof feels directed because its prose identifies the term under study, what has been established, and what still has to be bounded. It can devote most of a page to equations without losing this direction. Its statistical explanations are particularly useful models for nuisance estimation and conditional arguments.

**Do not imitate indiscriminately.** Lemma 2, p. 40, attributes a consequential rate simplification to a few lines of algebra and a condition on exponents. For a detailed proof, writing out that comparison would be an improvement. Lemma 8, p. 39, dismisses certain terms as lower order; a non-obvious comparison should be shown. Dense layers of indexed terms and occasional loose wording are not style goals.

## Agterberg and Zhang: expose reductions and theorem applications

Source: *Estimating Higher-Order Mixed Memberships via the \(\ell_{2,\infty}\) Tensor Perturbation Bound*, February 2024 version ([PDF](../examples/2212.08642v3.pdf)).

Read for these notes: Section 4, Lemma 4, Theorem 1, Corollary 1, and Lemma 17. Representative rendered pages inspected: 69, 70, and 72.

| Location | Observed choice | How to use it |
|---|---|---|
| Section 4, pp. 13-15 | The proof overview explains dependence between noise and estimated subspaces, why a direct concentration argument fails, and what the modified leave-one-out construction supplies. | Explain a major construction through the obstacle it removes, rather than merely naming the technique. |
| Lemma 4, pp. 24-26, (6)-(9) | A rowwise reduction yields two named terms. Successive additions and subtractions expose the leave-one-out comparison. Bounds are then substituted back into the original decomposition. | Display the algebra that creates the tractable terms and close the local argument by recombining them. |
| Lemma 4, p. 26, after (9) | The projection identity used at the end of a chain is explained immediately afterward. | Keep a consequential reason near its mathematical step. |
| Theorem 1, pp. 69-70 | The proof maps its objects to an imported theorem, introduces the required tolerance, bounds the relevant quantities, and reduces the applicability condition to the paper's assumptions. | A substantive theorem application needs a recognizable correspondence and the material condition checks. |
| Theorem 1, pp. 70-71 | A long displayed bound is followed by a return to the original theorem's parameterization and remaining conditions. | An intermediate rate is not the endpoint until its connection to the stated result is visible. |
| Lemma 17, pp. 71-72 | Fixed-row control is developed from independent summands and concentration inputs; a union bound then yields simultaneous rowwise control. | Write out the passage from an individual bound to the required uniform bound. |
| Corollary 1, p. 71 | A short norm comparison and averaging argument prove the claim without a roadmap. | Let a genuinely short proof remain short. |

**Overall impression.** The useful feature is that the reductions and applicability checks are visible. The paper often spends equations on exactly the operations that a compressed proof might conceal behind a theorem name or the phrase "leave-one-out argument."

**Do not imitate indiscriminately.** The large chain on p. 70 provides useful algebra but can require substantial effort to navigate. In a new proof, preserve meaningful steps while splitting at changes of purpose, such as inverse control, decomposition, and substitution of rates. Repeated stock transitions and awkward phrasing need not be retained. Dense tensor notation is appropriate to the subject, not an instruction to introduce comparable notation elsewhere.

## Li, Zhou, Wei, and Chen: carry a calculation back to its target

Source: [Faster Diffusion Models via Higher-Order Approximation](../examples/2506.24042v2.pdf), August 2025 revision.

Read for these notes: Section 5.3 and Lemmas 1, 3, 4, 6, 9, and 10. Representative rendered pages inspected: 26, 28, and 29.

| Location | Observed choice | How to use it |
|---|---|---|
| Section 5.3, pp. 11-15, especially (43) | The main argument is organized around density ratios, a total-variation decomposition, bounds for its two terms, and final assembly. | Use headings and term labels that correspond to real mathematical tasks. |
| Lemma 6, pp. 29-30, (88)-(89) | A square is expanded, an exponential is factored, an integral becomes a conditional expectation, and a tail calculation proceeds through changes of variables and completion of the square. | Show the mathematical transformations that create the final bound, rather than naming them without calculation. |
| Lemma 6, p. 29, explanation after (89) | The elementary inequality used to collect terms into an exponential bound is stated locally. | Explain a less visible simplification beside the display. |
| Lemma 4, pp. 27-28, (83)-(87) and the closing calculation | A local supremum is defined, trace and Jacobian bounds lead to a density comparison, and an absorption argument returns to the desired bound. | Make the purpose of auxiliary notation visible and finish by returning to the original target. |
| Lemma 10, p. 38, (114)-(119) | An event implication is established before a previously derived density-ratio relation is used. | Show that the current argument satisfies the conditions of the result being invoked. |
| Lemma 9, pp. 37-38, (113) | The proof chooses the first crossing index and identifies the exact numerical assumption contradicted at the end. | A contradiction proof should specify both the assumed failure and the incompatible conclusion. |

**Overall impression.** The paper is often equation-heavy, but its useful passages preserve a chain of mathematical purposes. Prose announces a reduction or explains a connection; calculations carry the actual transformations. Auxiliary notation simplifies a local task and is translated back when that task is complete.

**Do not imitate indiscriminately.** The crowded chain on p. 29 could use a clearer break between the tail-integral argument and completion of the square. Several proofs defer work to related arguments in prior papers, including Lemma 3's treatment of (28) on p. 27 and Lemma 11 on p. 39. A requested detailed proof should make the correspondence and relevant conditions explicit, or supply the derivation when appropriate. Repeated ceremonial transitions and draft imperfections are not useful models.

## What the examples establish together

The transferable lesson is the division of work between prose and formulas:

- Prose identifies the mathematical goal, the reason for a construction, the scope of a bound, or the consequence of a calculation.
- Displays expose the transformations that would otherwise have to be reconstructed.
- Detail increases at substantive transitions and decreases for immediate or genuinely repeated steps.
- Local conclusions reconnect component calculations to the claim being proved.

These observations support the writing guidance, not a claim that all human proofs follow the same form. In particular, they do not justify a phrase blacklist, a fixed number of steps, a fixed ratio of prose to equations, or copying omissions from a published or circulated paper.

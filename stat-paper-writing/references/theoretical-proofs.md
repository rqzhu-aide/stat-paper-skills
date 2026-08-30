# Proof Presentation Guidance

## Job of the section

Make the supplied proof exposition navigable and document how the manuscript says the result follows, where assumptions enter, and how named intermediate statements depend on one another.

This is a presentation-only review. Preserve hypotheses, quantifiers, domains, conclusions, equations, proof steps, stochastic orders, and logical direction. Do not certify validity, completeness, or correctness. Do not add a missing mathematical justification. If clearer exposition would require changing mathematical content, identify the exact conflict and leave it for author judgment.

## Start with a declared dependency map

For a proof section or appendix, record:

| Result | Stated direct dependencies | Stated main device | Assumptions cited |
|---|---|---|---|

Use only dependencies stated in the manuscript or unambiguous from its labels and cross-references. Do not infer a missing dependency from subject-matter expectations.

Order proofs by main-text theorem order unless a shared technical foundation makes the declared dependency order clearer.

## Proof roadmap

Begin a substantial proof with the manuscript's stated:

1. central decomposition, coupling, reduction, or contradiction;
2. intermediate claims;
3. points at which named assumptions enter;
4. step described as the main difficulty.

The roadmap should explain strategy without asserting that the argument is valid or repeating the theorem.

## Proof body

Give each block a clear declared purpose, such as:

- establish an identification or orthogonality statement;
- control a bias or remainder;
- state a regularity or measurability condition;
- derive a concentration statement or stochastic order;
- transfer a stated oracle result to a feasible estimator;
- invoke a named limit theorem;
- construct a counterexample or lower bound.

Keep notation local. State conditioning and randomness explicitly when they are already determined by the manuscript. When the proof exchanges limits, expectations, derivatives, or integrals, name the justification if the manuscript supplies one. If it does not, flag the missing exposition as **Unverified dependency** rather than supplying a theorem or argument.

Remove rhetorical shortcuts such as "clearly," "obviously," or "it is easy to see" when they replace explanation. Do not compensate by inventing a derivation.

Do not decide whether a proof-ending claim such as "this proves the theorem" or "this completes the proof" is mathematically warranted. Preserve the mathematical force and attributed status of supplied proof-ending language; make only presentation edits that do not require a completeness judgment. Do not add a new proof-completion claim or a standardized replacement. If the user asks whether the proof is correct or complete, direct them to invoke `$stat-paper-proofcheck` explicitly; do not start that audit implicitly.

## Lemmas

Place a lemma near its first declared use when it is local. Group lemmas only when several proofs visibly cite them. Do not promote routine algebra to a formal result merely for presentation.

Keep method assumptions distinct from conditions introduced only in a lemma. Preserve their labels and stated scopes.

## Main text versus appendix

Keep in the main text:

- the proof idea needed to understand the method;
- the stated main decomposition or geometric argument;
- the described role of central assumptions;
- a boundary example when it changes interpretation.

Move routine algebra, repeated bounds, technical concentration details, and auxiliary lemmas to the appendix when the dependency chain and cross-references remain clear. See [appendix-architecture.md](appendix-architecture.md).

## Presentation checklist

- Can the stated proof strategy be summarized in two or three sentences?
- Does every named intermediate result have a visible reference and declared role?
- Are assumption labels and described roles consistent across the theorem, roadmap, and proof?
- Are probability spaces, conditioning, and convergence terms introduced consistently?
- Does the final paragraph refer to the same written conclusion, rate, and scope as the theorem statement?
- Has any heuristic or intuition been presented as a formal implication?
- Is the main text sufficient to understand why the manuscript says the theorem supports the method?
- Does the output avoid any judgment about proof validity?

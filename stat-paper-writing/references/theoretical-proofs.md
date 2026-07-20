# Theoretical Proof Guidance

## Job of the section

Make the logical mechanism verifiable. A proof should show why the result follows, where assumptions enter, and how intermediate claims depend on one another.

Separate exposition review from correctness verification. Do not report a proof as verified unless every nontrivial step, dependency, and assumption use has been checked.

## Start with a dependency map

For a proof section or appendix, record:

| Result | Direct dependencies | Main device | Assumptions used |
|---|---|---|---|

Order proofs by main-text theorem order unless a shared technical foundation makes dependency order clearer.

## Proof roadmap

Begin a substantial proof with:

1. the central decomposition, coupling, reduction, or contradiction;
2. the intermediate claims required;
3. the point at which the main assumptions enter;
4. the step containing the main difficulty.

This roadmap should explain strategy, not repeat the theorem.

## Proof body

Give each block a mathematical purpose, such as:

- establish identification or orthogonality;
- control a bias or remainder;
- verify a regularity or measurability condition;
- derive concentration or a stochastic order;
- transfer an oracle result to a feasible estimator;
- apply a limit theorem;
- construct a counterexample or lower bound.

Keep notation local. State conditioning and randomness explicitly. When exchanging limits, expectations, derivatives, or integrals, name the justification when it is not immediate.

## Lemmas

Place a lemma near its first use when it is local. Group lemmas only when several proofs reuse them. Do not promote routine algebra to a formal result.

Separate method assumptions from conditions introduced only to prove a lemma.

## Main text versus appendix

Keep in the main text:

- the proof idea needed to understand the method;
- the main decomposition or geometric argument;
- the role of central assumptions;
- a boundary example when it changes interpretation.

Move routine algebra, repeated bounds, technical concentration, and auxiliary lemmas to the appendix. See [appendix-architecture.md](appendix-architecture.md) for the full supplement structure.

## If a presentation mode is needed

- **Compact and direct:** Use a short roadmap, combine routine steps, and retain all nontrivial justifications.
- **Explanatory and intuition-led:** Expose the invariant, decomposition, geometry, coupling, or conditioning argument in a stripped but nondegenerate regime before the general derivation. Do not remove the interaction that makes the proof difficult.
- **Formal and structure-led:** Expose dependencies, scopes, constants, conditioning, and assumption use step by step.
- **Evidence-led and comparative:** Use only when the proof explains a testable mechanism or comparison; connect the proved term to the later empirical diagnostic without inserting results into the proof.

## Review checklist

- Can the proof strategy be stated in two or three sentences?
- Does every intermediate result have a dependency role?
- Are all assumptions used where claimed?
- Are probability spaces, conditioning, and convergence operations clear?
- Does the final step match the theorem statement exactly?
- Has any unproved intuition been presented as a formal implication?
- Is the main text sufficient to understand why the theorem supports the method?

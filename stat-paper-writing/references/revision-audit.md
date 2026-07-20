# Full-Manuscript Revision Audit

## Contents

- [Audit depth and evidence](#audit-depth-and-evidence)
- [Argument and routing](#1-reconstruct-the-argument)
- [Reader, notation, and wording audit](#3-perform-a-reader-walkthrough)
- [Paragraphs, formulas, and formal results](#5-audit-paragraph-architecture)
- [Evidence and contribution claims](#8-audit-numerical-evidence)
- [Main text, supplement, and final checks](#10-audit-main-text-and-supplement-together)
- [Review output](#review-output)

## Audit depth and evidence

Choose the smallest audit that can answer the request:

- **Quick audit:** inspect a local passage and enough surrounding context to avoid changing its meaning. Do not infer paper-level defects from the excerpt alone.
- **Section audit:** inspect the section's intellectual job, internal argument, notation, support, and transition to adjacent sections.
- **Full audit:** reconstruct the paper-level claim chain and inspect all affected sections, appendices, references, and rendered outputs.

For every substantive finding, distinguish:

- **Observed:** directly visible in the manuscript;
- **Inferred:** a reader consequence supported by the manuscript;
- **Unverified:** dependent on a proof check, citation search, code inspection, numerical recomputation, or author knowledge.

Do not present an unverified concern as an established error.

### Reference-loading order

For a full audit, first use this file with [argument-architecture.md](argument-architecture.md) to identify paper-level failures. Do not preload every section guide. Open a section guide only when the first pass identifies a consequential problem in that section. Load [style-modes.md](style-modes.md) only when the repair requires a real choice about information order or explanatory depth. Load prose references only when language is in scope.

## 1. Reconstruct the argument

Without relying on headings, write down:

- the statistical target;
- the gap;
- the core representation or identity;
- the proposed estimator;
- the main theorem chain;
- the numerical claims;
- the principal limitation.

If these cannot be stated simply, repair the paper-level argument before sentence editing.

## 2. Audit section and presentation-mode routing

Identify which sections need revision. Check a section against its section-specific guide only after the paper-level pass shows that the section has a consequential failure. When presentation strategy is part of that failure, read [style-modes.md](style-modes.md) and verify that:

- every section has a clear reader-facing job;
- its organization fits that job rather than following a paper-wide template mechanically;
- its primary presentation mode suits the current draft, audience, topic familiarity, technical depth, venue, and available evidence;
- a secondary mode is used only for a local need, such as adding mechanism-level intuition before a formal statement;
- different sections may use different modes when their jobs differ;
- the selected mode clarifies the contribution rather than imitating an author or paper;
- theory and numerical evidence fulfill promises made earlier in the manuscript;
- important boundaries appear when the corresponding claim is made, not only in the discussion.

If the correct repair is already clear, skip mode comparison. If two modes remain genuinely plausible, rewrite one representative passage in each and retain the version that improves comprehension without weakening precision, evidence, or logical continuity.

## 3. Perform a reader walkthrough

Read from the start and mark every point where the reader must ask:

- Why is this object being introduced?
- Is this local to one query or global over the sample?
- Is this exact or a plug-in approximation?
- What data, randomness, and conditioning are in scope?
- Does this construction use information it claims to withhold or exclude?
- Does this theorem concern the implemented estimator?
- What should I learn from this figure?

Add the missing preflight explanation at the earliest point of confusion.

## 4. Audit terminology, notation, and register

Create a ledger with columns:

| Object | Canonical term | Symbol | First definition | Variants to remove |
|---|---|---|---|---|

Check subscripts, superscripts, conditioning sets, transpose notation, expectations, probability symbols, and dimensions. Verify every symbol is introduced before use and that nearby objects have visibly different notation.

Use common field terminology unless the paper is intentionally defining a new concept. Keep the number of new terms small.

When prose is in scope, apply [wording-register.md](wording-register.md). Name each object by its statistical, mathematical, or domain-science role. Treat software-manual vocabulary as a context-sensitive warning sign, preserve it only for literal implementation objects, and avoid blind global substitutions.

After editing, search the title, abstract, main text, algorithms, captions, tables, appendices, and supplement for inconsistent variants. Verify that the revisions preserve distinctions among population, oracle, feasible, empirical, and numerical objects.

## 5. Audit paragraph architecture

For each paragraph, identify its controlling question. Combine adjacent short paragraphs that form one argument. Split a paragraph only when the controlling question changes.

When section-level architecture remains unclear, label each paragraph by its main function: `need`, `gap`, `route`, `construction`, `mechanism`, `evidence`, `interpretation`, or `boundary`. Use the labels only as a diagnostic. Flag long runs of one function, especially construction without mechanism, introduction material without a route, or evidence without interpretation.

Flag label-first openings such as:

- "Remark on ..."
- "Definition of ..."
- "Let ..." without a preceding purpose;
- "We now turn to ..." without an intellectual transition.

Do not impose a fixed sentence or paragraph length. Statistical reasoning often requires a longer integrated paragraph.

## 6. Audit formulas and methods

For every displayed equation, record its job: definition, identity, estimator, decomposition, bound, or computational rule. Remove decorative displays and number only equations referenced later.

Check that normalizations have correct dimensions and interpretation. Distinguish mathematical necessity from implementation convenience. Where used, verify that sample splitting, exclusions, conditioning, or cross-fitting block the dependence paths they claim to block.

## 7. Audit formal results

For each theorem, proposition, corollary, or lemma, record:

- question answered;
- assumptions and their roles;
- exact conclusion;
- relation to prior literature;
- method component justified;
- limitation;
- proof location.

Demote results that are only algebraic observations. Move technical intermediate results to the supplement. Tighten theorem statements that mix the main claim with implementation details.

## 8. Audit numerical evidence

Map every central claim to a table, figure, theorem, or citation. Verify simulation truth, competitors, tuning, replication counts, uncertainty, and computational timing. Check whether results distinguish finite-computation noise from structural error.

Inspect rendered figures at publication size. Confirm common scales, readable legends, informative captions, and no unsupported graphical inference.

## 9. Audit citations and contribution claims

Check that citations remain attached to the claims they are intended to support and that contribution language agrees with the manuscript and any author-supplied sources. Flag definitions, decompositions, proof devices, algorithms, or novelty statements that require external source verification. Do not perform or imply a publication-backed novelty search within this author-side writing audit.

## 10. Audit main text and supplement together

The main text should contain the motivation, central objects, formal conclusions, and enough interpretation to stand alone. The supplement should contain proof detail, implementation detail, exhaustive settings, and secondary results.

Build a claim-to-support map using [appendix-architecture.md](appendix-architecture.md). Verify that every omitted dependency is cross-referenced and every appendix item supports a claim, a later dependency, or a labeled extension.

Remove duplicated narratives, orphan appendix items, and inconsistent notation across the files.

## 11. Final technical check

When editable source and a suitable toolchain are available, compile or render the manuscript and supplement. Check undefined references, missing citations, equation layout and punctuation, figure and table placement, and hyperlink behavior. Inspect affected rendered pages rather than relying only on a build log. For other formats, use the closest available structural and visual checks and state any validation limit.

If prose was rewritten, compare the source and revision for changes to negation, quantifiers, conditioning, convergence mode, uncertainty, scope, numerical values, citations, cross-references, and claim strength. Use [polishing-protocol.md](polishing-protocol.md).

## Review output

When reporting an audit, prioritize a small number of consequential issues:

1. validity or target mismatch;
2. contribution and argument;
3. method and theorem exposition;
4. numerical support;
5. notation and prose.

For each issue, explain why it matters to the reader and give a concrete revision direction. Avoid an exhaustive list of minor stylistic preferences.

Use this finding structure for Critical and Major issues:

| Field | Content |
|---|---|
| Priority | Critical, Major, Moderate, or Minor |
| Location | Section, paragraph, theorem, equation, figure, or manuscript-wide |
| Evidence | Exact manuscript fact or recurring pattern |
| Consequence | Effect on validity, argument, interpretation, or navigation |
| Revision direction | Specific action rather than a general aspiration |
| Remedy type | Safe prose edit, author decision, verification, reanalysis, new theory, or new evidence |

Do not force this table for a short local audit. Preserve the same information in compact prose.

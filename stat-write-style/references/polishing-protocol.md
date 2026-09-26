# Claim-Preserving Prose Polishing

## Scope and meaning

Distinguish light polish, substantive paragraph development, and section restructuring. Work within scope, check privately, and apply supported edits directly; ordinary polishing needs no audit report.

Before rewriting, identify the passage's job, claim, mathematical objects, evidence level, and boundary. Protect:

- mathematical expressions, symbols, indices, macros, labels, and cross-references;
- negation, logical direction, quantifiers, conditioning, and sources of randomness;
- finite-sample, asymptotic, oracle, feasible, empirical, and computational scope;
- uncertainty, modality, causal status, and novelty claims;
- numerical values, units, and citations.

Preserve scientific content while changing authorized explanation order, headings, and sentence subjects. Inspect affected scientific dependencies. Mathematical presentation follows the prose core; notation normalization requires authorization.

For conflicts, uncertain equivalence, missing support, or substantive corrections, use [support-and-author-decisions.md](support-and-author-decisions.md). Continue supported edits elsewhere; do not hide scientific changes inside a polish.

## Revise at the needed scale

Paper-level work follows [manuscript-workflow.md](manuscript-workflow.md). Local edits use relevant checks without a fixed sequence of separate passes.

## Prose core for drafting and revision

For drafting, read this subsection; revision-specific checks elsewhere in this guide are unnecessary.

**Sentence and cohesion.** Unpack stacked nouns into relations among named objects. Keep subjects near verbs and antecedents unambiguous. Build on preceding sentences with appropriate emphasis. Use stable terms for distinct statistical objects and substantive transitions between topics.

**Paragraph development.** Develop one question, claim, or obstacle through the explanation, comparison, and mathematical detail it needs. Combine fragments doing the same intellectual work; split at a change of purpose. A paragraph can contain a display and continue afterward. Watch for chains of tiny lead-ins, displays, and isolated follow-ups: integrate the thought instead of adding padding. Sustained comparisons may need space; transitions may be brief. Use no length quota or repeated paragraph skeleton. Remove repeated openings and summaries without erasing qualifications.

**Mathematical prominence.** Keep routine notation, short conditions, substitutions, and incidental identities inline when readable. Display central definitions and results, expressions needing visual comparison, or mathematics that would obstruct a sentence; a short central equation can deserve a display. Integrate displays grammatically and explain their role without paraphrasing every symbol. An isolated "Define," "Thus," or "where" may signal fragmentation, not a forbidden word.

**Presentation and preservation.** Within the requested scope, change paragraph breaks, display delimiters, environments, and surrounding prose while preserving mathematical expressions, conditions, scope, protected macros, labels, and reference targets. Respect explicit formatting constraints. Retain referenced displays when they serve navigation or emphasis, and preserve venue numbering requirements. Do not silently drop labels to move a formula inline or normalize mathematical tokens without authorization.

**Attribution and economy.** Credit inherited ideas at substantive use; explain their relationship to the present argument where consequential. Use supported comparisons, not a citation quota. Remove language that changes neither meaning nor navigation. Preserve authorial voice and clear sentences; use [wording-register.md](wording-register.md) for specialist terminology, evidence verbs, or register choices.

## Statistical prose mechanics

**Definitions.** Explain why an object is needed and keep its mathematical type clear. A definition does not itself imply existence, uniqueness, identification, or estimability.

**Assumptions.** Preserve who assumes what, under which law or regime, and for which result. Explain the supplied restriction instead of relying on unsupported descriptions such as mild or standard. Do not add an editor-proposed assumption to make the prose work.

**Evidence level.** Preserve the manuscript's attributed status: a proved result under stated assumptions, a numerical result in reported settings, an empirical pattern that suggests a conclusion, or an unproved mechanism that motivates it. A theorem environment or attached proof does not justify changing states or claims to proves or establishes. Likewise, preserve qualifications such as may, can, typically, and under Assumption 2 unless a supported substantive correction is authorized.

For proof prose, including a local polish, use [theoretical-proofs.md](theoretical-proofs.md) for the proof-ending boundary. This is exposition work, not a proof-completeness judgment.

**Comparisons.** Name the metric, comparison basis, information available, and scope. Replace outperforms with the reported advantage when it is not uniform across settings or criteria.

**Limitations.** Place a restriction beside the claim it qualifies. Repeat it when a distant passage could otherwise mislead, using a short reference where sufficient. Consolidate caveats without making a headline unconditional or concealing a theory-to-implementation gap.

## Compare and deliver

Compare source and revision for protected content, including symbol relationships, conditioning, convergence modes, constants, and theorem references. Check that prose matches the displayed relation, citation support still matches its clause, values and units agree, and terminology remains consistent across affected captions, algorithms, and supplements. Propagate any authorized notation change consistently.

Watch particularly for changes from some to all, pointwise to uniform, association to effect, oracle to feasible, approximate to exact, observed to established, can to guarantees, or one setting to general settings. These are changes of scientific force, not stylistic alternatives.

Deliver local edits directly. For longer revisions, summarize principal changes, validation, unresolved input, and substantive corrections. Keep a reviewable diff, not an exhaustive style log. Consult [polishing-examples.md](polishing-examples.md) for difficult choices; routine edits need no examples file.

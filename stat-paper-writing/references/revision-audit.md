# Full-Manuscript Writing and Presentation Audit

## Contents

- [Audit depth and evidence](#audit-depth-and-evidence)
- [Default inspection order](#default-inspection-order)
- [Neutral orientation](#1-read-once-without-judging)
- [Fine-to-section shared protocol](#passes-2-through-5-fine-to-section-protocol)
- [Cross-section and paper-level checks](#6-audit-cross-section-contracts)
- [Revision and closure](#10-revise-and-run-the-closure-loop)
- [Audit output](#audit-output)

## Audit depth and evidence

Choose the smallest audit that can answer the request:

- **Quick audit:** inspect the requested passage and enough context to preserve meaning. Do not infer paper-level defects from the excerpt alone.
- **Section audit:** inspect the requested section and the dependencies needed to understand it.
- **Full audit:** inspect the complete supplied manuscript using the default order below.

Honor an explicit user request for a different focus or order. A focused request may skip unrelated passes, but begin with enough neutral reading to understand the requested scope. For an explicit paper-level focus, move after orientation only through the requested coarse passes. Do not add intermediate passes unless one is indispensable to answer the request, and state that dependency if it is used.

Treat "focus only" or an instruction to ignore other checks as a strict scope contract. For contribution-and-narrative-only work, use `orientation -> contribution ledger when useful -> narrative`. Use the supplied scope directly and do not perform or report separate atomic, local, section, or cross-section passes.

Use [support-and-author-decisions.md](support-and-author-decisions.md) when supplied support, artifact authority, or an author choice becomes consequential. Use [reporting-and-validation.md](reporting-and-validation.md) when classifying and reporting findings.

## Default inspection order

For a full or unspecified audit, use this order:

| Pass | Granularity | Primary task |
|---|---|---|
| 1 | Orientation only | Read the whole supplied scope without judging or editing |
| 2 | Atomic | Check identifiers, symbols, direct references, numbers, and exact scope wording |
| 3 | Formal and evidentiary contracts | Check directly paired formulas, statements, algorithms, claims, citations, and support |
| 4 | Local | Check sentences, displays, terminology, paragraphs, and local transitions |
| 5 | Section | Check section jobs, internal dependency order, and adjacent transitions |
| 6 | Cross-section | Check objects, claims, evidence, discussion, and supplement agreements |
| 7 | Contribution map | Build the ledger when hierarchy or support is unclear |
| 8 | Reader walkthrough | Diagnose sequential reader-facing confusion |
| 9 | Paper | Judge the narrative spine, contribution hierarchy, section order, and boundary |
| 10 | Closure | After authorized edits, recheck the affected scope and render or compile |

Do not let a dramatic paper-level first impression reorder the default passes. Fine-grained documentary findings provide the evidence base for later interpretive judgments. Reporting priority need not follow inspection order.

### Reference-loading order

Start with this file. Load no repair-specific reference during the neutral orientation pass.

During Passes 2 and 3, use the manuscript and direct artifacts first. Load a specialized reference only when a consequential issue needs its rules. Load prose references in Pass 4, section guides in Pass 5 when needed for coverage or repair, and [appendix-architecture.md](appendix-architecture.md) in Pass 6 when main-text and supplement coordination is in scope.

In the default full audit, load [argument-architecture.md](argument-architecture.md) only after cross-section evidence has been gathered, for Passes 7 and 9. For an explicit planning, restructuring, contribution, or paper-level focus, load it after the neutral orientation and use the supplied scope directly. Do not require a separately named cross-section pass merely to populate the ledger. Use [style-modes.md](style-modes.md) only when a later repair requires a genuine choice about information order or explanatory depth.

## 1. Read once without judging

Read all supplied main text, appendices or supplement, captions, tables, references, rendered pages, and figure or table images once from beginning to end. Record only a private descriptive map:

- topic and stated statistical or scientific target;
- named population, oracle, feasible, empirical, and computational objects;
- declared formal claims and where they appear;
- supplied numerical or empirical evidence and where it appears;
- section and supplement roles;
- author-stated limitations and boundaries.

Use the manuscript's own terms. Do not mark errors, diagnose reader difficulty, rank contributions, select a preferred narrative, decide coherence, load repair guidance, or edit. This pass is for understanding only.

Store this orientation as one compact source-anchored manuscript map and reuse it across later passes. Treat the passes as logical checkpoints in one working context, not as separate required agents or model calls. Reopen source only for exact evidence, a consequential cross-check, lost context, or post-edit closure.

## Passes 2 through 5: fine-to-section protocol

For the default full audit, after neutral orientation load [quick-section-audit.md](quick-section-audit.md) and apply its atomic, formal-object, local, and section passes across the complete supplied scope. Reuse the full-manuscript orientation map rather than repeating its bounded orientation.

For an explicit focused plan, load that shared protocol only when one of its passes is selected or is an indispensable stated dependency. Do not insert its other passes into a coarse focus-only audit.

## 6. Audit cross-section contracts

After the fine, local, and section passes, compare across the manuscript:

- introduction promises against methods, formal statements, reported evidence, and discussion;
- canonical terminology, notation, objects, assumption labels, scopes, and boundaries across sections;
- method descriptions against the formal object and numerical implementation they name;
- contribution claims against formal, empirical, and citation support;
- discussion and conclusion language against earlier scopes and limitations;
- main-text claims against appendix or supplement support and cross-references.

The main text should contain the motivation, central objects, formal conclusions, primary evidence, and main boundary needed to stand alone. Use [appendix-architecture.md](appendix-architecture.md) to map omitted detail to support, remove orphan material, and check both directions of cross-reference.

## 7. Build the contribution-to-support ledger when needed

If several contributions compete or their hierarchy or support remains unclear after Pass 6, load [argument-architecture.md](argument-architecture.md) and build its six-column ledger.

Follow [argument-architecture.md](argument-architecture.md) for contribution identity, hierarchy, support cells, author decisions, and the exact ledger. The ledger organizes evidence already gathered; it does not establish proof validity, empirical correctness, novelty, or a preferred rank. CONTRIBUTION_LEDGER remains evaluative rather than a second orientation.

## 8. Perform the evaluative reader walkthrough

Reread sequentially and mark where a reader must ask:

- Why is this object being introduced?
- Is this local or global?
- Is this population, oracle, feasible, empirical, or numerical?
- Is this exact, estimated, or plug-in?
- Is the claim finite-sample, asymptotic, conditional, pointwise, uniform, or computational?
- What information, randomness, and conditioning are in scope?
- Has any observation or fitted object been withheld, reused, or cross-fitted, and is that role stated?
- What does this result or display contribute to the method?
- What should be learned from this figure?
- Where does the claim stop?

This is an evaluative pass, unlike the neutral first read. Ground every finding in evidence from the earlier passes. Add a missing explanation only when the manuscript supplies it; otherwise flag the missing input.

## 9. Audit whole-paper narrative and argument architecture

Only now evaluate the coarsest questions:

Reconstruct the supplied chain `target -> gap -> central route -> method object -> declared theorem chain -> primary evidence -> main boundary`. Identify the earliest missing or conflicting link before proposing a paper-level repair.

- Can the paper's target, stated gap, central route, method object, declared theorem chain, primary evidence, and main boundary be stated coherently?
- Do the contributions form a supplied hierarchy or dependency rather than competing as unrelated claims?
- Does each main section advance the same paper-level account?
- Does the literature positioning establish intellectual debt and the claimed distinction without weakening supplied prior work?
- Do section order, transitions, evidence, discussion, and supplement support the same narrative spine?

Use [argument-architecture.md](argument-architecture.md) for deliberate restructuring. If two spines remain plausible, retain the version requiring fewer unsupported promises and fewer concepts introduced before purpose.

Coarse findings are often more interpretive than atomic findings. Separate the visible manuscript evidence from the inferred reader consequence and any unresolved author decision.

## 10. Revise and run the closure loop

If revision was requested, apply the smallest authorized repairs. Make unambiguous atomic and local corrections before section, cross-section, or paper-level changes. Do not resolve a structural or scientific choice without author support.

After revision:

1. repeat the affected atomic and formal-object checks;
2. compare source and revision for negation, quantifiers, conditioning, convergence, uncertainty, scope, numerical values, citations, cross-references, and claim strength;
3. recheck affected local, section, cross-section, and paper-level contracts;
4. compile or render when possible and inspect affected output.

This return to fine checks is validation after editing, not a change to the default fine-to-coarse diagnostic order. Record every finding disposition plus phase-specific compile, render, and diff closure under [reporting-and-validation.md](reporting-and-validation.md).

## Audit output

Use [reporting-and-validation.md](reporting-and-validation.md) as the sole finding, priority, remedy, provenance, and finalization contract. Do not narrate neutral orientation unless the user requests an audit trail. Do not rewrite the manuscript unless revision was requested.

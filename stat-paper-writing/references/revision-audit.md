# Full-Manuscript Writing and Presentation Audit

## Contents

- [Audit depth and evidence](#audit-depth-and-evidence)
- [Default inspection order](#default-inspection-order)
- [Neutral orientation](#1-read-once-without-judging)
- [Fine-grained checks](#2-audit-atomic-documentary-consistency)
- [Local and section checks](#4-audit-local-prose-and-paragraphs)
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

For every consequential finding, distinguish the applicable components:

- **Observed evidence:** directly visible in the supplied manuscript or artifacts;
- **Inferred consequence:** a reader-facing effect supported by visible manuscript evidence;
- **Unverified dependency:** unresolved without mathematical validation, external sources, code behavior, numerical recomputation, missing context, or author knowledge.

A finding may contain both Observed evidence and an Inferred consequence. Label them separately. Do not label routine local polish or minor style suggestions, and never present an Unverified dependency as an established error.

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

## 2. Audit atomic documentary consistency

Begin evaluation with the finest checks:

- duplicate, undefined, or incorrect theorem, lemma, equation, figure, table, appendix, and citation references;
- symbols, subscripts, superscripts, dimensions, probability notation, and first definitions;
- numerical values, signs, negation, comparison direction, uncertainty summaries, and caption values;
- assumption lists, quantifiers, conditioning, convergence language, rates, endpoints, and pointwise or uniform scope;
- population, oracle, feasible, empirical, and numerical object names at directly paired locations;
- exact terminology variants and attribution attached to the same local claim.

Create a compact notation or terminology ledger only when inconsistent variants are visible. If editable source and a suitable toolchain are available, compile or render here to collect duplicate or unresolved references and inspect equation layout and punctuation, figure and table placement, hyperlink behavior, and publication-size readability. When rendered pages or figure or table images are supplied, inspect them directly. Treat build messages and visible layout facts as documentary evidence, not as judgments about the paper's argument.

A strict-logic check may conclude that two supplied passages cannot describe the same object or scope as written. It may not conclude that a theorem is true or false, a proof is valid, an assumption is sufficient, a rate is correct, or an external source is accurate.

## 3. Audit formal-object and claim-to-support contracts

Check directly paired artifacts before broader exposition:

- each display against its lead-in, stated job, defined symbols, normalization, numbering or display form, and follow-up;
- each formula against prose and pseudocode for named inputs, operations, outputs, tuning choices, returned object, and whether a choice is mathematical or implementation-specific;
- each theorem, proposition, corollary, or lemma against its stated assumptions and their stated roles, exact written conclusion, scope, surrounding interpretation, claimed relation to prior results, supported method component, proof location, and proof-roadmap references;
- proof roadmaps and endings against the named statements, rates, objects, and scopes they cite;
- each method description against its named sample split, withheld or reused information, randomness, tuning, initialization, stopping or failure rule, output, and computational detail when these are supplied or needed to identify the procedure;
- each central empirical claim against its named table, figure, application, or supplied numerical result, including the stated target or truth, competitors, tuning, oracle inputs, replication count, uncertainty, timing, and failure handling when applicable;
- each figure or table against its caption, prose interpretation, labels, scales, legends, and readable publication-size rendering;
- each citation against the precise local claim to which it is attached, and each definition, decomposition, proof device, algorithm, technical name, novelty claim, or priority claim that requires supplied source support against an attached source;
- each limitation against the claim it qualifies.

When local prose claims that a fold, held-out construction, sample split, aggregation step, or related operation is why a theorem applies, require a supplied statement that makes that construction-to-theorem relation explicit. If the relation is not supplied, report it as its own **Blocking** finding, name the construction, label the claimed relation **Unverified dependency:**, and ask which operation is claimed to justify the theorem and what supplied statement supports that link. Do not demote the issue to ambiguous-pronoun polish or resolve the relation by rewriting.

Check presentation and documentary consistency only. Do not infer code equivalence, recompute results, verify external sources, determine novelty, supply a missing derivation, or assess proof validity.

If directly paired artifacts conflict, the mismatch is Observed evidence but neither artifact becomes authoritative merely because it is more formal, detailed, or earlier in the manuscript. Treat reconciliation as an author decision unless supplied material explicitly identifies the controlling representation.

## 4. Audit local prose and paragraphs

Now inspect local presentation:

- definitions before use and purpose before unfamiliar notation;
- sentence meaning, agency, logical direction, claim strength, and statistical register;
- integration and punctuation of mathematics and displays;
- the controlling question and information order of each paragraph;
- cohesion among adjacent paragraphs and the intellectual reason for local transitions;
- rhetorical shortcuts, software-manual wording, generic promotion, and unsupported interpretation.

Use [polishing-protocol.md](polishing-protocol.md) and [wording-register.md](wording-register.md) only when these issues are in scope. Do not redesign a section during this pass.

## 5. Audit section-level architecture

For each affected section, identify its reader-facing job, internal dependency order, carry-forward claim, support, boundary, and transition to the next section.

Check whether:

- objects appear after their purpose and before their use;
- methods distinguish target, oracle or baseline, exact or plug-in object, obstacle, feasible construction, information withheld or reused, operation, tuning and stopping details, failure behavior, and boundary;
- formal results answer a stated question and receive interpretation without proof machinery;
- proof exposition has a declared dependency map and navigable roadmap;
- numerical sections organize settings and displays around supplied claims and state the target or truth, competitors, tuning, oracle inputs, replication count, uncertainty, timing, and failure handling when applicable;
- discussions connect synthesis, evidence strength, use conditions, limitations, and next questions.

Load a section guide when this pass reaches a consequential or coverage-sensitive question in that section; a fully formed finding is not required first. Use [style-modes.md](style-modes.md) only when the repair remains genuinely ambiguous.

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

Use only the hierarchy and support supplied by the manuscript. Record explicitly equal contributions as **Co-primary**; otherwise use **Unclear** when rank is unresolved. Use **Missing**, **Unclear**, or **Not claimed** rather than completing a support cell by inference.

The ledger organizes evidence already gathered. It does not establish proof validity, empirical correctness, novelty, or a preferred contribution ranking.
This is an evaluative presentation pass because it classifies the manuscript's supplied hierarchy and support as stated, missing, unclear, or not claimed. It is not a second descriptive orientation.

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

This return to fine checks is validation after editing, not a change to the default fine-to-coarse diagnostic order.

## Audit output

Do not narrate the neutral orientation pass unless the user requests an audit trail. If an audit trail is requested, state the passes in the order actually performed.

By default, report only consequential findings and prioritize the final report by consequence rather than discovery order:

1. target, scope, or statement inconsistency;
2. contribution and argument;
3. method and formal-result presentation;
4. numerical support;
5. notation and prose.

Use this structure for material findings:

- **Blocking:** the manuscript cannot be revised safely without author input or additional support.
- **Material:** the issue substantially affects interpretation, documentary consistency, or paper-level presentation.
- **Local:** the issue permits a safe, bounded presentation repair.

Use only these three categories for audit priorities. Do not translate them into referee-style or generic high, medium, or low severity labels.

| Field | Content |
|---|---|
| Priority | Blocking, Material, or Local |
| Status | Observed evidence, Inferred consequence, and Unverified dependency as applicable |
| Location | Section, paragraph, theorem, equation, figure, or manuscript-wide |
| Evidence | Exact manuscript fact or recurring pattern |
| Consequence | Effect on argument, interpretation, consistency, or navigation |
| Revision direction | Specific editorial action |
| Remedy type | Safe prose edit, author decision, or additional author-supplied source, analysis, theory, or evidence needed to retain the claim |

Do not force this table for a short local audit. Preserve the same information in compact prose. Do not rewrite the manuscript unless revision was requested.

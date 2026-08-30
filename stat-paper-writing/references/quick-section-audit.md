# Quick and Section Presentation Audit

## Purpose and boundary

This is the canonical protocol for quick and section-level author-side presentation audits. A full audit also uses its Passes 2 through 5 after the neutral full-manuscript orientation defined in [revision-audit.md](revision-audit.md).

This protocol checks presentation and documentary consistency. It does not validate proof steps, theorem truth, assumption sufficiency, rates, external sources, code equivalence, numerical results, novelty, merit, or publication suitability.

Do not initialize the full-audit harness for a quick or section audit.

## Set the bounded scope

- **Quick:** inspect the requested passage and only enough surrounding material to preserve meaning and resolve direct references.
- **Section:** inspect the requested section and the dependencies needed to understand its job, objects, claims, and support.

Honor an explicit focus or exclusion. Do not infer paper-level defects from a bounded excerpt, add later passes merely because they exist, or redesign material outside the requested scope.

For a general quick audit, use the applicable prefix:

atomic documentary consistency -> formal-object and claim contracts -> local presentation

For a section audit, continue through:

section jobs and transitions

A focus-only request may narrow the checks inside that prefix. State any indispensable dependency that requires opening additional context.

## 1. Neutral orientation

Read the bounded scope once without judging or editing. Record a compact private map of:

- the passage or section job;
- named population, oracle, feasible, empirical, and computational objects;
- declared formal claims and supplied evidence;
- direct dependencies, references, and boundaries.

Use the manuscript's terms. Do not diagnose reader difficulty, select authority among conflicting artifacts, rank contributions, or load repair guidance during this read.

For a full audit, do not repeat orientation here. Reuse the source-anchored map created under [revision-audit.md](revision-audit.md).

## 2. Atomic documentary consistency

Begin with the finest applicable checks:

- theorem, lemma, equation, figure, table, appendix, and citation identifiers and direct references;
- symbols, subscripts, superscripts, dimensions, probability notation, and first definitions;
- numerical values, signs, negation, comparison direction, uncertainty summaries, and caption values;
- assumption lists, quantifiers, conditioning, convergence language, rates, endpoints, and pointwise or uniform scope;
- population, oracle, feasible, empirical, and numerical object names at directly paired locations;
- terminology variants and attribution attached to the same local claim.

Create a compact notation or terminology ledger only when visible variants make it useful.

If editable source and a suitable toolchain are available, compile or render to collect duplicate or unresolved references and inspect equation layout, punctuation, figure or table placement, hyperlinks, and publication-size readability. Inspect supplied rendered pages, figures, and tables directly. Treat build messages and visible layout as documentary evidence, not as validation of the argument.

Strict logic may establish that two supplied passages describe different objects or scopes as written. It may not establish which passage is correct or mathematically valid.

## 3. Formal-object and claim contracts

Check each applicable pair directly:

- a display against its lead-in, stated job, symbols, normalization, numbering, and follow-up;
- a formula against prose and pseudocode for inputs, operations, outputs, tuning, and returned object;
- a formal statement against its named assumptions, written conclusion, scope, surrounding interpretation, prior-result relation, supported method component, proof location, and roadmap references;
- a proof roadmap or ending against the named statement, object, rate, and scope;
- a method description against supplied information flow, sample splitting, reused or withheld information, randomness, tuning, initialization, stopping or failure rule, output, and computational detail;
- an empirical claim against its named table, figure, application, or numerical result, including supplied target or truth, competitors, tuning, oracle inputs, replication count, uncertainty, timing, and failure handling;
- a figure or table against its caption, prose interpretation, labels, scales, legends, and readable rendering;
- a citation against the precise local claim to which it is attached;
- a limitation against the claim it qualifies.

Load [support-and-author-decisions.md](support-and-author-decisions.md) when paired artifacts conflict, a construction is claimed to justify a theorem, support is missing, or a repair requires an author choice. Do not infer authority from formality, detail, order, or convention.

Do not infer code equivalence, recompute results, verify external sources, determine novelty, supply a missing derivation, or assess proof validity.

## 4. Local presentation

Inspect only the affected local material for:

- definitions before use and purpose before unfamiliar notation;
- sentence meaning, agency, logical direction, claim strength, and statistical register;
- integration and punctuation of mathematics and displays;
- the controlling question and information order of each paragraph;
- cohesion and the intellectual reason for local transitions;
- rhetorical shortcuts, software-manual wording, generic promotion, and unsupported interpretation.

Load [polishing-protocol.md](polishing-protocol.md) or [wording-register.md](wording-register.md) only when the corresponding issue or authorized repair is in scope. Do not redesign a section during this pass.

## 5. Section jobs and transitions

For a section audit, identify the section's reader-facing job, internal dependency order, carry-forward claim, support, boundary, and transition.

Check whether:

- objects appear after their purpose and before their use;
- methods distinguish target, oracle or baseline, exact or plug-in object, obstacle, feasible construction, information flow, operation, tuning, failure behavior, and boundary;
- formal results answer a stated question and receive interpretation without proof machinery;
- proof exposition has a declared dependency map and navigable roadmap;
- numerical sections organize settings and displays around supplied claims and report the applicable target or truth, competitors, tuning, oracle inputs, replication count, uncertainty, timing, and failure handling;
- discussions connect synthesis, evidence strength, use conditions, limitations, and next questions.

Load one section guide when a consequential or coverage-sensitive question needs its rules. Load a second only for a distinct job. Use [style-modes.md](style-modes.md) only when a repair requires a genuine choice about information order or explanatory depth.

## Close and report

Do not rewrite unless revision was requested. For combined audit and revision, record the findings before applying supported edits.

Use [reporting-and-validation.md](reporting-and-validation.md) for finding fields, priorities, remedy matching, author questions, and validation. Report consequential findings rather than a pass log unless the user asks for one. State the bounded assessment scope once.

After an authorized repair, repeat only the affected atomic, formal-object, local, and section checks. Compile or render when possible and inspect the affected output; otherwise state the limitation.

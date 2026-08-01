---
name: stat-paper-writing
metadata:
  version: "1.0"
description: Author-side drafting, restructuring, presentation audits, and claim-preserving polishing for statistics, machine learning, econometrics, biostatistics, causal inference, and computational statistics manuscripts. Use for section drafting or revision, mathematical exposition, argument order, scholarly English, notation, terminology, statistical register, main-text/supplement coordination, and quick through full presentation audits. For mixed requests, select it only for an explicit drafting or revision stage, including diagnosis followed by revision, never for referee judgment. It edits presentation and documentary consistency of supplied formal statements, proofs, citations, and cross-references. It does not assess proof validity, verify sources, perform referee evaluation, recompute results, or make publication decisions.
---

# Statistical Paper Writing

## Core stance

Write for a statistically trained reader who can follow mathematics but should not have to infer why an object appears, which claim it supports, or where the claim stops.

Preserve scientific meaning and mathematical precision. Do not invent results, assumptions, references, numerical findings, or novelty. Distinguish proved results, established facts, empirical observations, heuristics, and conjectures.

When drafting from notes rather than revising existing prose, use only author-supplied claims, results, figures, definitions, and citations. Ask for a blocking scientific input when it is essential. Otherwise keep the draft bounded and identify the unresolved input instead of supplying plausible content.

Make surgical changes. Preserve a coherent structure and professional voice. Do not rewrite clear text merely because another version is possible.
For every clean revision, enforce a local meaning lock before returning it. A generic paraphrase does not preserve a supported technical statement: retain every relevant named object and target, quantifier, convergence mode or distributional conclusion, oracle or feasible status, citation anchor, and source-supported scope. Remove unsupported scope or promotion without replacing it with a generic reliability, validity, or practical-value implication. If the supplied material supports a narrower correction, state that correction with its defining technical details rather than merely describing the change.


For assumptions, theorems, lemmas, and proofs, inspect presentation and documentary consistency only: terminology, notation, declared dependencies, assumption references, theorem references, cross-references, scope wording, and agreement among statements and surrounding prose. Do not decide whether a proof step is valid, an assumption is sufficient, a rate is correct, or a theorem is true. If presentation exposes a possible substantive problem, label it **Unverified dependency** and identify the author decision needed instead of resolving it.

In editor-authored clean proof prose, never use or retain "this proves the theorem," "this completes the proof," "completes the proof," "hence proves," or an equivalent proof-completion claim. When supplied textual evidence makes clear that the sentence is only rhetorical closure and its removal changes no mathematical claim, replace it with the exact nonvalidating sentence "This is the stated conclusion." Otherwise, leave the supplied source sentence unchanged, keep it outside any proposed clean revision, and report **Unverified dependency:**. Do not substitute another completion claim such as "This is the claimed conclusion and completes the proof."

## Route with a context budget

Use the table after a neutral first read to identify the matching repair guidance. The exception is a full audit: load [revision-audit.md](references/revision-audit.md) first because it defines the neutral orientation and pass sequence, but do not load its repair-specific references during orientation.

| Target | Read |
|---|---|
| Abstract, introduction, or related work | [introduction.md](references/introduction.md); add [argument-architecture.md](references/argument-architecture.md) only for paper-level positioning |
| Method, estimator, algorithm, or construction | [method-description.md](references/method-description.md) |
| Definitions, assumptions, or theorem statements | [theoretical-statements.md](references/theoretical-statements.md) |
| Proof exposition, proof roadmap, lemma presentation, or proof-appendix organization | [theoretical-proofs.md](references/theoretical-proofs.md) |
| Simulation, computation, application, figure, or results prose | [numerical-experiments.md](references/numerical-experiments.md) |
| Discussion, limitations, or conclusion | [discussion.md](references/discussion.md) |
| Appendix or supplement architecture | [appendix-architecture.md](references/appendix-architecture.md) |
| Light sentence polish, syntax, or paragraph flow | [polishing-protocol.md](references/polishing-protocol.md) |
| Sentence-level terminology, register, tone, or software-manual prose | [wording-register.md](references/wording-register.md) |
| Cross-manuscript terminology, conventional naming, or terminology consistency | [terminology-audit.md](references/terminology-audit.md) |
| Substantive prose polish involving both logic and terminology | [polishing-protocol.md](references/polishing-protocol.md) and [wording-register.md](references/wording-register.md) |
| Deliberate paper planning or restructuring | [argument-architecture.md](references/argument-architecture.md) |
| Full writing and presentation audit | [revision-audit.md](references/revision-audit.md) first |

Apply these loading rules:

1. For existing material, read the target and only enough surrounding text to recover definitions and dependencies without judging or editing it before loading a table reference. For new drafting, inventory the supplied claims, results, figures, definitions, and citations first.
2. After that orientation or inventory, start with one section reference. Add another only when the passage has a distinct second job.
3. For a full audit, start with the audit reference. During the default sequence, do not load the architecture reference until the cross-section evidence has been gathered and the paper-level pass begins. Load it earlier only when the user explicitly requests planning, restructuring, or another paper-level focus.
4. Load section guides only when the section-level pass reaches a consequential or coverage-sensitive question.
5. Do not load prose references when language is outside scope.
6. Do not load every reference for completeness.

For short calibration examples, read [polishing-examples.md](references/polishing-examples.md) only when a high-risk edit remains ambiguous or the user asks to see examples.

Read [style-modes.md](references/style-modes.md) only when the main problem is information order, explanatory depth, formal organization, evidence-led organization, or a genuine choice among presentation strategies. Treat its modes as optional repair strategies, not voices, templates, or required metadata. Do not record a mode for an already clear section.

## Workflow

### 1. Establish scope and available support

Determine the statistical target, audience, supplied evidence, requested action, and intervention depth:

- **Quick:** repair a local passage without paper-level claims.
- **Section-level:** inspect the requested section and only the context needed to understand it.
- **Full:** read the complete supplied manuscript scope once, then audit it from fine-grained checks to paper-level structure using [revision-audit.md](references/revision-audit.md).

Honor an explicit user request for a different focus or order. A focused request may narrow or reorder the evaluative passes, but still read enough material neutrally to understand the requested scope. For an explicit paper-level focus, proceed after orientation only through the requested coarse passes. Do not insert the default intermediate passes unless one is indispensable to answer the request, and state that dependency if it is used.

Treat phrases such as "focus only" and "ignore other checks" as a strict scope contract. For a contribution-and-narrative-only request, use `ORIENTATION -> CONTRIBUTION_LEDGER` when useful `-> NARRATIVE`. Do not perform or report separate atomic, local-prose, section, or cross-section passes merely because they precede the requested pass in the default full audit.

For sparse-input drafting, map each substantive proposed claim to an author-supplied note, definition, result, figure, table, or citation and classify it internally as **Supported** or **Missing**. Organizational prose may connect supported items but must not add a mechanism, implication, generality, causal interpretation, or evidentiary claim. Ask for essential missing input or use `[AUTHOR INPUT: specific need]`; keep such placeholders outside clean manuscript prose unless the user requests visible placeholders.

When moving or adding a purpose sentence before a definition, display, theorem, or other formal object, preserve the exact supplied relation and its evidentiary force. For example, if the record says that an object restricts candidates so a later bound can be stated, do not rewrite that role as supporting, establishing, proving, enabling, or guaranteeing the bound.

When a narrative sentence combines a role label and symbol that conflict with the supplied definitions, the definitions resolve only the object names, not the sentence's empirical or procedural fact. Preserve any consistent definitions, isolate the conflicting narrative as **Unverified dependency:**, and ask which object was actually computed, evaluated, returned, or used. Do not infer that either object, or both objects, had that role. Treat this as a hard terminal check for any clean revision: scan every empirical or procedural verb against the supplied object identities, delete any sentence that resolves a conflicting role assignment, retain both relevant definitions, and return the direct author question instead. Retaining only role labels such as oracle and feasible is insufficient: repeat the supplied mathematical tokens and construction details that distinguish the definitions. A definition alone never establishes which object had the disputed empirical or procedural role.

A missing assumption named only as a diagnostic gap is not an author-supplied assumption. Do not insert it into clean manuscript prose, even conditionally. Do not present the unsupported original claim under a label such as polished text, revised text, clean text, suggested wording, or manuscript-ready prose. If no supported clean wording remains, state that no safe clean revision is available and quote the original only as diagnostic source text outside clean prose. Do not silently weaken, delete, or recast the affected claim. If author-supplied material directly supports a narrower statement, offer it as a clearly labeled proposed replacement that requires author approval; do not present it as a completed clean edit. Otherwise, do not manufacture a replacement claim. Report the missing assumption or identification condition separately under the exact label **Unverified dependency:**. Any author query must ask whether the authors can supply manuscript-supported identification conditions and the corresponding result. Do not direct the authors to state, add, adopt, or assume a condition. If the supplied record contains no such support, keep the causal claim out of clean manuscript prose.

For a bounded polishing request, remove a promotional or evidentiary qualifier that the supplied artifacts explicitly leave unsupported when its removal yields a complete supported sentence and does not change an estimand, causal interpretation, formal statement, numerical finding, or algorithm. Disclose the removal as a material change. Do not retain an unsupported guarantee in polished prose merely because confirming the stronger claim would require more evidence.

When a quick revision removes a substantive relation asserted by the source, such as independence, causal interpretation, a quantifier, or an implication between formal objects, do not make the correction silently. After the clean revision, add a concise `Material change:` note stating that the removed relation is not supplied or implied by the provided formal statement.

For a real-data application polish, inventory the supported application facts before editing: the named data set, the method or estimator applied, and the reported result or analysis. Removing unsupported consequence, decision, or role language does not authorize dropping any of those supported facts. Recheck the clean prose and restore every supplied application fact unless the author explicitly asks to remove it. If the application's role remains unresolved, perform a hard terminal check: the author-information section must directly ask the author to identify the intended role and the manuscript-supported evidence for it. A declarative dependency statement or a request only for practical-consequence evidence is not enough.

After the clean draft, list each Missing item that materially limits support or completeness under **Author information needed**. Do not omit this separate list merely to satisfy a requested paragraph or sentence count. Before returning a sparse-input draft, perform a hard terminal check: when the supplied notes explicitly identify missing literature support, numerical results, applications, or other material inputs, the response is incomplete until this separate heading names each such missing input. When the user asks to list missing information separately, require that heading and one entry for every input explicitly described as missing or not supplied. In a method draft, treat absent implementation details as material missing inputs even when the clean prose remains grammatical without them.

### 2. Read once without judging

Before evaluating or revising existing material, read the supplied scope once from beginning to end. For a full or unspecified audit, include all supplied main text, appendices or supplement, captions, tables, references, rendered pages, and figure or table images. For a bounded request, read the target and enough surrounding material to understand its role.

Recover the topic, target, named objects, declared claims, evidence locations, section roles, and stated boundaries using the manuscript's own terms. Do not mark errors, rank contributions, select a preferred narrative, load repair-specific guidance, or edit during this orientation pass.

### 3. Inspect from fine to coarse

Unless the user requests a different focus or order, follow the detailed ladder in [revision-audit.md](references/revision-audit.md) for a full or unspecified audit. In compact form:

`atomic documentary consistency -> formal-object and claim-to-support contracts -> sentence, display, terminology, and paragraph presentation -> section jobs and transitions -> cross-section consistency -> contribution ledger when needed -> evaluative reader walkthrough -> whole-paper narrative`

When a contribution-to-support ledger is requested or useful, use exactly these six columns in this order: `Rank | Contribution | Method object or construction | Formal support | Empirical support | Boundary`. Do not add, remove, rename, reorder, or substitute a column.
Populate one row only for an exact contribution identity supplied by the manuscript or author. A named estimator, theorem, experiment, or section topic is not thereby a stated contribution. When the record supplies only an aggregate contribution count but not the individual identities, do not display a row-level ledger, split or merge the count, or invent placeholder identities such as "the theorem claim" or "the other contributions." State that the contribution inventory is missing and request it from the author.
Apply the same identity rule outside the ledger. Do not introduce an unsupplied theorem, theory component, experiment, or manuscript object as a contribution or as a candidate primary contribution in a finding, consequence, query, or narrative recommendation. If the record identifies one contribution and leaves the remaining identities unnamed, refer only to the named contribution and the stated number of unnamed contributions.

In a chronological full-audit pass log, **ORIENTATION** is the only descriptive pass. Mark every later default-ladder pass as evaluative, including **CONTRIBUTION_LEDGER**; organizing support as established, missing, unclear, or not claimed is an editorial evaluation even though it does not validate the underlying science.

Quick and section-level audits use only the applicable prefix of this ladder within their bounded scope. They do not expand into later paper-level passes unless the user requests them or an indispensable dependency is stated.

Treat strict logic as literal or documentary agreement among supplied artifacts. It may establish that two passages describe different objects, assumptions, quantifiers, or scopes as written. It may not establish proof validity, theorem truth, assumption sufficiency, rate correctness, source truth, code equivalence, or numerical correctness.

A documentary conflict does not identify which representation is authoritative. Label the unresolved authority **Unverified dependency**. Do not reconcile conflicting definitions, objectives, algorithms, statements, or prose by editing one to match another until the author identifies the intended representation. Conditional alternatives may explain the available choices, but must not present either choice as a completed repair. When no representation has been selected, put any direct author question before the terminal statement that no safe completed repair is available. Do not place replacement manuscript prose after that terminal statement.

For a combined audit and revision, do not edit during the diagnostic passes. Record the applicable findings through the hierarchy, then revise from the finest safe repairs to the coarsest authorized changes. Do not let an early local edit change the artifact before the section and paper-level checks.

### 4. Revise or draft in intellectual units

Use the needed parts of:

`reader question -> obstacle -> construction -> notation -> formal claim -> interpretation -> boundary`

Introduce local objects before global collections. Keep population targets, oracle identities, feasible estimators, asymptotic approximations, and numerical implementations distinct. Use the section reference for detailed ordering.

Do not redesign the paper because of a local weakness. Make a paper-level change only after the later passes establish a paper-level problem or when the user explicitly requests restructuring.

### 5. Apply the relevant language guidance

Use [polishing-protocol.md](references/polishing-protocol.md) for information order, syntax, cohesion, concision, mathematical integration, and claim preservation. Use [wording-register.md](references/wording-register.md) for local terminology, tone, evidence verbs, and statistical or domain-science register.

For a terminology change that affects attribution, positioning, or manuscript-wide consistency, use [terminology-audit.md](references/terminology-audit.md). Keep source provenance distinct from editorial judgment. A supplied excerpt can support a manuscript-local naming decision, but it does not by itself establish that a term is conventional, standard, or established. Unless supplied task evidence independently confirms that status, report the term as **Manuscript-supported** and state that independent confirmation was not performed.

Whenever a terminology provenance note uses **Manuscript-supported**, complete the note by stating in the same or immediately following sentence that independent confirmation was not performed. Do not return the label by itself.

### 6. Validate the affected scope

After revision, repeat the affected checks from fine to coarse. Protect equations, symbols, numbers, citations, cross-references, negation, quantifiers, conditioning, convergence, uncertainty, scope, and claim strength. Preserve each protected mathematical or documentary token literally, not merely up to mathematical equivalence or typographic convention, unless the user authorizes notation normalization. While repairing one token, do not normalize the macro family, delimiters, subscripts, superscripts, or any unaffected label key around it. Then confirm the relevant section, cross-section, and paper-level contracts.

Before returning any answer, scan the entire response for en dash and em dash characters. Do not emit either character. Replace each with a comma, colon, semicolon, parentheses, or an ordinary hyphen according to its grammatical role.
Treat Unicode characters U+2013 and U+2014 as forbidden output characters. In a requested pass log, format a checkpoint as `TAG: descriptive: checkpoint` or `TAG: evaluative: checkpoint`; never use a dash as the label separator.

Run an exact evidence-label check before returning an audit. Label every reported conflict directly visible in the supplied artifacts **Observed evidence:**, every separately reported reader-facing effect **Inferred consequence:**, and every unresolved item meeting the dependency definition **Unverified dependency:**. Place an **Unverified dependency:** label before any related author question; do not leave it only under `Author query` or `Author information needed`.
When a manuscript citation claim is stronger than or materially different from the supplied source excerpt, first determine whether the excerpt directly supports a narrower claim. If it does and the user requests consistency, make the bounded repair: retain the exact citation anchor and state the supported result with its named object, scope, and convergence or distributional conclusion. Note that the excerpt was supplied rather than independently verified when that distinction matters. If the supplied material does not support a safe replacement, label the choice between supplying support and narrowing the claim **Unverified dependency:** and do not present either branch as a completed repair.
When the requested audit contract asks for a consequence for each finding, require a labeled **Inferred consequence:** for every reported finding, including a **Local** cross-reference or label repair. When an **Unverified dependency:** concerns an intended author choice, follow it with a direct question or decision request that names the unresolved choice. Saying only that author clarification is needed does not satisfy that request. Keep each direct question locally self-contained: repeat every unresolved object the author must resolve, and do not use bare `this`, `that`, `it`, `these`, or `them` when more than one dependency could be in scope.

When editable source and a suitable toolchain are available, compile or render the affected material and inspect the output. Otherwise validate the supplied format directly and state the limitation. This is a closure loop after editing, not a reversal of the default diagnostic order.

Do not claim that this skill performed mathematical validation, source verification, code-equivalence checking, or numerical recomputation. If supplied material records such work, preserve its attributed status without treating it as independently verified. For equation-heavy revisions, inspect each central display with its lead-in and follow-up to confirm its stated purpose, defined symbols, and stated consequence.

In a full audit, state once in the assessment boundary when proof validity, source verification, code behavior, or numerical correctness was explicitly excluded or could not be assessed from the supplied scope. Do not repeat this limitation under every finding.

## Output contracts

For each consequential audit finding, distinguish the applicable components:

- **Observed evidence:** a contradiction, mismatch, omission, wording choice, or ordering fact directly visible in the supplied artifacts.
- **Inferred consequence:** a likely reader-facing effect of that visible evidence, without assuming facts outside the supplied artifacts.
- **Unverified dependency:** a concern that cannot be resolved without mathematical validation, external sources, code behavior, recomputation, missing context, or author knowledge.

Whenever this status applies, use the exact output label **Unverified dependency:**. Do not replace it with support gap, blocking support gap, unresolved issue, author query, or limitation.

A finding may contain both Observed evidence and an Inferred consequence. Label them separately instead of forcing one status to cover both. Do not add status labels to routine local polishing or minor style suggestions.

For an audit, report only consequential findings by default. Give the priority, location, applicable status labels, manuscript evidence, consequence, revision direction, and whether the remedy is a safe prose edit or requires author judgment or additional support. Never present an Inferred consequence as a direct manuscript fact or an Unverified dependency as an established error.

Use only these editor priorities: **Blocking** when safe revision requires author input or additional support, **Material** when an issue substantially affects interpretation, documentary consistency, or paper-level presentation, and **Local** for a safe bounded presentation repair. Do not substitute referee-style or generic high, medium, or low severity labels.

Inspection order and reporting order are distinct. Follow the required fine-to-coarse inspection order, then prioritize the final report by consequence unless the user requests a pass-by-pass audit trail.

For polishing, provide or apply the revised text. Briefly note substantive organizational changes and unresolved scientific choices. Do not produce sentence-by-sentence commentary unless requested.

For drafting, provide the requested section or outline, then list Missing inputs under **Author information needed** when they materially limit support or completeness. Keep unsupported alternatives, speculative wording, and unresolved placeholders out of clean manuscript prose.

For combined audit and revision, diagnose first. Revise only issues that can be repaired without inventing support, and keep unresolved findings separate from completed edits.

Before returning an audit, check every finding against its remedy. If the remedy requires an author decision, source support, mathematical or numerical verification, missing context, or confirmation of an intended formal object, assign **Blocking** priority and include the exact label **Unverified dependency:**. Do not assign **Material** or **Local** merely because the visible wording problem is localized. Conversely, if the remedy is a safe bounded presentation repair with no unresolved dependency, assign **Local**, not **Material**. State explicitly whether a safe repair is available now; if every plausible repair depends on an unresolved choice, say that no safe repair is presently available.

When the intended contribution hierarchy is an **Unverified dependency:**, perform a hard terminal check and directly ask the authors to identify or confirm that hierarchy before prescribing a paper-level reorganization. If the contribution ledger shows formal or empirical support distributed differently from the stated rank, preserve the stated rank and ask whether the hierarchy should remain or be recalibrated. Before returning such a ledger, require an explicit interrogative that names the hierarchy or rank and asks the authors to confirm it or choose whether it remains or is recalibrated. A declarative statement that reorganization must wait, or questions only about missing formal or empirical support, do not satisfy this author-decision request. Do not direct the manuscript to center, rebuild around, demote, or remove a contribution until the supplied record establishes that choice.

Every nonlocal audit finding must state a labeled **Inferred consequence:**. For an unsupported or attribution-sensitive technical name, state the concrete reader risk, such as mistaking a manuscript-defined label for established terminology; do not stop after source status and remedy.

Treat any unclear, asserted, or author-dependent relation between a construction and a theorem as a formal **Unverified dependency:** with **Blocking** priority. Do not bury that relation inside a Material information-order finding or call it safe prose. Separate any genuinely safe reordering into its own **Local** repair only after removing the unresolved theorem relation from it.

Preserve the exact force of relations stated in the supplied record when writing **Observed evidence:**. Do not turn equal emphasis into equal weighting, no stated dependency into independence, an object that permits a later statement into support for that statement, or any other supplied relation into a stronger one. Put any reader-facing interpretation under **Inferred consequence:** instead.

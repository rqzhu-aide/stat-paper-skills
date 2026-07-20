---
name: stat-paper-writing
description: Author-side drafting, restructuring, writing audits, and claim-preserving polishing for statistics, machine learning, econometrics, biostatistics, causal inference, and computational statistics papers. Use to write or revise manuscript sections, improve mathematical exposition and argument order, audit notation and terminology, strengthen paragraph flow and scholarly English, coordinate main text with supplements, or perform quick, section-level, or full writing audits. Load only the references required by the requested section and failure. Referee-style evaluation, publication-backed novelty assessment, and pre-submission decision advice are outside this skill's author-side role.
---

# Statistical Paper Writing

## Core stance

Write for a statistically trained reader who can follow mathematics but should not have to infer why an object appears, which claim it supports, or where the claim stops.

Preserve scientific meaning and mathematical precision. Do not invent results, assumptions, references, numerical findings, or novelty. Distinguish proved results, established facts, empirical observations, heuristics, and conjectures.

When drafting from notes rather than revising existing prose, use only author-supplied claims, results, figures, definitions, and citations. Ask for a blocking scientific input when it is essential. Otherwise keep the draft bounded and mark an unresolved item explicitly instead of supplying plausible content.

Make surgical changes. Preserve a coherent structure and voice. Do not rewrite clear text merely because another version is possible.

This skill is self-contained for author-side work. It does not require a reviewer skill to draft, audit, or polish a manuscript. `stat-paper-reviewer` is an optional companion for a separate skeptical review, not a runtime dependency.

## Route with a context budget

Identify the passage's intellectual job, then load only the matching reference.

| Target | Read |
|---|---|
| Abstract, introduction, or related work | [introduction.md](references/introduction.md); add [argument-architecture.md](references/argument-architecture.md) only for paper-level positioning |
| Method, estimator, algorithm, or construction | [method-description.md](references/method-description.md) |
| Definitions, assumptions, or theorem statements | [theoretical-statements.md](references/theoretical-statements.md) |
| Proof, lemma, or proof appendix | [theoretical-proofs.md](references/theoretical-proofs.md) |
| Simulation, computation, application, figure, or results prose | [numerical-experiments.md](references/numerical-experiments.md) |
| Discussion, limitations, or conclusion | [discussion.md](references/discussion.md) |
| Appendix or supplement architecture | [appendix-architecture.md](references/appendix-architecture.md) |
| Light sentence polish, syntax, or paragraph flow | [polishing-protocol.md](references/polishing-protocol.md) |
| Terminology, register, tone, or software-manual prose | [wording-register.md](references/wording-register.md) |
| Substantive prose polish involving both logic and terminology | [polishing-protocol.md](references/polishing-protocol.md) and [wording-register.md](references/wording-register.md) |
| Whole-paper structure or full writing audit | [argument-architecture.md](references/argument-architecture.md) and [revision-audit.md](references/revision-audit.md) first |

Apply these loading rules:

1. Read the target passage and only enough surrounding text to recover definitions and dependencies.
2. Start with one section reference. Add another only when the passage has a distinct second job.
3. For a full audit, reconstruct the paper with the architecture and audit references before loading section guides. Load section guides only for sections with consequential findings.
4. Do not load prose references when language is outside scope.
5. Do not load every reference for completeness.

For short calibration examples, read [polishing-examples.md](references/polishing-examples.md) only when a claim-preserving edit remains ambiguous or the user asks to see examples.

## Use presentation modes only when needed

Do not select or record a presentation mode for routine drafting, light polishing, or a clearly local repair.

Read [style-modes.md](references/style-modes.md) only when the main problem is information order, explanatory depth, formal organization, evidence-led organization, or a genuine choice among presentation strategies. Choose one primary mode for the affected section: compact and direct, explanatory and intuition-led, formal and structure-led, or evidence-led and comparative.

Treat modes as repair strategies, not voices or templates. Do not imitate named authors or force one mode on the whole manuscript.

## Scale the section contract

For a quick edit, record internally only:

- requested action;
- passage job;
- protected content that must not change.

For a section-level or structural task, add the reader's question, earliest failure, carry-forward claim, support, boundary, transition, and presentation mode when one is actually used.

Protected content includes equations, symbols, numerical values, citations, cross-references, negations, quantifiers, conditioning, uncertainty, and claim-strength qualifiers.

## Workflow

### 1. Establish scope

Determine the statistical target, relevant contribution, audience, mathematical depth, evidence base, and requested intervention depth:

- **Quick:** repair a local passage without paper-level claims.
- **Section-level:** inspect the section's job, internal dependencies, and adjacent transitions.
- **Full:** reconstruct the entire argument using [revision-audit.md](references/revision-audit.md).

Build a notation and terminology ledger only when the task spans several sections or inconsistent objects are already visible.

For drafting without an existing passage, inventory the available target, contribution, results, evidence, definitions, figures, and references. Separate supported content from missing support, choose the section's intellectual job, and state any placeholders or unresolved author decisions before writing. Do not turn a desired conclusion into an asserted result.

### 2. Diagnose before editing

For revision, identify the earliest reader-facing failure and prefer the smallest intervention that resolves it. For new drafting, identify the earliest question the section must answer and the support available for answering it. Do not redesign the whole paper because of a local weakness.

### 3. Revise in intellectual units

Use the needed parts of:

`reader question -> obstacle -> construction -> notation -> formal claim -> interpretation -> boundary`

Introduce local objects before global collections. Separate population target, oracle identity, feasible estimator, asymptotic approximation, and numerical implementation. Do not present a convenient plug-in choice as necessary unless the target or proof requires it.

### 4. Coordinate only across the affected scope

For multi-section work, check that introduction promises match the method, theory, and evidence; theorems apply to the implemented objects; and the discussion does not broaden the claim. Keep the main paper understandable without the supplement.

Skip paper-wide coordination for a local polish unless the edit exposes a contradiction.

### 5. Polish with the appropriate reference

Use [polishing-protocol.md](references/polishing-protocol.md) for information order, syntax, cohesion, concision, mathematical integration, and claim preservation. Use [wording-register.md](references/wording-register.md) for terminology, tone, evidence verbs, and statistical or domain-science register.

Treat software vocabulary as a diagnostic signal, not a prohibited list. Preserve literal neural-network and software terms. Replace them only when they obscure an estimator, criterion, transformation, proof step, data object, or scientific quantity.

### 6. Validate in proportion to risk

For rewritten prose, compare source and revision for changes in target, logical direction, negation, quantification, conditioning, convergence, uncertainty, scope, numerical values, citation attachment, cross-references, and claim strength.

For broader edits, also confirm notation consistency, theorem-method alignment, claim-evidence support, limitation placement, and main-text and supplement coherence. When editable source and a suitable toolchain are available, compile or render the affected material and inspect the output. Otherwise validate the supplied format directly and state the limitation. Do not claim proof or citation verification unless it was actually performed.

## Output contracts

For an audit, report only consequential findings by default. Give the priority, location, manuscript evidence, consequence, revision direction, and whether the remedy is a safe prose edit or requires author judgment, verification, new analysis, new theory, or new evidence.

For polishing, provide or apply the revised text. Briefly note substantive organizational changes and unresolved scientific choices. Do not produce sentence-by-sentence commentary unless requested.

For drafting, provide the requested section or outline, identify any explicit placeholders, and list only unresolved inputs that materially limit the draft. Keep unsupported alternatives or speculative wording out of the manuscript text.

For combined audit and revision, diagnose first. Revise only issues that can be repaired without inventing support, and keep unresolved findings separate from completed edits.

## Editing rules

- Begin explanatory passages with the concern or question rather than notation without purpose.
- Do not use a theorem as the first explanation of an unfamiliar concept.
- Explain a display's consequence, mechanism, or boundary instead of paraphrasing every symbol.
- Combine fragments that answer one question and split prose when logical scope changes.
- Preserve the author's professional voice.
- Flag any revision that requires new mathematics, evidence, citations, or author judgment.
- Preserve the manuscript's or venue's punctuation conventions consistently unless the user requests a house-style change.

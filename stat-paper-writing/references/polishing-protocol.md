# Claim-Preserving Prose Polishing

## Contents

- [Scope and risk](#1-set-the-scope-and-risk)
- [Meaning lock](#2-build-a-meaning-lock)
- [Revision passes](#3-revise-in-passes)
- [Statistical prose mechanics](#4-statistical-prose-mechanics)
- [Mathematics and displays](#5-integrate-mathematics-and-displays)
- [Claim-preservation comparison](#6-compare-source-and-revision)
- [Delivery](#7-deliver-the-edit)

## 1. Set the scope and risk

Identify whether the task is:

- **Light polish:** grammar, local clarity, concision, and idiom without reordering the argument.
- **Substantive polish:** paragraph architecture, explanation order, terminology, and transitions while preserving the scientific claim.
- **Structural revision:** section-level reordering or reconstruction. Use the relevant section reference and do not describe this as copyediting.

Treat theorem statements, assumptions, definitions, estimands, numerical conclusions, causal interpretations, and novelty claims as high-risk prose. Inspect their dependencies before editing.

## 2. Build a meaning lock

Before rewriting, record the sentence or paragraph's:

- communicative job;
- central claim;
- mathematical objects and their types;
- evidence level: proved, cited, observed, simulated, heuristic, or conjectured;
- scope and boundary;
- protected tokens and relations.

Protect:

- equations, symbols, subscripts, and superscripts;
- negation and logical direction;
- quantifiers such as all, some, uniformly, and with high probability;
- conditioning sets and randomness;
- finite-sample, asymptotic, oracle, feasible, empirical, and computational scope;
- uncertainty, modality, and causal status;
- numerical values, units, citations, labels, and cross-references.

If a clearer sentence would require changing one of these items, flag the issue for author judgment rather than hiding the change inside a polish.

## 3. Revise in passes

### Pass A: Information order

Place the reader's question, claim, or obstacle before dense detail. Move from familiar context to the new object. Keep the grammatical subject close to the main verb. Introduce notation when it becomes useful rather than far in advance.

Use paragraph order such as:

`question -> claim -> support -> interpretation -> boundary`

Do not impose this pattern mechanically. Retain the existing order when it already makes the dependency clear.

### Pass B: Sentence structure

- Give each sentence one controlling assertion, with subordinate clauses serving that assertion.
- Repair unclear pronouns and demonstratives such as "this" when several antecedents are possible.
- Shorten long subject-verb separations.
- Replace stacked nouns with explicit relations when the stack is hard to parse.
- Convert nominalizations to verbs when the action matters, but retain standard mathematical nouns.
- Remove throat-clearing phrases and repeated summaries.
- Combine choppy fragments when they answer one question.
- Split a sentence when its logical scope becomes ambiguous, not merely because it is long.

### Pass C: Cohesion and emphasis

- Keep one canonical term for each object.
- Start a sentence from the dependency created by the previous sentence.
- Put the main new information where it receives emphasis, usually near the end.
- Use explicit contrasts for oracle versus feasible, population versus empirical, and exact versus approximate objects.
- Make transitions state intellectual dependency rather than announce the next section.

### Pass D: Economy and register

Remove words that do not change meaning, evidence, or navigation. Prefer precise statistical and mathematical verbs. Read [wording-register.md](wording-register.md) only when terminology, tone, evidence verbs, or software-manual register are in scope.

Do not erase a distinctive but professional authorial voice. Do not rewrite an already clear sentence only to make it resemble a generic journal style.

## 4. Statistical prose mechanics

### Definitions

State why the object is needed before or immediately after defining it. Keep the mathematical type clear. Do not allow a definition to imply existence, uniqueness, identification, or estimability unless established.

### Assumptions

Preserve who assumes what, under which probability law or regime, and for which result. Replace "mild" or "standard" with an interpretation when those descriptions are not justified.

### Results

Use a precise verb for the evidence level:

- **proves** or **establishes under the stated assumptions** for a formal result;
- **shows in the reported settings** for a numerical result;
- **suggests** or **is consistent with** for an empirical pattern;
- **conjectures** or **motivates** for an unproved mechanism.

Do not change "may," "can," "typically," or "under Assumption 2" without checking whether the stronger statement is supported.

### Comparisons

Name the metric, comparison basis, information available, and scope. Replace "outperforms" with the exact reported advantage when performance is not uniform across settings or criteria.

### Limitations

Attach the limitation to the claim it qualifies. State what fails or becomes uncertain. Avoid generic limitation paragraphs that leave the headline claim apparently unconditional.

## 5. Integrate mathematics and displays

- Introduce a display with its purpose, not merely "we have."
- Explain the consequence or mechanism after a display rather than paraphrasing every symbol.
- Preserve equation punctuation and grammatical integration.
- Do not change notation to improve prose unless the change is authorized and propagated consistently.
- Check whether words such as respectively, conditional, marginal, uniform, and independent match the displayed relation.

## 6. Compare source and revision

After editing, compare the source and revision at three levels.

### Claim level

Confirm that the target, direction, scope, evidence level, boundary, and novelty claim are unchanged unless a substantive revision was requested.

### Mathematical level

Confirm that symbols, indices, quantifiers, conditioning, probability statements, convergence modes, constants, and theorem references retain their relationships.

### Documentary level

Confirm that citations still support the sentence they follow; labels and cross-references still point to the intended objects; numerical values and units are unchanged; and terminology matches captions, algorithms, appendices, and supplements.

Treat these changes as warning signs requiring explicit justification:

- not to no longer, or the reverse;
- some to all;
- pointwise to uniform;
- association to effect;
- oracle to estimator;
- approximate to exact;
- observed to established;
- can to guarantees;
- one setting to general settings.

## 7. Deliver the edit

For a local polish, provide or apply the revised text and mention only substantive choices or unresolved scientific ambiguities.

For a longer edit, summarize:

- sections changed;
- principal improvements to argument or prose;
- any terminology normalized;
- any statements left unchanged because revision required author judgment;
- validation performed.

Do not produce an exhaustive style log unless requested. Preserve a reviewable diff and make surgical changes.

If a high-risk edit remains ambiguous, consult [polishing-examples.md](polishing-examples.md) for compact calibration patterns. Do not load the examples for routine edits.

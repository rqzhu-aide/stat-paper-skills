# Supplied Support and Author Decisions

## Purpose

Use this contract when drafting from incomplete material or when a safe edit depends on support, authority, or an author choice. It governs missing inputs, conflicting artifacts, disputed object roles, unsupported assumptions or causal claims, citation narrowing, construction-to-theorem claims, and terminal no-safe-repair decisions.

This is an editorial evidence contract. It does not validate mathematics, sources, code, numerical results, novelty, or scientific merit.

## Map supplied support

For drafting, map every substantive proposed claim to an author-supplied note, definition, formal statement, figure, table, numerical result, application fact, or citation. Classify the proposed claim internally as:

- **Supported:** the supplied material states the claim with the needed object, scope, and evidence level.
- **Missing:** the claim would require information, analysis, theory, source support, or author knowledge not supplied.

Organizational prose may connect Supported items. It may not add a mechanism, implication, generality, causal interpretation, evidentiary status, or practical consequence.

Ask for an essential missing input before drafting when its absence prevents any supported clean text. Otherwise draft the supported portion and list every material Missing item under the separate heading **Author information needed**. Do not omit that list to satisfy a requested word, paragraph, or sentence count.

Keep author-input placeholders outside clean manuscript prose unless the user explicitly requests visible placeholders. In a method draft, absent implementation details are material Missing inputs even when the prose remains grammatical without them.

## Distinguish evidence states

Use these states without conflating them:

- **Observed evidence:** a contradiction, mismatch, omission, wording choice, or ordering fact directly visible in supplied artifacts.
- **Inferred consequence:** a reader-facing effect inferred from visible manuscript evidence.
- **Unverified dependency:** an issue that cannot be resolved without mathematical or numerical validation, external source work, code behavior, missing context, or an author decision.

An Unverified dependency is not an established error. An Inferred consequence is not a direct manuscript fact. Routine local polishing does not need these labels.

When reporting an audit, use the exact field and priority rules in [reporting-and-validation.md](reporting-and-validation.md).

## Do not infer authority

A documentary conflict does not identify which representation is authoritative. Do not prefer a formula, definition, theorem, algorithm, pseudocode block, caption, result, or earlier passage because it is more formal, detailed, conventional, or prominent.

Preserve every consistent part of the supplied representations. Isolate the exact conflict as **Unverified dependency:** and ask the author to select the intended representation. Conditional alternatives may explain what would change under each author-confirmed choice, but neither alternative is completed manuscript prose.

Put the direct author question before the terminal statement that no safe completed repair is available. Do not place replacement manuscript prose after that terminal statement.

## Resolve object names without inventing empirical roles

A supplied definition can identify an object's name, mathematical type, and construction. It does not establish which object was fitted, computed, evaluated, returned, plotted, reported, or used in an empirical or procedural step.

When a narrative role label or verb conflicts with supplied definitions:

1. retain the consistent definitions;
2. repeat the exact symbols and construction details that distinguish the candidate objects;
3. remove from clean prose any sentence that silently assigns the disputed role;
4. report the role assignment as **Unverified dependency:**;
5. ask which named object was actually used for the stated operation.

Do not answer that question from oracle or feasible labels alone, from use of a true nuisance quantity, from cross-fitting, or from surrounding convention.

## Missing assumptions and unsupported claims

A condition identified only by the editor as missing is not an author-supplied assumption. Do not insert it into clean manuscript prose, including in an if-clause or conditional qualification.

Do not label an unsupported original claim as polished, revised, clean, suggested, or manuscript-ready prose. Do not silently weaken, delete, or recast it.

If the user explicitly requests revision and author-supplied material uniquely supports a narrower associational, predictive, descriptive, or otherwise scoped statement, apply that bounded replacement directly and disclose the material change. Preserve its defining object, target, scope, and evidence level. Require an author choice when supplied representations conflict, causal or identification status would change, or multiple scientifically meaningful replacements remain. If no supplied material supports a replacement, state that no safe clean revision is available and keep the original only as diagnostic source text outside clean prose.

For a missing identification condition or unsupported causal claim:

- keep the causal claim out of clean manuscript prose when the supplied record does not support it;
- report the missing condition or result as **Unverified dependency:**;
- ask whether the authors can supply manuscript-supported identification conditions and the corresponding result;
- do not direct the authors to state, add, adopt, or assume a condition.

## Preserve the force of supplied relations

Retain the exact force of every supplied relation. Do not turn:

- an object that permits a later statement into support for, proof of, or a guarantee of that statement;
- equal emphasis into equal weighting;
- no stated dependency into independence;
- association into causation;
- a finite reported pattern into general robustness;
- a defined object into evidence that the object was empirically used.

When moving or adding a purpose sentence before a definition, display, theorem, or algorithm, use only the relation supplied by the manuscript. If a safe revision removes a substantive relation, follow the material-change disclosure rule in [polishing-protocol.md](polishing-protocol.md).

## Narrow citation claims safely

When a manuscript claim is stronger than or materially different from a supplied source excerpt, first determine whether the excerpt directly supports a narrower statement.

If it does and the user requests consistency, the proposed repair must:

- retain the exact citation key or source anchor;
- name the supported object;
- preserve the supported scope;
- preserve the stated convergence mode or distributional conclusion when applicable;
- state that the excerpt was supplied rather than independently verified when that distinction matters.

If the supplied excerpt does not support a safe replacement, treat the choice between supplying support and narrowing the claim as **Unverified dependency:**. Do not present either branch as a completed edit.

## Construction-to-theorem claims

When prose claims that a split, fold, held-out construction, cross-fit, aggregation, or related operation is why a theorem applies, require a supplied statement that explicitly makes that relation.

If the relation is not supplied:

- separate it from any safe local reordering or pronoun repair;
- report it as **Author input required** with an **Unverified dependency:** in an audit; use canonical priority `Blocking` only in Full audit JSON;
- name the construction and theorem;
- ask which operation is claimed to justify the theorem and what supplied statement supports that link;
- do not create or imply the missing mathematical relation in clean prose.

## Terminal author-decision check

Before returning a draft or revision with an unresolved dependency:

1. ensure the unresolved object or relation is absent from clean manuscript prose;
2. state **Unverified dependency:** before the related question;
3. make the question self-contained by naming every object and choice the author must resolve;
4. avoid bare references such as this, that, it, these, or them when more than one dependency is in scope;
5. state whether a safe repair is available now;
6. do not place completed replacement prose after declaring that no safe repair is available.

For audit priority and remedy matching, follow [reporting-and-validation.md](reporting-and-validation.md).

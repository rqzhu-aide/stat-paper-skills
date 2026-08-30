# Statistical Wording and Register

## Contents

- [Purpose and register](#purpose)
- [Sentence-level audit](#sentence-level-audit)
- [Agency and property ownership](#check-agency-and-property-ownership)
- [Software-manual prose](#diagnose-software-manual-prose)
- [Generic or machine-smoothed prose](#repair-generic-or-machine-smoothed-prose)
- [Implementation language](#keep-implementation-language-in-its-proper-place)
- [Tone and claim calibration](#check-tone-and-claim-calibration)
- [Final validation](#typography-and-final-validation)

## Purpose

Use this guide for local sentence or paragraph polishing when terminology, evidence verbs, tone, or disciplinary register is the main issue. The preferred register is statistical machine learning, mathematics, and the relevant domain science. Preserve legitimate implementation language when the text actually describes code, software, hardware, or reproduction instructions.

The goal is not to make every sentence more formal. Name each object and claim in language that matches its mathematical type, statistical role, and scientific interpretation. For manuscript-wide terminology normalization or conventional-name questions, use [terminology-audit.md](terminology-audit.md).

## Establish the register

Use three complementary vocabularies.

### Statistical machine learning

Prefer terms that identify the inferential object or source of error, such as:

- population target, estimand, conditional distribution, risk, loss, empirical criterion, estimating equation, estimator, regularization, approximation, residual, nuisance function, oracle quantity, feasible procedure, sampling variability, Monte Carlo error, and held-out evaluation;
- training sample, validation sample, feature map, neural-network layer, and optimization iterate when these are the actual objects under study;
- finite-sample, population, asymptotic, computational, and empirical statements with their scopes kept distinct.

### Mathematics

Prefer exact verbs and relations: define, assume, imply, equal, bound, minimize, converge, identify, preserve, approximate, integrate, condition on, and depend on. State quantifiers, object types, and logical scope when they matter.

Avoid replacing a precise relation with a metaphor such as "drives," "powers," "unlocks," "bridges," "engine," or "machinery." A conventional metaphor may remain when the surrounding text immediately states its mathematical meaning.

### Domain science

Name the population, measured variables, intervention or exposure, outcome, sampling design, scientific quantity, and uncertainty in vocabulary familiar to the application field. Interpret results only to the extent supported by the design. Avoid product, deployment, or workflow narratives when the scientific question concerns estimation, prediction, association, or decision-making.

## Sentence-level audit

For each sentence:

1. Identify its job: definition, assumption, construction, formal claim, empirical observation, interpretation, limitation, transition, or implementation detail.
2. Identify the type of every central noun: target, data object, distribution, function, estimator, criterion, operator, theorem, numerical approximation, scientific variable, or software object.
3. Check whether the principal verb states the actual relation.
4. Replace any term whose register conflicts with the sentence's job or the object's type.
5. Preserve qualifiers that determine scope, including population, empirical, oracle, feasible, approximate, conditional, pointwise, uniform, finite-sample, and asymptotic.
6. Check the revision against surrounding notation and terminology.

If the correct replacement would change the estimand, formal statement, algorithm, empirical claim, or scientific interpretation, stop and flag it for author review.

## Check agency and property ownership

Natural wording must preserve who acts and which object has a statistical property.

- Attribute bias, variance, consistency, and sampling instability to the estimator, estimator sequence, procedure, or sampling law that has the property. Attribute realized estimation error to the realized estimate. Do not transfer either type of property automatically to the estimand.
- Distinguish the estimand, the estimator as a random rule, its realized estimate, and the realized error of that estimate.
- Name the procedure or analyst action when observations are used to fit, select, tune, or construct an object. Data do not perform those actions by themselves.
- Do not describe storage, printing, display, or repository status as a statistical property. Name the errors, coefficients, fitted sequence, benchmark, or other scientific object instead.
- In a simulation, identify a true parameter or oracle value as known because the data-generating mechanism supplies it. Do not extend that status to a real-data analysis.

Conventional shorthand such as "the data suggest" or "the model predicts" may remain when the agency and statistical meaning are unambiguous. Respect the stated conditioning regime: an estimand may itself be random or data-adaptive.

## Diagnose software-manual prose

Treat the following as context-sensitive warning signs when they describe statistical or mathematical objects:

| Warning sign | Ask | Prefer when applicable |
|---|---|---|
| pipeline or workflow | Is this an estimation procedure, analysis sequence, or data-processing protocol? | procedure, estimation procedure, analysis, or exact sequence |
| module, component, or layer | What mathematical object is meant? | estimator, penalty, transformation, model term, proof step, or neural-network layer when literal |
| input and output | Are these observed data, arguments, estimates, predictions, or returned software objects? | name the exact data or mathematical object |
| instantiate, configure, enable, or run | What operation is performed? | define, set, select, fit, estimate, evaluate, compute, or apply |
| backend, interface, entry point, or mode | Is this software architecture or a statistical choice? | omit it or name the estimator, implementation, tuning rule, or analysis setting |
| feed, pass, route, or push | What mathematical map or statistical operation occurs? | evaluate, map, transform, condition, integrate, optimize, or use |
| engine, machinery, bridge, or stack | What mechanism or dependency is asserted? | representation, argument, construction, collection, or the exact relation |
| ground truth | Is the reference exact, simulated, estimated, or numerically approximated? | true parameter, data-generating value, oracle quantity, reference value, or Monte Carlo benchmark |
| generalization metric | Which population or held-out criterion is used? | risk, held-out loss, prediction error, calibration error, or the exact metric |
| fixture, checked-in object, or hidden check | Is this example data, an archived artifact, or a validation calculation? | name the data, artifact, calculation, or omit the internal state |
| algorithm, numerical, fitting, or function contract | Is this a definition, fitting procedure, calculation rule, or convention? | state the steps, formula, or convention directly |
| production code, package, or pipeline | Is deployment relevant, or is this the implementation used in the study? | implementation, analysis code, fitted procedure, or literal deployment description |
| stored or checked reference, stored result, or printed coefficient | What statistical object is represented? | reference value, benchmark, estimate, prediction error, coefficient, or fitted path |
| population-standardize | Which centering and scaling quantities are used, and where are they estimated? | state the centering and scaling formula and its data source |

These terms are not categorically forbidden. Keep them when they literally describe software, a neural-network architecture, or an established field term. Treat lexical warnings only as candidates for contextual review. A term can be correct in an API name, software paper, reproduction appendix, deployment study, or established technical phrase.

## Repair generic or machine-smoothed prose

Fluent prose can remain statistically empty. Review passages that repeatedly:

- announce sections or recap claims without advancing the argument;
- use abstract containers such as framework, paradigm, mechanism, or landscape where the exact target, estimator, result, or comparison should appear;
- rotate synonyms for one object;
- use interchangeable significance, robustness, or generality language without naming the evidence and scope;
- repeat one paragraph skeleton across different scientific jobs;
- replace a logical dependency with generic transitions.

Repair the content, not the surface signature. Recover the exact object, relation, evidence, and boundary. Remove metacommentary that contributes no scientific content. Do not add specificity the manuscript does not support, and do not standardize every paragraph into the same cadence.

## Keep implementation language in its proper place

In the main text, describe the statistical construction, information used, returned estimator, governing dimensions, and stated validity conditions.

In an algorithm, name inputs and outputs precisely, but connect them to the statistical objects already defined. Use imperative steps only inside pseudocode or explicit reproduction instructions.

In an appendix or supplement, retain software versions, function arguments, storage choices, hardware, stopping rules, and file organization when needed for reproduction. Do not let these details replace the mathematical description.

When a convention changes the estimator, target, comparison, or reproducibility, state the operation directly. Relevant examples include when a split is made, which observations determine centering or scaling, the loss and penalty normalization, tie-breaking, matrix orientation, and consequential randomization.

## Check tone and claim calibration

Revise language that is:

- promotional, such as "powerful," "seamless," "state-of-the-art," or "unlocks," unless a precise comparison supports it;
- defensive or reviewer-facing, such as "we emphasize that this is not a limitation";
- vague about evidence, such as "works well," "is robust," or "captures uncertainty" without a defined criterion and scope;
- stronger than the result, such as "guarantees" for an empirical pattern or "validates" for an illustrative application;
- weaker than needed because of excessive hedging around a stated identity or theorem.

Use only alternatives supported by the manuscript or author-supplied material: proves, establishes under the stated assumptions, suggests in the reported settings, is consistent with, improves the specified criterion, or remains unresolved. Do not upgrade a statement to **proves** or **establishes** merely because it appears as a theorem or has a proof. For proof prose, load [theoretical-proofs.md](theoretical-proofs.md) rather than inferring whether a proof is complete.

## Typography and final validation

Preserve the manuscript's or stated venue's punctuation and typographic conventions, including supplied U+2013 and U+2014 characters. Correct malformed punctuation, but do not impose the assistant's output house style on manuscript text unless requested.

Compare source and revision for changes in object type, logical direction, scope, evidence level, uncertainty, numerical values, citations, labels, and cross-references. If the supplied format can be compiled or rendered, inspect the affected passage. Otherwise state the validation limit.

As a final pass, ask of every generic or software-oriented noun: who acts, on what statistical object, by what operation, with what evidence, and under what scope? Retain the term only when it is literal, defined, and useful.

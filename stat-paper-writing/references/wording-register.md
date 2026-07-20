# Statistical Wording and Register Audit

## Contents

- [Purpose and register](#purpose)
- [Terminology ledger](#build-a-terminology-ledger)
- [Sentence-level audit](#sentence-level-audit)
- [Software-manual prose](#diagnose-software-manual-prose)
- [Tone and claim calibration](#check-tone-and-claim-calibration)
- [Whole-manuscript validation](#audit-the-full-manuscript)

## Purpose

Use this guide for sentence-level polishing, terminology audits, or whole-manuscript wording revisions. The preferred register is statistical machine learning, mathematics, and the relevant domain science. Preserve legitimate implementation language when the text actually describes code, software, hardware, or reproduction instructions.

The goal is not to make every sentence more formal. The goal is to name each object and claim in the language that best matches its mathematical type, statistical role, and scientific interpretation.

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

## Build a terminology ledger

For a multi-section audit, record:

| Object | Mathematical type | Canonical term | Symbol | Acceptable local variant | Variants to revise |
|---|---|---|---|---|---|

Assign one canonical term to each central object. Permit a local variant only when the section changes the object's role or level, such as population risk versus empirical risk, oracle estimator versus feasible estimator, or scientific outcome versus coded response.

Do not force distinct objects to share one term merely for verbal consistency. Do not give one object several names for stylistic variety.

## Sentence-level audit

For each sentence, apply this sequence:

1. Identify its job: definition, assumption, construction, formal claim, empirical observation, interpretation, limitation, transition, or implementation detail.
2. Identify the type of every central noun: target, data object, distribution, function, estimator, criterion, operator, theorem, numerical approximation, scientific variable, or software object.
3. Check whether the principal verb states the actual relation.
4. Replace any term whose register conflicts with the sentence's job or the object's type.
5. Preserve qualifiers that determine scope, including population, empirical, oracle, feasible, approximate, conditional, and asymptotic.
6. Check the revised sentence against the surrounding notation, claims, and terminology ledger.

If the correct replacement would change the estimand, theorem, algorithm, empirical claim, or scientific interpretation, stop and flag it for author review.

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

These terms are not categorically forbidden. Keep them when they literally describe software, a neural-network architecture, or an established field term. Revise them when they obscure the statistical object or make prose read like user documentation.

## Keep implementation language in its proper place

In the main text, describe the statistical construction, information used, returned estimator, governing dimensions, and conditions under which the procedure is valid.

In an algorithm, name inputs and outputs precisely, but connect them to the statistical objects already defined. Use imperative steps only inside pseudocode or explicit reproduction instructions.

In an appendix or supplement, retain software versions, function arguments, storage choices, hardware, stopping rules, and file organization when needed for reproduction. Do not let these details replace the mathematical description of the procedure.

## Check tone and claim calibration

Revise language that is:

- promotional, such as "powerful," "seamless," "state-of-the-art," or "unlocks," unless a precise comparison supports it;
- defensive or reviewer-facing, such as "we emphasize that this is not a limitation" or "to address a possible concern";
- vague about evidence, such as "works well," "is robust," or "captures uncertainty" without a defined criterion and scope;
- stronger than the result, such as "guarantees" for an empirical pattern or "validates" for an illustrative application;
- weaker than needed because of excessive hedging around a proved identity or theorem.

Use calibrated alternatives: proves, establishes under the stated assumptions, suggests in the reported settings, is consistent with, improves the specified criterion, or remains unresolved.

## Audit the full manuscript

After sentence-level edits, check all occurrences of each canonical term in:

- title, abstract, keywords, and introduction;
- method, algorithms, assumptions, theorems, and proofs;
- simulations, applications, captions, legends, tables, and footnotes;
- discussion, appendices, supplementary files, and notation tables.

Check especially that:

- population, oracle, feasible, empirical, and numerical objects remain distinct;
- a scientific variable is not renamed as a software field or data column in the main argument;
- a finite Monte Carlo benchmark is not called exact truth;
- an empirical diagnostic is not called a theorem-backed guarantee;
- implementation terminology does not migrate into mathematical statements;
- domain interpretation remains conditional on the sampling and identification assumptions;
- terminology changes do not alter labels, citations, numerical values, equations, or cross-references.

## Typography and final validation

Preserve the manuscript's or stated venue's punctuation and typographic conventions consistently. Correct malformed punctuation, but do not impose a private house style unless the user requests it.

When editable source and a suitable toolchain are available, compile or render the affected material and inspect the output. Otherwise inspect the supplied format directly and state the validation limit. Search again for rejected terminology variants. Report any remaining phrase whose correction requires scientific, mathematical, or domain-specific judgment rather than silently guessing.

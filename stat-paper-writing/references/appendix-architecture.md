# Appendix Architecture

## Purpose

Treat appendices and supplements as a navigation and reproduction system. They should extend the main path downward into supporting detail, not sideways into a second narrative.

## Contents

- [Retention and claim mapping](#main-text-retention-test)
- [Top-level organization](#recommended-top-level-order)
- [Proof presentation](#proof-module)
- [Computation and reproduction](#computational-module)
- [Simulations and empirical analyses](#simulation-module)
- [Additional results and extensions](#additional-figures-and-tables)
- [Multi-file supplements](#multi-file-supplements)
- [Cross-reference audit](#cross-reference-audit)

## Main-text retention test

Keep material in the main text when removing it would prevent a careful reader from understanding:

- why the method exists;
- the estimand, target, or exact problem;
- the central representation and described method;
- the statement and meaning of the main result;
- the primary evidence;
- the main failure mode or boundary.

Move material when it mainly supports navigation, detailed checking, or reproduction:

- complete supplied proofs and auxiliary lemmas;
- repeated derivations;
- implementation details and numerical safeguards;
- complete simulation definitions and secondary results;
- data processing, decision logs, and sensitivity records;
- specialized extensions that do not alter the main claim.

Do not use page pressure alone as the criterion. Compress prose and remove duplication before moving conceptual links out of the main text.

## Build a claim-to-support map

Create a table before restructuring:

| Main-text claim | Support type | Main-text content retained | Appendix item | Dependencies |
|---|---|---|---|---|
| Main guarantee | theorem and proof | statement, interpretation, proof idea | proof section | lemmas, notation |
| Computational claim | analysis and benchmark | governing complexity and main comparison | implementation and timing protocol | hardware, stopping rule |
| Robustness claim | sensitivity study | principal perturbation and conclusion | full grid and negative results | data-processing choices |

Every appendix item should support a main-text claim, a later appendix dependency, or a clearly labeled extension. Every main-text claim that relies on omitted details should point to a specific appendix location.

## Recommended top-level order

Use only the modules the paper needs:

1. shared notation and declared dependency map;
2. proofs and technical derivations;
3. algorithms and implementation;
4. simulation and computational details;
5. empirical data processing and sensitivity analyses;
6. additional figures and tables grouped by claim;
7. extensions and exploratory results.

Order proof sections by main-text theorem order unless shared lemmas make a declared dependency-first order clearer.

## Proof module

This module is edited for presentation and documentary consistency only. Do not assess proof validity.

### Opening map

Begin with:

- a list of main results addressed;
- a dependency graph or compact table using manuscript-declared dependencies;
- notation used only in proofs;
- assumptions introduced in technical lemmas.

Example:

| Result | Stated direct dependencies | Stated main device |
|---|---|---|
| Main theorem | Lemmas A.1 and A.3 | decomposition plus concentration |
| Corollary | Main theorem | parameter substitution |
| Boundary result | Lemma A.2 | counterexample or lower bound |

### Lemma placement

Place a lemma immediately before its first declared use when it is local. Group lemmas near the beginning only when several proofs visibly cite them.

Do not create formal lemmas for one-line algebra. Keep method assumptions distinct from proof-only notation and preserve all labels.

### Proof openings

Begin each substantial proof with the manuscript's stated:

1. proof strategy;
2. main decomposition or coupling;
3. dependencies on earlier results;
4. points at which important assumptions enter.

After this roadmap, compact derivations are acceptable. Remove rhetorical shortcuts that replace explanation, but do not invent missing justifications.

### Proof endings

Connect the final displayed statement to the written theorem conclusion. If the proof ending and theorem statement use different rates, scopes, assumptions, or objects, report the visible conflict and leave the mathematical choice to the author.

## Computational module

Include supplied information about:

1. pseudocode inputs, outputs, and returned object;
2. initialization and warm-start rules;
3. stopping criteria and convergence checks;
4. numerical safeguards and failure handling;
5. tuning and default choices;
6. complexity and storage in governing dimensions;
7. parallelization, communication, and hardware assumptions;
8. software versions and reproducibility instructions.

Distinguish conceptual sample size from stored representation size. Distinguish stated theoretical complexity from measured runtime. When screening or approximation can change the returned solution, report the supplied guarantee or empirical check.

## Simulation module

For each simulation family, report:

- estimand and data-generating truth;
- sample size, dimension, and signal regime;
- axis linked to each claim or assumption;
- competitors and stated relevance;
- tuning and information available to each competitor;
- number of replications and uncertainty summaries;
- failure, nonconvergence, and exclusion handling;
- random seeds or reproducible seed protocol;
- exact metric definitions.

Group additional results by claim, not internal experiment number. Include negative results that define the method's reported boundary.

## Empirical and audit module

Include supplied:

1. data provenance and inclusion rules;
2. outcome and predictor construction;
3. missingness, preprocessing, and leakage-prevention procedures;
4. perturbation or sensitivity registry;
5. model and tuning choices;
6. alternative specifications;
7. decision log for analyst judgments;
8. diagnostics and uncertainty checks.

When the paper presents a reliability framework, organize the module so a reader can follow the stated procedure. Use tables that state what changed, why the change is described as reasonable, and how the reported conclusion responded.

## Additional figures and tables

Each item needs:

- a claim-oriented caption;
- the estimand and scale;
- definitions for uncertainty displays;
- a main-text or appendix cross-reference;
- a reason it is secondary rather than primary.

Do not create a gallery of uncurated plots. Consolidate redundant displays and preserve common scales where comparisons matter.

## Extensions module

Separate:

- immediate corollaries described as requiring only substitution;
- methodological extensions described as requiring a new component;
- exploratory ideas without a complete guarantee.

Label the status explicitly. Do not let an exploratory extension broaden the title, abstract, or main contribution claim.

## Multi-file supplements

If the supplement spans several files, use one master outline and one notation source. Keep theorem labels, equation labels, and terminology stable across files.

Use descriptive file roles such as proofs, algorithms, simulations, and data details. Do not repeat the introduction in every file.

## Cross-reference audit

Check both directions:

- every main-text reference resolves to the intended appendix item;
- every appendix theorem or figure is cited or has a stated dependency role;
- numbering follows a predictable scheme;
- appendix notation does not silently redefine main-text symbols;
- proof statements and main-text statements use the same labels, objects, rates, and scopes;
- simulation settings match captions and reported values;
- implementation descriptions agree across formulas, algorithms, and prose.

Do not infer that source code implements the described algorithm. Treat claims about uninspected code behavior as **Unverified dependency**.

Remove orphan items, duplicated narratives, and extensions with no relation to the paper's contract.

## Final reader test

Read the main paper without opening the appendix. The argument should remain understandable and its stated support visible. Then follow each main-text cross-reference into the appendix. The requested detail should be easy to locate without reconstructing the whole manuscript.

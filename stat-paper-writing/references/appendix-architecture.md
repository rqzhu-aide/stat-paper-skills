# Appendix Architecture

## Purpose

Treat appendices and supplements as a verification and reproduction system. They should extend the main path downward into proof and detail, not sideways into a second narrative.

## Contents

- [Retention and claim mapping](#main-text-retention-test)
- [Top-level organization](#recommended-top-level-order)
- [Proofs](#proof-module)
- [Computation and reproduction](#computational-module)
- [Simulations and empirical analyses](#simulation-module)
- [Additional results and extensions](#additional-figures-and-tables)
- [Multi-file supplements and presentation modes](#multi-file-supplements)
- [Cross-reference audit](#cross-reference-audit)

## Main-text retention test

Keep material in the main text when removing it would prevent a careful reader from understanding:

- why the method exists;
- the estimand, target, or exact problem;
- the central representation and implemented method;
- the statement and meaning of the main result;
- the primary evidence;
- the main failure mode or boundary.

Move material when it mainly supports verification or reproduction:

- complete proofs and auxiliary lemmas;
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
| Robustness claim | sensitivity study | principal perturbation and conclusion | full grid and negative results | data processing choices |

Every appendix item must support a main-text claim, a later appendix dependency, or a clearly labeled extension. Every main-text claim that relies on omitted details must point to a specific appendix location.

## Recommended top-level order

Use only the modules the paper needs:

1. shared notation and dependency map;
2. proofs and technical derivations;
3. algorithms and implementation;
4. simulation and computational details;
5. empirical data processing and sensitivity analyses;
6. additional figures and tables grouped by claim;
7. extensions and exploratory results.

Order proof sections by main-text theorem order unless shared lemmas make a dependency-first order substantially clearer.

## Proof module

### Opening map

Begin with:

- a list of main results proved;
- a dependency graph or compact table;
- notation used only in proofs;
- any assumptions introduced solely for technical lemmas.

Example dependency table:

| Result | Direct dependencies | Main device |
|---|---|---|
| Main theorem | Lemmas A.1 and A.3 | decomposition plus concentration |
| Corollary | Main theorem | parameter substitution |
| Boundary result | Lemma A.2 | counterexample or lower bound |

### Lemma placement

Place a lemma immediately before the first proof that uses it when it is local. Group lemmas near the beginning only when several proofs reuse them.

Do not create formal lemmas for one-line algebra. Do not bury method assumptions inside proof-only notation.

### Proof openings

Begin each substantial proof with:

1. the proof strategy;
2. the main decomposition or coupling;
3. dependencies on earlier results;
4. the step at which each important assumption enters.

After this roadmap, compact derivations are acceptable.

### Proof endings

Close by connecting the final bound or identity to the exact theorem conclusion. If the proof reveals a stronger, weaker, or differently scaled statement than the main text suggests, repair the theorem or interpretation.

## Computational module

Include:

1. pseudocode with inputs, outputs, and returned object;
2. initialization and warm-start rules;
3. stopping criteria and convergence checks;
4. numerical safeguards and failure handling;
5. tuning and default choices;
6. complexity and storage in governing dimensions;
7. parallelization, communication, and hardware assumptions;
8. software versions and reproducibility instructions.

Distinguish conceptual sample size from stored representation size. Distinguish theoretical complexity from measured runtime. When screening or approximation can change the solution, state the guarantee or empirical check.

## Simulation module

For each simulation family, record:

- estimand and data-generating truth;
- sample size, dimension, and signal regime;
- axis linked to each claim or assumption;
- competitors and why they are relevant;
- tuning and information available to each competitor;
- number of replications and uncertainty summaries;
- failure, nonconvergence, and exclusion handling;
- random seeds or reproducible seed protocol;
- exact metric definitions.

Group additional results by claim, not by internal experiment number. Include negative results that define the method's boundary.

## Empirical and audit module

Include:

1. data provenance and inclusion rules;
2. outcome and predictor construction;
3. missingness, preprocessing, and leakage prevention;
4. perturbation or sensitivity registry;
5. complete model and tuning choices;
6. alternative specifications;
7. decision log for analyst judgments;
8. additional diagnostics and uncertainty checks.

When the paper proposes a reliability framework, this module should make the framework executable. Use tables that state what changed, why the change is reasonable, and how the conclusion responded.

## Additional figures and tables

Each item needs:

- a claim-oriented caption;
- the estimand and scale;
- definitions for uncertainty displays;
- a main-text or appendix cross-reference;
- a reason it is secondary rather than primary.

Do not create a gallery of uncurated plots. Consolidate redundant displays and preserve common scales where comparisons matter.

## Extensions module

Separate three types:

- immediate corollaries requiring only substitution;
- methodological extensions requiring a new component;
- exploratory ideas without a complete guarantee.

Label the status explicitly. Do not let an exploratory extension broaden the title, abstract, or main contribution claim.

## Multi-file supplements

If the supplement spans several files, use one master outline and one notation source. Keep theorem labels, equation labels, and terminology stable across files.

Use descriptive file roles such as proofs, algorithms, simulations, and data details. Do not repeat the introduction in every file.

## Apply presentation modes by module only when needed

Do not assign one mode to the entire supplement. Consult [style-modes.md](style-modes.md) only for a module with a genuine presentation problem, then choose the smallest suitable repair:

- use **compact and direct** for routine derivations, implementation inventories, and reproducibility details;
- use **explanatory and intuition-led** for a mechanism-level roadmap before a proof device or algorithm that is difficult to understand from formal steps alone;
- use **formal and structure-led** for proof dependencies, assumptions, scopes, and exact algorithm contracts;
- use **evidence-led and comparative** for sensitivity analyses, additional simulations, timing studies, and secondary empirical results.

Do not record a mode for routine or already clear modules. When a mode is used, keep it stable within the affected module and use another only where it solves a distinct local reader problem.

## Cross-reference audit

Check both directions:

- every main-text reference resolves to the intended appendix item;
- every appendix theorem or figure is cited or has a stated dependency role;
- numbering follows a predictable scheme;
- appendix notation does not silently redefine main-text symbols;
- proof statements match main-text statements exactly;
- simulation settings match captions and reported values;
- implementation details describe the code that generated the reported results.

Remove orphan items, duplicated narratives, and extensions with no relation to the paper's contract.

## Final reader test

Read the main paper without opening the appendix. The argument should remain understandable and credible. Then read the appendix from each main-text cross-reference. The requested verification detail should be easy to locate without reconstructing the whole manuscript.

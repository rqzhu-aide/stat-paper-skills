# Statistical Wording and Register

## Purpose

Use for terminology, evidence verbs, tone, and disciplinary register. Preserve literal implementation language where software or reproduction is the subject.

Match wording to mathematical type, statistical role, and scientific interpretation without merely increasing formality. For manuscript-wide normalization or conventional names, use [terminology-audit.md](terminology-audit.md). For difficult specialist rewriting or a high-risk claim edit, consult [polishing-examples.md](polishing-examples.md).

## Establish the register

Choose terms for the work they do in the passage.

- **Specialist term or unnecessary label:** retain nuisance function, oracle estimator, or neural-network layer when the distinction matters. Explain unfamiliar objects by definition and role. A new "bridge" or "engine" adds little when the relation can be stated directly. Preserve supplied contribution names without using them instead of explanation.
- **Statistical conclusion or proof operation:** replacement, coupling, and linearization can name proof steps precisely. Around a main result, explain which distributions are approximated, which covariance estimator is consistent, or which error is negligible, with the relevant norm, regime, and conditioning. A proof label alone does not supply that conclusion.
- **Relation or metaphor:** prefer the actual relation, such as bounds, minimizes, converges to, or depends on. Retain conventional metaphors when clear. Follow [support-and-author-decisions.md](support-and-author-decisions.md) when an interpretation would add scientific content.
- **Domain meaning:** name the population, variables, design, scientific quantity, and uncertainty in the application field's vocabulary. Keep statistical, computational, and empirical interpretations distinct.

These choices depend on the paper and passage. They do not prescribe an algorithm-first order or a list of banned phrases.

## Targeted disciplinary calibration

Calibrate explanation to research readers: what is established, why direct reuse does not cover this setting, which supplied insight addresses the obstacle, and what changes. Keep needed definitions; skip unnecessary explanation of familiar identities. An identity can still expose the central difficulty.

Use supplied or verified comparisons first. When a consequential register or comparison question remains, inspect only the relevant passages in one or two related papers, including recent work that changes the comparison. Retain source locations and reuse the notes across sections. Routine local edits need no search. If relevant passages are inaccessible, make a conservative choice and note uncertainty only where consequential. Do not invent an advance, import unsupported claims, copy prose, imitate authors, or impose a repeated paragraph template.

## Check agency and property ownership

Natural wording must preserve who acts and which object has a statistical property.

- Attribute bias, variance, consistency, and sampling instability to the estimator, sequence, procedure, or law with that property; attribute realized error to the estimate. Distinguish both from the estimand, which may be random or data-adaptive under the stated conditioning.
- Specify sampling, algorithmic, or Monte Carlo randomness when ambiguous. Preserve what is conditioned on or held fixed.
- Name the procedure or analyst that fits, selects, tunes, or constructs an object; data do not act by themselves.
- Name the scientific object rather than treating storage, printing, display, or repository status as a statistical property.
- A simulated true parameter or oracle value is known from the data-generating mechanism; do not extend that status to real-data analysis.

Conventional shorthand such as "the data suggest" or "the model predicts" may remain when the agency and statistical meaning are unambiguous.

## Diagnose software-manual prose

Ask what the words denote before replacing them:

| Warning sign | Contextual decision |
|---|---|
| pipeline, module, interface, or layer | Retain literal software architecture or neural-network terminology. For statistical objects, name the procedure, estimator, transformation, or model term. |
| input, output, feed, or pass | Identify the data, estimates, predictions, or returned software objects and the operation relating them. |
| instantiate, configure, enable, or run | State the operation, such as define, select, fit, or compute, unless software execution is the subject. |
| ground truth | Distinguish exact or simulated truth, oracle values, estimated references, and numerical or Monte Carlo benchmarks. |
| generalization metric | Name the population or held-out criterion: risk, prediction error, calibration error, or another exact metric. |
| fixture, checked reference, stored result, or printed coefficient | Name the data, benchmark, estimate, or validation calculation. Retain storage or repository status only when relevant. |
| algorithm or fitting contract | State the definition, fitting steps, formula, or convention directly unless a software contract is meant. |
| population-standardize | State the centering and scaling formula and where its quantities are estimated. |

Retain literal software descriptions, API names, and established field terms, including in software papers, reproduction appendices, and deployment studies.

## Keep implementation language in its proper place

Connect algorithm inputs and outputs to the statistical construction, information used, returned estimator, governing dimensions, and stated validity conditions. Reserve imperative steps for pseudocode or explicit reproduction instructions.

Keep implementation choices affecting the estimator or interpretation visible where needed. Place software versions, function arguments, storage, hardware, and file organization according to their importance and venue requirements, often in the supplement. They do not replace the mathematical description.

State conventions affecting the estimator, target, comparison, or reproducibility directly: split timing, observations used for centering or scaling, loss and penalty normalization, tie-breaking, matrix orientation, and consequential randomization.

## Check tone and claim calibration

Replace promotional or vague claims such as "powerful," "works well," "is robust," and "captures uncertainty" with their supplied object, criterion, evidence, and boundary. Do not invent specificity. Remove defensive reviewer-facing commentary. Avoid both "guarantees" for an empirical pattern and needless hedging around a stated identity. Evidence-level choices follow [polishing-protocol.md](polishing-protocol.md); proof prose also uses [theoretical-proofs.md](theoretical-proofs.md).

Write in the paper's authorial voice. "The supplied studies" or "the source files report" describes editing; identify the actual studies and evidence instead. Keep unresolved provenance in an author note and wherever it limits a manuscript claim. Inspect retained preambles and labels around protected displays too: preserving mathematics does not freeze its explanation.

## Mathematics and citations in prose

Keep short, routine expressions inline when readable. Display central definitions, relations needing visual inspection, and long expressions that would obstruct a sentence. Number equations needed for reference or required by the venue; retain supplied labels and references during revision. Introduce notation when it earns its cost through precision or reuse. Explain a derivation's decisive steps without displaying every elementary manipulation or paraphrasing every line. Give displays prominence in proportion to their role in the argument.

Place a citation beside the claim or clause it supports, especially when a sentence combines prior work with the present contribution. Use narrative attribution when an author's contribution is the subject and parenthetical attribution when the statistical claim is the subject, following the venue's citation system. Avoid a paragraph-end citation whose scope is unclear.

Citation density should follow intellectual dependence. Related-work synthesis may need several sources; a new derivation may need none. Attribute borrowed definitions, results, procedures, comparator implementations, data, and external interpretations at their substantive use, with renewed attribution after substantial separation when needed for clarity. Avoid both missing credit and repetitive citations for an already clear attribution. Use verified or supplied sources only; do not invent references to meet a frequency target.

## Typography

Preserve the manuscript's or stated venue's punctuation and typographic conventions, including supplied U+2013 and U+2014 characters. Correct malformed punctuation, but do not impose the assistant's output house style on manuscript text unless requested.

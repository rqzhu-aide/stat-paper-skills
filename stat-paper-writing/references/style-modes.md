# Generic Presentation Modes

## Purpose

Use a presentation mode only for an affected section with a genuine problem of information order, emphasis, or explanatory depth. After identifying that section's job, choose from the current draft, audience, topic familiarity, technical depth, venue constraints, and type of support. Do not imitate a named author or paper.

Different sections may use different modes. A manuscript may need an explanatory introduction, a compact method section, formal theorem statements, and evidence-led experiments. Route by subsection when a long section contains distinct reader-facing jobs.

These modes control information order, emphasis, and explanatory depth. They are not authorial personas or replacements for the manuscript's established voice.

## Contents

- [Selection and tie-breaking](#selection-table)
- [Compact and direct](#compact-and-direct)
- [Explanatory and intuition-led](#explanatory-and-intuition-led)
- [Formal and structure-led](#formal-and-structure-led)
- [Evidence-led and comparative](#evidence-led-and-comparative)
- [Combining and validating modes](#combining-modes)

## Selection table

| Mode | Prefer when | Current-draft signal | Main control |
|---|---|---|---|
| Compact and direct | The topic and notation are familiar, the contribution is narrow, or space is tight | Repetition, long setup, multiple summaries, delayed contribution | Remove detours and state each paragraph's job early |
| Explanatory and intuition-led | The structural idea is unfamiliar, the conceptual jump is large, or readers work outside the narrow subfield | Formula-first prose, unexplained mechanism, theorem-first exposition | Expose the mechanism before dense formalization |
| Formal and structure-led | The contribution is theorem-heavy, identification-sensitive, or logically deep | Ambiguous assumptions, mixed oracle and feasible objects, unclear dependencies | Make definitions, scopes, assumptions, and result dependencies explicit |
| Evidence-led and comparative | The central claims depend on simulations, computation, applications, or contrasts | Method catalogues, unsupported performance claims, result-by-result narration | Organize around claims, comparisons, and observable consequences |

## Selection questions

For each target section, ask:

1. What must the reader understand or believe by the end of this section?
2. Is the main obstacle verbosity, conceptual unfamiliarity, logical ambiguity, or weak connection to evidence?
3. How familiar is the intended research reader with the subfield, mechanism, and notation?
4. Is the contribution carried mainly by a construction, theorem, proof mechanism, or empirical result?
5. How much depth and space does the venue permit?

Choose the mode that fixes the dominant reader problem. Do not choose the most elaborate mode by default.

### Tie-breaking

When several modes appear useful, use this priority:

1. Resolve ambiguity about the target, assumptions, scope, or mathematical claim.
2. Repair missing conceptual understanding.
3. Connect claims to adequate evidence.
4. Compress only after the necessary logic and support are present.

This priority determines what to repair first, not the permanent mode of the section.

## Compact and direct

### Use

Use for expert audiences, mature problems, narrow technical advances, short papers, or drafts that already contain enough explanation but lack economy.

### Paragraph pattern

1. State the controlling claim or question.
2. Give the minimum support needed.
3. State the consequence or transition.

### Language

- Prefer concrete verbs and stable terminology.
- Remove repeated motivation and method recaps.
- Keep one purpose per paragraph.
- Introduce only notation used soon afterward.
- Interpret equations briefly but specifically.

### Risk

Do not confuse brevity with omission. Retain the estimand, the key reason for the construction, assumption roles, and the principal boundary.

## Explanatory and intuition-led

### Use

Use when statistically trained readers need the structural mechanism before dense notation, when the method combines ideas from different subfields, or when the draft asks readers to manipulate objects before understanding what creates the result.

### Calibrate the level

Assume graduate-level statistical maturity unless the manuscript specifies another audience. Explain the paper-specific difficulty, not standard background that the intended reader already knows.

Choose an example or intuition that preserves the mechanism being explained. Prefer, in order:

1. a limiting or boundary regime in which the key term becomes visible;
2. two nearby regimes that differ in one assumption, dependence path, or information constraint;
3. an error, risk, likelihood, or objective decomposition that identifies the operative term;
4. a geometric, optimization, probabilistic, or information-flow interpretation;
5. a small numerical illustration only when scale, sign, or threshold behavior is the point.

Do not use a toy example that removes the dependence, identifiability, high-dimensional, adaptive, or computational feature responsible for the difficulty.

### Paragraph pattern

1. State the precise structural tension or research question.
2. Isolate the operative mechanism with a diagnostic regime, contrast, or decomposition.
3. Explain what changes, which term changes, and why.
4. Introduce the formal object as the exact expression of that mechanism.
5. Interpret the resulting claim and mark where the intuition stops being exact.

### Language

- State the conceptual role before dense notation without re-teaching standard definitions.
- Use one diagnostic example only when it retains the paper's central difficulty.
- Explain transformations through invariance, information flow, geometry, or the error term they control.
- Separate exact statements from heuristics.
- Prefer mathematical or statistical intuition to everyday analogy. Use an analogy only when its mapping and failure point are explicit.

### Risk

Do not lower the technical level, over-explain standard facts, or replace a nontrivial mechanism with a classroom example. Stop once the reader can anticipate the formal construction and understand what the formalism must resolve.

## Formal and structure-led

### Use

Use when correctness depends on careful scopes, conditioning, identification, theorem chains, or distinctions among population, oracle, feasible, asymptotic, and computational objects.

### Paragraph pattern

1. State the formal question.
2. Define the objects and regime.
3. Group assumptions by role.
4. State the result.
5. Explain its dependency and boundary.

### Language

- Keep notation local where possible.
- State quantifiers, conditioning, and convergence modes.
- Separate method assumptions from proof-only conditions.
- Use explicit dependency transitions.
- Distinguish necessary, sufficient, and convenient conditions.

### Risk

Do not make formalism the first explanation of an unfamiliar idea. Add a short preflight explanation when the theorem's purpose is not already evident.

## Evidence-led and comparative

### Use

Use when the manuscript's contribution is judged through accuracy, robustness, calibration, computation, diagnostic value, or a changed scientific conclusion.

### Paragraph pattern

1. State the claim or comparison question.
2. Define the evidence needed to answer it.
3. Report the main pattern and magnitude.
4. Connect it to the method or theory.
5. State the exception, uncertainty, or limit.

### Language

- Name the estimand, metric, and comparison basis.
- Separate observations from explanations.
- Compare methods around questions, not one method at a time.
- Report uncertainty and relevant scales.
- Tie every table or figure to one primary claim.

### Risk

Do not let empirical organization replace method explanation. The reader must still know what changed and why the comparison is fair.

## Combining modes

Choose one primary mode per section. Use a secondary mode only for a local need, such as:

- a compact section with one explanatory paragraph before a new construction;
- a formal theorem statement followed by an intuitive interpretation;
- an evidence-led experiment section with compact implementation details.

Do not blend all modes uniformly or alternate modes for stylistic variety. The purpose of routing is to choose what the section most needs.

## Style validation

After drafting, check:

- Does the chosen mode address the section's main reader difficulty?
- Is the scientific claim unchanged by the presentation choice?
- Is the section consistent with surrounding notation and voice?
- Has the mode introduced unnecessary length or removed necessary support?
- Could a different mode make the same content clearer with less effort?

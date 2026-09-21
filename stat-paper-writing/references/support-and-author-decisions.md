# Supplied Support and Author Decisions

Use when a revision depends on incomplete support, conflicting artifacts, or a scientific choice. This guide owns the detailed editing boundary; it does not validate mathematics, sources, code, results, or novelty.

## Decide what can be edited

| Situation | Action |
|---|---|
| Equivalent supported wording or an editorial change within the requested scope | Edit directly. Structural revision includes reversible ordering of supplied material; preserve explicit author priorities. |
| An explicitly authorized substantive correction with a uniquely supported replacement | Apply that correction and disclose the scientific change. Do not expand the authority or invent a replacement. |
| Conflicting scientific representations, unsupported interpretation, or competing author intentions affecting the claim | Identify the unresolved choice, ask the specific question needed, and continue independent work. |

For substantive claims, identify the supporting note, definition, formal statement, figure, result, application fact, or source excerpt. A new explanation or elementary algebraic restatement is supported when its equivalence is checkable from supplied definitions and conditions, with the same regime, quantifiers, and conditioning. Check that equivalence; unfamiliar wording alone does not require approval. A new argument, assumption, mechanism, or guarantee requires further support.

Draft the supported portion when possible. List material missing inputs separately under **Author information needed**, outside clean manuscript prose. Ask before drafting only when nothing supported can be written. Missing implementation details are material when they determine the estimator, interpretation, or reproducibility at the requested level. A conceptual method draft need not request every software detail.

## Conflicting representations and object roles

A documentary conflict does not identify which representation is authoritative. Do not prefer a formula, theorem, algorithm, caption, or earlier passage merely because it is more formal, detailed, conventional, or prominent. Preserve consistent material and isolate the exact conflict for the author. Conditional alternatives can explain the choice but are not completed manuscript prose.

A definition establishes an object's name, type, and construction, not which object was fitted, computed, evaluated, returned, plotted, or reported. If a role label conflicts with definitions, name the competing symbols and construction details and ask which object performed the operation. Oracle or feasible labels, true nuisance quantities, cross-fitting, and surrounding convention cannot resolve empirical use.

Do not remove a substantive relation merely because another representation omits it. After an authorized correction, disclose the changed relation and its documentary basis; omission alone does not show that the relation is false.

## Unsupported claims and missing assumptions

An editor-proposed condition is not an author-supplied assumption. Do not insert it into clean prose, even as an if-clause. For unsupported identification or causal claims, ask for the supplied conditions and corresponding result, rather than directing the author to adopt an assumption.

Do not silently weaken, delete, or present an unsupported scientific claim as manuscript-ready. If the user explicitly authorizes a substantive correction and the supplied material uniquely determines a narrower claim, apply it under the decision rule above. Otherwise ask what support or intended interpretation should govern. A general polishing request does not authorize changing causal or identification status, the target, a formal conclusion, or a numerical finding.

An explicitly unsupported promotional or evidentiary qualifier can be removed in a bounded polish when the remaining sentence is complete and supported and no scientific object, conclusion, or procedure changes. Disclose the removal. Distinguish this from erasing a substantive claim because its support is missing.

Preserve the force of supplied relations. Do not turn:

- an object that permits a later statement into proof or a guarantee of that statement;
- equal emphasis into equal weighting;
- no stated dependency into independence;
- association into causation;
- a finite reported pattern into general robustness;
- a defined object into evidence of its empirical use.

A purpose sentence before a definition, display, or algorithm must respect these distinctions.

## Citation scope and construction-to-theorem links

When a supplied source excerpt supports a narrower claim and the user requests citation consistency, retain the exact citation key, supported object and scope, and convergence mode or distributional conclusion. Disclose substantive narrowing. Distinguish supplied excerpts from independently checked sources when relevant. If no unique supported replacement exists, ask whether the author intends to supply support or revise the claim.

When prose says that a split, fold, held-out construction, cross-fit, or aggregation is why a theorem applies, require a supplied statement supporting that link. If absent, separate the unsupported link from any safe local edit. Name the construction and theorem and ask what stated relation connects them; do not invent an independence or applicability argument.

## Communicate unresolved decisions

Distinguish observed manuscript evidence, inferred reader consequences, and **Unverified dependency** when resolution requires missing context, source work, mathematical validation, code behavior, or an author choice. An unverified dependency is not an established error. Ordinary polishing needs no field labels; audit reporting follows [reporting-and-validation.md](reporting-and-validation.md).

Keep the unresolved span out of completed replacement prose. Name the object or relation and ask a self-contained question specifying the choice, without padding or repeating general scope disclaimers. State when no safe completed repair is available, while retaining supported edits elsewhere. Do not follow that statement with a purported clean repair of the same unresolved span.

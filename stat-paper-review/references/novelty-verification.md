# Publication-Backed Novelty Verification

## Contents

- [Claim decomposition](#1-decompose-the-claim)
- [Comparison set](#2-build-a-verified-comparison-set)
- [Substantive comparison](#3-compare-the-contributions)
- [Conclusion](#4-report-a-bounded-conclusion)

## 1. Decompose the claim

Extract each novelty claim in the requested assessment scope; a full review covers the abstract, introduction, related work, method, and theory. Decompose it into:

- target or scientific question;
- data, information, and statistical regime;
- construction, estimator, representation, or algorithm;
- identifying and regularity assumptions;
- guarantee or formal conclusion;
- computational property;
- empirical or application scope.

Do not search only the proposed method name. New terminology may hide an established idea, while similar terminology may refer to a different target.

## 2. Build a verified comparison set

Follow [academic-search-operations.md](academic-search-operations.md) for citation resolution, multi-source search, record verification, version linking, evidence limits, and stopping rules. For actual novelty, priority, or related-work comparison, start with the manuscript's claim-bearing citations in scope, then search for uncited close work. A precise named-source support question does not itself require contribution-wide decomposition or uncited-work discovery.

Keep these questions separate:

1. Does the cited or discovered publication exist with the reported metadata?
2. Does its content support the statement attached to it?
3. How closely does it overlap with the manuscript's claimed contribution?

Use full text when the distinction depends on assumptions, theorem scope, algorithm details, or empirical design. Do not use search snippets or citation counts as evidence of conceptual closeness.

## 3. Compare the contributions

Use a compact matrix for the manuscript and the closest verified publications:

| Work | Status and date | Target/regime | Main construction | Assumptions | Guarantee | Evidence/application | Overlap and distinction | Cited? |
|---|---|---|---|---|---|---|---|---|

Compare the intellectual contribution rather than surface vocabulary. Report separate, nonexclusive fields:

- **Evidence coverage:** decisive full text inspected, abstract-limited, metadata-only, or not assessed.
- **Overlap status:** distinction supported relative to the verified comparison set; narrower than claimed; anticipated by cited work; challenged by uncited close work; or indeterminate.
- **Contribution form:** new target, construction, guarantee, evidence, application, combination, implementation, proof, extension, or interpretation.
- **Citation status:** cited and distinguished fairly; cited but distinguished inadequately; found independently and uncited; or not assessable.

### Practical usefulness relative to existing alternatives

Assess what a researcher or practitioner gains compared with methods already available for the same question. Include simpler established procedures and alternatives from different method families, not only the closest technical ancestor. Reuse the comparison above; no second table or exhaustive benchmark list is required.

- Do existing methods already deliver a similar or identical scientific conclusion, inferential statement, prediction, or decision in the intended setting? Compare the target, available information, assumptions, uncertainty or guarantee, and relevant operating conditions. Agreement of point estimates or significance on one dataset does not establish equivalence.
- What supported benefit remains: better precision or calibration, robustness, weaker assumptions, less data, lower computational or tuning burden, easier implementation, clearer interpretation, or a previously inaccessible setting? Assess the size and relevance of the gain as well as its costs; different machinery alone is not a benefit.
- If an existing feasible method already provides essentially the same answer under comparable conditions and no meaningful additional benefit is demonstrated, say that the practical contribution is limited or not established. Distinguish evidence of practical overlap from a missing comparison, and identify the alternative and evidence rather than dismissing the work as merely similar.
- Keep intellectual contribution and practical benefit separate. A new proof, representation, or guarantee can be valuable even when current practical conclusions remain unchanged; conversely, a theoretically familiar method can offer substantial practical value. For a theoretical paper, assess its stated purpose and label prospective usefulness as prospective rather than requiring immediate empirical superiority.

Report the resulting practical judgment alongside the novelty conclusion when relevant, explaining whether users gain a new answer or a better way to obtain an existing answer. Base the comparison on supplied or verified method content and relevant numerical or analytical evidence. If decisive comparison evidence is unavailable, state that limit rather than infer either practical equivalence or superiority. Request additional comparisons only when needed to support the paper's actual claim.

### The combination test

First distinguish a new primitive from a combination. Use **new primitive** only when the central target, construction, or guarantee is not reducible to an assembly of components in the verified comparison set, and the verified comparison supports that specific distinction. Do not use **new primitive** for a contribution already classified as a combination, and do not infer it from new terminology.

When the contribution form is a combination of established components, do not stop at the label. Determine:

1. **Capability:** does the combination deliver a target, guarantee, or application that no publication in the verified comparison set achieves or approximates? Name the closest approximation and what it misses.
2. **Nontrivial development:** did making the combination work require a new identification argument, a new analysis, or a non-obvious algorithmic or theoretical step, or does it follow directly from the components in their published forms?
3. **Classification:** when the evidence supports classification, conclude with either `enabling combination`, meaning a new capability or nontrivial development supported by the comparison set, or `convenience assembly`, meaning components joined as published with the capability already approximated by existing methods. Otherwise leave the classification unassessed and identify the missing decisive comparison or argument.

State the supported classification and its basis, or the unassessed status, in the novelty conclusion; an unresolved distinction that could reverse novelty requires a novelty score of `N/A`. Assess practical usefulness separately using the comparison above: an enabling combination need not improve current practice, and a convenience assembly can still reduce cost or effort. Neither classification alone settles practical value.

When no closer publication is identified, say:

> No closer work was identified within the documented search boundary.

Do not translate this result into proof that the paper is first, unique, or globally novel. Prefer a precise narrower claim over unsupported "first," "unique," or "no existing method" language.

## 4. Report a bounded conclusion

Report the exact claim assessed, manuscript citations verified, closest external publications, substantive comparison, evidence-coverage level, sources and query concepts, search date, access limits, and calibrated conclusion. Give every decisive publication's verified DOI, PMID, arXiv ID, or direct official link. When external verification is unavailable or excluded, classify supplied items as packet-only comparators rather than verified decisive publications and retain their supplied identifiers with an explicit `not independently verified` label. Inspected supplied content may support a packet-bounded overlap or practical-usefulness assessment, but not independently verified field-level novelty or priority. Without the required external verification and search, mark field-level novelty unassessed and its score `N/A`; without substantive comparator content, assess positioning clarity only. State citation status explicitly. Use `cited by the manuscript`, `found independently and uncited` for independently discovered work, or `supplied in the packet and uncited` for an uncited packet-only comparator; do not leave the status implicit.

Keep verification status separate from discovery and citation status. If a packet says that a work was found independently and is uncited, preserve `found independently and uncited` even when the reviewer cannot independently verify the record. Do not reclassify its discovery channel merely because the record was relayed in an offline packet.

For each decisive comparator, expose both axes as explicit fields: `Verification status:` and `Discovery/citation status:`. Do not let chronology or the word `uncited` stand in for the supplied discovery status.

Keep first-reader and literature judgments separate. The sequential pass asks whether the manuscript makes its novelty case clearly when encountered. The search pass asks whether that case survives comparison with real publications.

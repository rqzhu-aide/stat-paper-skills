# Publication-Backed Novelty Verification

## Contents

- [Claim decomposition](#1-decompose-the-claim)
- [Comparison set](#2-build-a-verified-comparison-set)
- [Substantive comparison](#3-compare-the-contributions)
- [Conclusion](#4-report-a-bounded-conclusion)

## 1. Decompose the claim

Extract each central novelty claim from the abstract, introduction, related work, method, and theory. Decompose it into:

- target or scientific question;
- data, information, and statistical regime;
- construction, estimator, representation, or algorithm;
- identifying and regularity assumptions;
- guarantee or formal conclusion;
- computational property;
- empirical or application scope.

Do not search only the proposed method name. New terminology may hide an established idea, while similar terminology may refer to a different target.

## 2. Build a verified comparison set

Follow [academic-search-operations.md](academic-search-operations.md) for citation resolution, multi-source search, record verification, version linking, evidence limits, and stopping rules. Start with the manuscript's small set of claim-bearing citations, then search for uncited close work.

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

When no closer publication is identified, say:

> No closer work was identified within the documented search boundary.

Do not translate this result into proof that the paper is first, unique, or globally novel. Prefer a precise narrower claim over unsupported "first," "unique," or "no existing method" language.

## 4. Report a bounded conclusion

Report the exact claim assessed, manuscript citations verified, closest external publications, substantive comparison, evidence-coverage level, sources and query concepts, search date, access limits, and calibrated conclusion. Give every decisive publication's verified DOI, PMID, arXiv ID, or direct official link. When external verification is unavailable or excluded, classify supplied items as packet-only comparators rather than verified decisive publications, retain their supplied identifiers with an explicit `not independently verified` label, and keep substantive novelty provisional or unassessed within the packet boundary. State citation status explicitly. Use `cited by the manuscript`, `found independently and uncited` for independently discovered work, or `supplied in the packet and uncited` for an uncited packet-only comparator; do not leave the status implicit.

Keep verification status separate from discovery and citation status. If a packet says that a work was found independently and is uncited, preserve `found independently and uncited` even when the reviewer cannot independently verify the record. Do not reclassify its discovery channel merely because the record was relayed in an offline packet.

For each decisive comparator, expose both axes as explicit fields: `Verification status:` and `Discovery/citation status:`. Do not let chronology or the word `uncited` stand in for the supplied discovery status.

Keep first-reader and literature judgments separate. The sequential pass asks whether the manuscript makes its novelty case clearly when encountered. The search pass asks whether that case survives comparison with real publications.

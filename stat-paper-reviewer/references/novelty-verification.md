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

Compare the intellectual contribution rather than surface vocabulary. Determine whether the manuscript's contribution is:

- supported as stated;
- real but narrower than stated;
- primarily a new combination, implementation, proof, extension, or interpretation;
- anticipated by cited work;
- challenged by an uncited close publication;
- not assessable from available evidence.

Prefer a precise narrower claim over unsupported "first," "unique," or "no existing method" language.

## 4. Report a bounded conclusion

Report the exact claim assessed, manuscript citations verified, closest external publications, substantive comparison, whether decisive publications were cited, sources and query concepts, search date, access limits, and calibrated conclusion.

Keep first-reader and literature judgments separate. The sequential pass asks whether the manuscript makes its novelty case clearly when encountered. The search pass asks whether that case survives comparison with real publications.

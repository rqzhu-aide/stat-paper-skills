# Reviewer Scores

## Purpose

Treat each score as an ordinal reviewer judgment, not a measurement, acceptance probability, or substitute for the evidence-based diagnosis.

Every full or pre-submission review ends with the default category scorecard below. Score additional dimensions, alternative scales, or venue rubrics only when the user requests them.

A defined rubric supplied by the user or a named venue governs the additional rubric-specific table and any rubric-specific overall score; it does not replace the default scorecard in a full or pre-submission review. Keep the tables separate when their dimensions or scales differ, and do not blend, average, or silently translate their scores. For a focused review that is not full or pre-submission, use only the requested rubric and the relevant dimensions. A defined rubric specifies dimensions and scale anchors and, for an overall score, weights or a decision rule. A request for decimals, missing-as-zero treatment, or a simple average is an output preference, not a defined rubric, and cannot override the evidence safeguards below.

For a named venue, verify that the criteria are current and official, record the source and access date, and preserve the venue's scale and anchors. If those criteria cannot be verified, do not assign a venue-fit score; provide a qualitative general fit assessment instead.

## Default category scorecard

Score these four categories on the 1-10 scale below, assigning an integer only when assessable and `N/A` otherwise:

| Category | Question | Evidence base |
|---|---|---|
| Novelty | Does the claimed contribution survive the combination test and the documented external comparison? | [novelty-verification.md](novelty-verification.md) |
| Theory | Do the assumptions, formal results, plausibility screen, and interpretation align with the claims? | [review-framework.md](review-framework.md) sections 2 and 3 |
| Computation and evidence | Is the method computationally correct and practical, and do the experiments support the claims against suitable alternatives in representative settings? | [review-framework.md](review-framework.md) sections 2 and 4 |
| Writing and presentation | Can a critical reader recover the claim chain, and is the manuscript professionally edited? | [review-framework.md](review-framework.md) section 5 and [ai-writing-alarm.md](ai-writing-alarm.md) |

Scoring the novelty category requires the external comparison in [novelty-verification.md](novelty-verification.md); perform it whenever a search route in [academic-search-operations.md](academic-search-operations.md) is available. When no external search was possible, mark novelty `N/A`, comment only on positioning clarity, and state why.

When the user requests finer or additional dimensions, report them the same way and keep them consistent with their parent category: contribution identity and literature-supported novelty belong to novelty; statistical validity and method-theory coherence to theory; evidence, reproducibility, and computational practicality to computation and evidence; reviewer readability and patterned prose to writing and presentation. Interpretation and relevance, broad significance, and venue fit are separate optional dimensions scored only on request.

## Default scale

Use integer scores only, anchored in bands:

- **1-2:** not established or centrally deficient;
- **3-4:** weak, with major unresolved gaps;
- **5-6:** plausible but mixed, requiring substantial revision;
- **7-8:** strong, with bounded concerns;
- **9-10:** compelling and well supported in the reviewed scope.

Within a band, use the lower number when the limiting issue sits closer to the band below and the higher number otherwise. Do not use decimals. Missing material in a partial review is `N/A`, never zero or automatically a low score.

When the user requests a numeric scale from (a) to (b) without supplying anchors, first assign the supported default score (sin{1,ldots,10}), then map it by
[
t=a+rac{s-1}{9}(b-a).
]
State the mapping and rounding rule once, round only the final mapped value to the precision supported by the requested scale, and preserve `N/A` as `N/A`. Do not use this conversion for a supplied or verified rubric that already defines its own anchors.

## Evidence and consistency

For every scored category or dimension, report:

- score;
- support status: established, partially supported, challenged, not established, or unassessed;
- one concise manuscript-specific justification;
- the principal limiting issue or missing verification.

For novelty, also report the contribution form, the combination-test classification when the contribution is a combination, the search-coverage level, and whether the conclusion is bounded or provisional. Never assign a positive novelty score solely from the manuscript's own positioning.

Check scores against the findings:

- an unresolved Critical finding caps every category it directly affects at 4;
- an unresolved Major finding caps its category at 7 unless the scope distinction is explicit;
- `N/A` must not be converted to zero for aggregation;
- broad interest, presentation, or novelty cannot compensate for an unestablished technical case.

## Overall judgment

Do not calculate an arithmetic mean by default. Use the qualitative readiness categories in [report-formats.md](report-formats.md) for the overall judgment.

Provide an overall numerical score only when a supplied or verified rubric defines its scale and aggregation or decision rule. A request for a simple average alone does not provide a defensible rule. Otherwise use a qualitative readiness category and explain why no aggregate is reported. Never let an aggregate conceal a Critical validity or central-claim failure.

## Output

Place the scorecard immediately after the overall assessment. State once, directly above the table, that scores are integers on the 1-10 scale and that `N/A` marks unassessable material rather than deficiency:

| Category | Score | Support status | Brief basis | Limiting issue |
|---|---:|---|---|---|

Follow the table with a one-or-two-sentence verdict per category, then a short qualitative synthesis rather than a restatement of every finding. For a focused review, show only the categories or dimensions relevant to the request.

When an additional user-supplied or venue rubric is requested in a full or pre-submission review, place its separate table after the default category verdicts. Label its source, scale, and aggregation rule, and state any mapping used for overlapping dimensions.

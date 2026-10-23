# Reviewer Scores

## Purpose

Treat each score as an ordinal reviewer judgment, not a measurement, acceptance probability, or substitute for the evidence-based diagnosis.

Every full or pre-submission review includes the default category scorecard below. Score additional dimensions, alternative scales, or venue rubrics only when the user requests them.

A defined rubric supplied by the user or a named venue governs the additional rubric-specific table and any rubric-specific overall score; it does not replace the default scorecard in a full or pre-submission review. Keep the tables separate when their dimensions or scales differ, and do not blend, average, or silently translate their scores. For a focused review that is not full or pre-submission, use only the requested rubric and the relevant dimensions. A defined rubric specifies dimensions and scale anchors and, for an overall score, weights or a decision rule. A request for decimals, missing-as-zero treatment, or a simple average is an output preference, not a defined rubric, and cannot override the evidence safeguards below.

For a named venue, verify that the criteria are current and official, record the source and access date, and preserve the venue's scale and anchors. If those criteria cannot be verified, do not assign a venue-fit score; provide a qualitative general fit assessment instead.

## Default category scorecard

Score these four categories on the 1-10 scale below, assigning an integer only when assessable and `N/A` otherwise:

| Category | Question | Evidence base |
|---|---|---|
| Novelty | Does the claimed contribution survive the combination test and the documented external comparison? | [novelty-verification.md](novelty-verification.md) |
| Theory | Do the assumptions, formal results, plausibility screen, and interpretation align with the claims? | [review-framework.md](review-framework.md) sections 2 and 3 |
| Computation and evidence | Does the implementation and evidence support the claimed practical scale and usefulness relative to existing feasible alternatives, including those giving similar conclusions? | [review-framework.md](review-framework.md) sections 2 and 4 |
| Writing and presentation | Can a critical reader recover the claim chain, and is the manuscript professionally edited? | [review-framework.md](review-framework.md) section 5; [ai-writing-alarm.md](ai-writing-alarm.md) only when its trigger applies |

Scoring the novelty category requires the external verification and search in [novelty-verification.md](novelty-verification.md); perform them whenever a search route in [academic-search-operations.md](academic-search-operations.md) is available and external search is within the requested scope. Without that verification and search, mark novelty `N/A` and state why. This does not prevent a supported packet-bounded overlap or practical-usefulness assessment under the [offline comparison boundary](novelty-verification.md#4-report-a-bounded-conclusion).
If an unresolved detail in a close comparator could reverse the novelty judgment, mark novelty `N/A` even when a search was performed. A limited search can support a provisional numeric score only when the inspected comparison still supports a bounded judgment.

When the user requests finer or additional dimensions, report them the same way and keep them consistent with their parent category: contribution identity and literature-supported novelty belong to novelty; statistical validity and method-theory coherence to theory; evidence, reproducibility, and computational practicality to computation and evidence; reviewer readability and patterned prose to writing and presentation. Interpretation and relevance, broad significance, and venue fit are separate optional dimensions scored only on request.

## Default scale

Use integer scores only, anchored in bands:

- **1-2:** not established or centrally deficient;
- **3-4:** weak, with major unresolved gaps;
- **5-6:** plausible but mixed, requiring substantial revision;
- **7-8:** strong, with bounded concerns;
- **9-10:** compelling and well supported in the reviewed scope.

Within a band, use the lower number when the limiting issue sits closer to the band below and the higher number otherwise. Do not use decimals. Missing material in a partial review is `N/A`, never zero or automatically a low score.

When the user requests a numeric scale from \(a\) to \(b\) without supplying anchors, first assign the supported default score \(s \in \{1,\ldots,10\}\), then map it by
\[
t=a+\frac{s-1}{9}(b-a).
\]
State the mapping and rounding rule once, round only the final mapped value to the precision supported by the requested scale, and preserve `N/A` as `N/A`. Do not use this conversion for a supplied or verified rubric that already defines its own anchors.

## Evidence and consistency

For every scored category or dimension, report:

- score;
- support status: established, partially supported, challenged, not established, or unassessed;
- one concise manuscript-specific justification;
- the principal limiting issue or missing verification, if any.

Across the brief basis and limiting issue, name the concrete claim, result, assumption, experiment, verified comparator, or passage driving the judgment and explain its consequence for that category. Select the decisive evidence and principal limitation; leave supporting calculations, experiment inventories, and secondary concerns in the findings. Generic phrases such as "restrictive conditions" or "useful experiments" are insufficient without the actual restriction or tested capability. A finding reference can carry details but cannot replace the reason. If no material limitation was identified within the reviewed scope, say so rather than inventing one.

For novelty, also report the contribution form, the supported combination-test classification or its unassessed status when the contribution is a combination, the search-coverage level, and whether the conclusion is bounded or provisional. Never assign a positive novelty score solely from the manuscript's own positioning.

Explain intellectual distinction and incremental practical benefit separately in the existing assessment. Judge a claimed new capability against alternatives that already provide similar conclusions; assess demonstrated practical gains in computation and evidence. Similar practical conclusions do not erase a supported theoretical contribution, and technical novelty alone does not establish usefulness. Let the overall judgment reflect the paper's stated purpose and remaining contribution. Do not add a fifth numerical category or automatic penalty, count the same overlap twice, or demand practical superiority from a paper claiming only a theoretical advance.

Apply the [repair and consequence calibration](review-framework.md#6-priority-synthesis) before using severity to constrain scores. A local typo, wrong justification, or repairable derivation is not by itself a major unresolved gap or a reason to demote the entire theory assessment. Judge the remaining supported contribution, accounting for any substantive restriction needed to repair it. Do not infer a score cap from the words "proof error" or "guarantee mismatch."

Check scores against the calibrated findings:

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

The table carries the category verdicts. Add a sentence below it only when a material distinction cannot be conveyed in a row, then give a short qualitative synthesis rather than restating every finding. For a focused review, show only the categories or dimensions relevant to the request.

When an additional user-supplied or venue rubric is requested in a full or pre-submission review, place its separate table after the default scorecard and any explanatory sentence. Label its source, scale, and aggregation rule, and state any mapping used for overlapping dimensions.

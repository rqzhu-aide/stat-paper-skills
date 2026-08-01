# Requested Reviewer Scores

## Purpose

Use numerical scores only when the user requests them. Treat each score as an ordinal reviewer judgment, not a measurement, acceptance probability, or substitute for the evidence-based diagnosis.

Use a defined rubric supplied by the user or a named venue when available. A defined rubric specifies dimensions and scale anchors and, for an overall score, weights or a decision rule. A request for decimals, missing-as-zero treatment, or a simple average is an output preference, not a defined rubric, and cannot override the evidence safeguards below.

For a named venue, verify that the criteria are current and official, record the source and access date, and preserve the venue's scale and anchors. If those criteria cannot be verified, do not assign a venue-fit score; provide a qualitative general fit assessment instead.

## Default dimensions

When no rubric is supplied, use the default dimensions relevant to the user's scoring request. Include every requested relevant dimension in the scorecard, assign an integer score only when assessable, and mark it `N/A` otherwise:

| Dimension | Question |
|---|---|
| Contribution identity and positioning | Is the paper's central contribution precise, coherent, and fairly positioned as presented? |
| Literature-supported novelty | Does the claimed distinction survive the documented external comparison? |
| Statistical validity and assumptions | Do the target, assumptions, method, and conclusions align? |
| Method-theory coherence | Do the formal results support the proposed and implemented procedure? |
| Evidence and reproducibility | Does the numerical or application evidence support the claims and permit evaluation? |
| Interpretation and relevance | Are the conclusions bounded, meaningful, and consequential? |
| Reviewer readability | Can a critical reader identify and evaluate the paper's claim chain? |
| Broad significance or venue fit | Score broad significance when the reviewed scope supports it. A named-venue fit score additionally requires verified current official criteria; otherwise report venue fit as `N/A` and provide only a bounded qualitative general-fit judgment. |

Keep contribution positioning separate from literature-supported novelty. If no external literature comparison was performed, score positioning when possible and mark literature-supported novelty `N/A`.

## Default scale

Use integer scores only:

- **1:** not established or centrally deficient;
- **2:** weak, with major unresolved gaps;
- **3:** plausible but mixed, requiring substantial revision;
- **4:** strong, with bounded concerns;
- **5:** compelling and well supported in the reviewed scope;
- **N/A:** not assessable from the supplied material or completed verification.

Do not use decimals or create apparent precision between anchors under the default rubric, even when the requested output format asks for them. Missing material in a partial review is `N/A`, never zero or automatically a low score.

## Evidence and consistency

For every dimension, report:

- score;
- support status: established, partially supported, challenged, not established, or unassessed;
- one concise manuscript-specific justification;
- the principal limiting issue or missing verification.

For literature-supported novelty, also report the search-coverage level and whether the conclusion is bounded or provisional. Never assign a positive novelty score solely from the manuscript's own positioning.

Check scores against the findings:

- an unresolved Critical finding must constrain any dimension it directly affects;
- a score of 4 or 5 is inconsistent with an unresolved Major finding in the same dimension unless the scope distinction is explicit;
- `N/A` must not be converted to zero for aggregation;
- broad interest, presentation, or novelty cannot compensate for an unestablished technical case.

## Overall judgment

Do not calculate an arithmetic mean by default. Use the qualitative readiness categories in [report-formats.md](report-formats.md) for the overall judgment.

Provide an overall numerical score only when a supplied or verified rubric defines its scale and aggregation or decision rule. A request for a simple average alone does not provide a defensible rule. Otherwise use a qualitative readiness category and explain why no aggregate is reported. Never let an aggregate conceal a Critical validity or central-claim failure.

## Output

Place the requested scorecard immediately after the overall assessment:

| Dimension | Score | Support status | Brief basis | Limiting issue |
|---|---:|---|---|---|

Show only dimensions relevant to the request. Follow the table with a short qualitative synthesis rather than repeating every finding.

# Statistical Review Report Formats

These formats deliver reviewer diagnosis, prioritized objections, and edit specifications. They do not produce revised manuscript text or modify manuscript artifacts.

An edit specification states what must change, where, why it matters to the paper's case, and what support or verification is needed. It is not insert-ready prose.

## Contents

- [Default integrated review](#default-integrated-review)
- [Scorecards](#scorecards)
- [Focused review](#focused-review)
- [Pre-submission readiness memo](#pre-submission-readiness-memo)
- [Multiple lenses](#multiple-lenses)
- [Finding anatomy](#finding-anatomy)

## Default integrated review

Use these components for a full manuscript review. The report should present the scientific judgment and its evidence, not reproduce the internal reading trace or search log. Combine components when they concern the same finding, and keep a review of partial material proportionate to what can be assessed.

1. **Review setup**
   - review scope and material reviewed;
   - intended paper type or venue, if known;
   - one-sentence manuscript claim.
2. **Overall assessment**
   - concise verdict;
   - strongest defensible aspect, if one is visible;
   - principal obstacle to a convincing paper and whether the central claim is supported in the reviewed scope.
3. **Category scorecard**
   - the default four categories from [scoring-rubric.md](scoring-rubric.md), plus any requested dimensions, each with an integer 1-10 score when assessable and `N/A` otherwise;
   - support status, brief basis, and limiting issue per row; add a category verdict below the table only when it explains a distinction the row cannot convey.
4. **Literature comparison, when assessed**
   - state the exact novelty claim and compare it with the closest verified work, identifying which was already cited and which was found independently; if no close work was found, state that result within the search boundary;
   - state what the inspected content supports, the material overlap or distinction, and why that distinction matters for the paper's claimed contribution;
   - give verification and discovery/citation status, source links or identifiers, and the search boundary near the conclusion; use a compact table or a few sentences rather than a search log.
5. **Main strengths**
   - up to three manuscript-specific strengths supported by the reviewed material;
   - do not count an important topic, an ambitious aim, the mere presence of paper components, stated intentions, or conditional future coherence as a strength;
   - omit this section when no defensible strength is visible in the reviewed scope.
6. **Priority findings**
   - Critical and Major findings first;
   - Moderate findings only when consequential;
   - Minor findings only when they retain a concrete reviewer-facing consequence;
   - include consequential first-reader failures and any reportable patterned-prose concern as findings, with their required evidence and scope;
   - group repeated symptoms of one scientific problem into one finding, and refer to the literature comparison rather than repeating it;
   - add a separate likely-objections note only if requested and it contributes a distinct concern.
7. **Assessment boundary and unresolved verification**
   - missing materials;
   - novelty, proof, citation, or implementation claims not verified; if no external comparison was possible, state that substantive novelty is unassessed here.
8. **Revision sequence**
   - ordered actions referring to existing finding labels;
   - distinguish rewrites from new scientific work;
   - end the integrated report here.

The category scorecard is part of the full review. Do not add other scores, an acceptance probability, or an editorial decision unless requested. If a recommendation posture is useful, use calibrated categories such as:

- ready for external review;
- promising, but revise before submission;
- substantial development required;
- central claim not yet established;
- venue or framing mismatch;
- assessment incomplete from supplied material.

## Scorecards

Use [scoring-rubric.md](scoring-rubric.md) for the default category scorecard in every full or pre-submission review and for any requested scores. Place the scorecard immediately after the overall assessment. Show `N/A` rather than penalizing categories that cannot be assessed from a partial manuscript or incomplete verification.

Do not calculate an arithmetic mean by default. Keep the qualitative readiness posture separate from the category scores. For named-venue scores, use current official criteria or mark venue fit unassessed and provide only a qualitative general fit judgment. In a full or pre-submission review, retain the default scorecard and place any user-supplied or venue rubric in a separate labeled table.

## Focused review

For a request limited to one section or concern, return:

1. scope and question reviewed;
2. concise diagnosis;
3. up to five prioritized findings, and fewer when only fewer consequential findings exist;
4. concrete edit specifications;
5. unassessed dependencies.

Do not force a paper-level verdict from a partial excerpt.
For a novelty-focused request, include the closest verified work, its substantive overlap or distinction, and the search boundary within the findings.

For a focused AI-writing request, classify only the reviewed scope. If the evidence is too short or narrow, use "not assessable." For an assessable case below the reporting threshold, use the single public label **No reportable pattern**. After emitting it once, delete every later occurrence of `reportable pattern` or `reportable recurrent pattern`, including negated forms. Express the bounded consequence without another classification phrase, and do not claim that AI use was ruled out.

## Pre-submission readiness memo

Organize around action:

1. submit now or revise first;
2. strongest reviewer-facing asset;
3. main acceptance risks;
4. a concise comparison with the closest literature and its search boundary when novelty is assessed;
5. changes possible by rewriting or reorganization;
6. changes requiring new analysis, theory, evidence, or verification;
7. optional venue-positioning note;
8. recommended revision order, which ends the memo.

Include the default category scorecard from [scoring-rubric.md](scoring-rubric.md) after the submit-or-revise judgment, and apply that rubric to any additionally requested scores. If the user requests outcome probabilities, state that they are judgmental rather than calibrated forecasts and explain the evidence behind them.

## Multiple lenses

Use multiple reviewer lenses only when requested. Keep a shared manuscript fact base and vary the weighting of stated criteria, for example:

- statistical validity and assumptions;
- contribution and theory-method coherence;
- evidence, application, and practical relevance;
- broad significance and nonspecialist readability when relevant.

Do not invent names, institutions, seniority, confidential knowledge, or access to different evidence. End with a synthesis that distinguishes consensus from weighting differences.

## Finding anatomy

Use this compact pattern for substantive findings:

### [Severity] Short diagnostic title

- **Location:** section, theorem, figure, or manuscript-wide scope.
- **Evidence:** what the manuscript states or shows.
- **Evidence status:** provenance and support status.
- **Reader sequence:** what information was available at that point, when relevant.
- **Concern:** the exact mismatch or omission.
- **Why it matters:** consequence for validity, contribution, interpretation, or reviewer confidence.
- **Edit specification:** what must change, its intended effect, and any dependency.
- **Remedy type:** rewrite, reanalysis, new evidence, new theory, verification, or author decision.

Use a compact evidence, consequence, and action paragraph instead of every template field as a separate bullet when the review remains equally precise. The overall assessment may summarize the principal concern once; keep its full evidence and diagnosis in one finding and refer back to that finding elsewhere.

For a material patterned-prose alarm, use the title "Recurrent patterned prose weakens claim traceability." Give two to four representative locations and follow [ai-writing-alarm.md](ai-writing-alarm.md). Do not title the finding "AI-written prose."

Do not supply replacement paragraphs, revised abstracts, insert-ready contribution bullets, or other manuscript-ready language. When actionability needs structure, use a diagnostic contribution-support ledger, theorem-role map, evidence-gap table, or evidence-requirement checklist and label it as reviewer analysis.

Even when the user requests review and revision together, complete the assessment boundary before the revision sequence and stop at the final dependency-ordered action. A focused report may instead stop at its unassessed dependencies. Do not add a closing boundary explanation or recommend a later editing workflow.
An edit specification may state the type and essential comparison or diagnostic requirement for a benchmark, control, sensitivity analysis, or guarantee. Do not invent results, a full study design, an estimator or algorithm, a numerical result, or exact theorem, rate-condition, or proof-step content not supplied by the manuscript.

For literature-based findings, cite the verified publication and identify whether it was cited by the manuscript or found independently. Do not present a search result as substantive overlap until the relevant content has been inspected.

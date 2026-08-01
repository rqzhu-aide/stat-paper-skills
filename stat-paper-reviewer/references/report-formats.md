# Statistical Review Report Formats

These formats deliver reviewer diagnosis, prioritized objections, and edit specifications. They do not produce revised manuscript text or modify manuscript artifacts.

An edit specification states what must change, where, why it matters to the paper's case, and what support or verification is needed. It is not insert-ready prose.

## Contents

- [Default integrated review](#default-integrated-review)
- [Requested scorecards](#requested-scorecards)
- [Focused review](#focused-review)
- [Pre-submission readiness memo](#pre-submission-readiness-memo)
- [Multiple lenses](#multiple-lenses)
- [Finding anatomy](#finding-anatomy)

## Default integrated review

Use this structure for a full manuscript review:

1. **Review setup**
   - review scope and material reviewed;
   - intended paper type or venue, if known;
   - one-sentence manuscript claim.
2. **Overall assessment**
   - concise verdict;
   - strongest defensible aspect, if one is visible;
   - principal obstacle to a convincing paper.
3. **Requested scorecard, when requested**
   - all requested relevant dimensions, with an integer score when assessable and `N/A` otherwise;
   - support status, brief basis, and limiting issue.
4. **Main strengths**
   - up to three manuscript-specific strengths supported by the reviewed material;
   - do not count an important topic, an ambitious aim, the mere presence of paper components, stated intentions, or conditional future coherence as a strength;
   - omit this section when no defensible strength is visible in the reviewed scope.
5. **Priority findings**
   - Critical and Major findings first;
   - Moderate findings only when consequential;
   - Minor findings only when they retain a concrete reviewer-facing consequence.
6. **First-reader sequence findings, when consequential**
   - earliest unresolved or delayed reader problem;
   - where later text resolves it, if applicable;
   - effect on the argument encountered in order.
7. **Patterned-prose alarm, when requested or when the reporting threshold is met**
   - bounded classification;
   - representative locations and evidence classes;
   - consequence for statistical meaning or claim traceability;
   - explicit statement that prose does not establish authorship.
8. **Novelty and citation evidence, when assessed**
   - manuscript citations checked;
   - closest external publications found;
   - each decisive publication labeled as cited by the manuscript or found independently and uncited;
   - verified distinction and remaining search boundary.
9. **Likely reviewer objections, when they add new framing**
   - concise objections not already expressed by the findings.
10. **Assessment boundary and unresolved verification**
   - missing materials;
   - novelty, proof, citation, or implementation claims not verified.
11. **Revision sequence**
   - ordered actions referring to existing finding labels;
   - distinguish rewrites from new scientific work;
   - end the integrated report here.

Do not include a score, acceptance probability, or editorial decision unless requested. If a recommendation posture is useful, use calibrated categories such as:

- ready for external review;
- promising, but revise before submission;
- substantial development required;
- central claim not yet established;
- venue or framing mismatch;
- assessment incomplete from supplied material.

## Requested scorecards

Use [scoring-rubric.md](scoring-rubric.md) whenever scores are requested. Place the scorecard immediately after the overall assessment. Show `N/A` rather than penalizing dimensions that cannot be assessed from a partial manuscript or incomplete verification.

Do not calculate an arithmetic mean by default. Keep the qualitative readiness posture separate from requested aspect scores. For named-venue scores, use current official criteria or mark venue fit unassessed and provide only a qualitative general fit judgment.

## Focused review

For a request limited to one section or concern, return:

1. scope and question reviewed;
2. concise diagnosis;
3. up to five prioritized findings, and fewer when only fewer consequential findings exist;
4. concrete edit specifications;
5. unassessed dependencies.

Do not force a paper-level verdict from a partial excerpt.

For a focused AI-writing request, classify only the reviewed scope. If the evidence is too short or narrow, use "not assessable." For an assessable case below the reporting threshold, use the single public label **No reportable pattern**. After emitting it once, delete every later occurrence of `reportable pattern` or `reportable recurrent pattern`, including negated forms. Express the bounded consequence without another classification phrase, and do not claim that AI use was ruled out.

## Pre-submission readiness memo

Organize around action:

1. submit now or revise first;
2. strongest reviewer-facing asset;
3. main acceptance risks;
4. changes possible by rewriting or reorganization;
5. changes requiring new analysis, theory, evidence, or verification;
6. optional venue-positioning note;
7. recommended revision order, which ends the memo.

If the user requests a score, apply [scoring-rubric.md](scoring-rubric.md). If the user requests outcome probabilities, state that they are judgmental rather than calibrated forecasts and explain the evidence behind them.

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

Use paragraphs instead of this template when the review remains equally precise. The overall assessment may summarize the principal concern once; keep its full evidence and diagnosis in one finding and refer back to that finding elsewhere.

For a material patterned-prose alarm, use the title "Recurrent patterned prose weakens claim traceability." Give two to four representative locations and follow [ai-writing-alarm.md](ai-writing-alarm.md). Do not title the finding "AI-written prose."

Do not supply replacement paragraphs, revised abstracts, insert-ready contribution bullets, or other manuscript-ready language. When actionability needs structure, use a diagnostic contribution-support ledger, theorem-role map, evidence-gap table, or evidence-requirement checklist and label it as reviewer analysis.

Even when the user requests review and revision together, complete the assessment boundary before the revision sequence and stop at the final dependency-ordered action. A focused report may instead stop at its unassessed dependencies. Do not add a closing boundary explanation or recommend a later editing workflow.
An edit specification may state the type and essential comparison or diagnostic requirement for a benchmark, control, sensitivity analysis, or guarantee. Do not invent results, a full study design, an estimator or algorithm, a numerical result, or exact theorem, rate-condition, or proof-step content not supplied by the manuscript.

For literature-based findings, cite the verified publication and identify whether it was cited by the manuscript or found independently. Do not present a search result as substantive overlap until the relevant content has been inspected.

# Statistical Reviewer QA

Grounding, provenance and support status, severity, mathematical fidelity, role boundaries, and applicable terminal output checks govern every review. Dimension-specific checks apply when that dimension is assessed or needed to support the requested judgment. A focused review does not require unrelated scores, literature claims, writing assessments, or a whole-paper reading record.

## Grounding

- Trace each substantive judgment to manuscript text, supplied context, a visible figure or result, or a verified source.
- Label provenance separately as manuscript assertion, manuscript demonstration, reviewer inference, or verified external source.
- Label support separately as established, partially supported, challenged, not established, or unassessed.
- Do not treat an observed manuscript assertion as established evidence.
- Mark missing evidence instead of inventing it.
- Before an absence finding, check likely locations, terminology variants, and relevant references within the assessment scope. Reuse prior searches and limit the claim to the coverage inspected.
- Keep the manuscript fact base consistent across the report.
- Do not use nonexistent line numbers, figures, comparisons, citations, or results.

## First-reader integrity

- Preserve the order in which the manuscript supplied information.
- Locate a reader problem at its earliest consequential occurrence.
- If later text resolves it, describe the resolution as delayed rather than pretending it was available earlier.
- Do not let external literature or a second reading erase the first-pass assessment.
- When later material resolves the scientific question, retain any consequential presentation delay without treating it as a continuing validity gap; calibrate severity to the remaining defect.
- Do not include a full reading diary when only a few sequence failures matter.

## Technical calibration

- Distinguish target mismatch, validity gap, exposition gap, and missing verification.
- Do not call a proof incorrect because its roadmap is unclear.
- Do not call a proof verified unless all nontrivial steps and dependencies were checked.
- Do not describe an oracle guarantee as a feasible-procedure guarantee.
- Do not confuse statistical error, approximation error, and computational error.
- Do not infer causal meaning from predictive or associational evidence.

## Review calibration

- State the main concern early.
- Rank issues by consequence rather than by manuscript order.
- Apply [repair and consequence calibration](review-framework.md#6-priority-synthesis) before assigning severity. State the credible remedy and whether it changes assumptions, conclusions, or meaningful scope; a wrong justification for a valid step differs from a wrong derivation. Assess both conventionality and actual restriction when an assumption must be added.
- Distinguish an established local repair, a demonstrated need for stronger conditions, and an unresolved repair question. Do not infer impossibility from failure to find a repair or call an assumption standard without supplied or verified support.
- Avoid demanding new theory or experiments when narrowing or clarifying the claim is sufficient.
- Distinguish required revisions from optional strengthening.
- Omit isolated style preferences and pure copyediting even when detailed language comments are requested, except through the aggregate editing report and its capped examples defined in [review-framework.md](review-framework.md) section 5 whenever writing is scored or explicitly assessed.
- Report an exposition issue only when it has a concrete consequence for a consequential claim, validity assessment, evidence, reproducibility, interpretation, professional readiness, or reviewer confidence.
- Make each high-priority recommendation actionable through an edit specification.
- Do not express actionability as insert-ready manuscript prose.

## Patterned-prose alarm

- Do not infer AI authorship, intent, or misconduct from prose.
- Do not use detector scores, perplexity, sentence rhythm, word lists, phrase inventories, or simulated detector rationales as evidence.
- Confirm the required number of independent instances, evidence classes, and section spread before reporting a manuscript-wide alarm.
- Check literal software language, genre conventions, translation, multi-author editing, and required templates as alternative explanations.
- Cite representative passages and describe the statistical or claim-traceability consequence. Apply [ai-writing-alarm.md](ai-writing-alarm.md)'s example caps to the prose assessment, not to independently consequential scientific findings.
- Keep technical S1 or S2 findings under their native headings and avoid duplicating them as separate prose findings.
- For every explicit provenance question, state that textual evidence does not establish authorship, AI use, intent, or a particular writing tool.

## Novelty and venue boundaries

- Verify central cited references and search for close external publications for every field-level novelty, originality, or priority judgment or score.
- Without the required external verification and search, mark field-level novelty unassessed and its score `N/A`. Keep any supported packet-bounded overlap or practical-usefulness assessment separate, following the [offline comparison boundary](novelty-verification.md#4-report-a-bounded-conclusion).
- Distinguish citation existence, metadata accuracy, claim support, and contribution overlap.
- Identify whether each decisive publication was cited by the manuscript or found independently.
- Distinguish peer-reviewed publications, conference papers, accepted manuscripts, and preprints.
- Report searched sources, search date, query concepts, and important access limits.
- Use a provisional novelty conclusion only when the inspected external comparison supports a bounded judgment; leave it unassessed and its score `N/A` when missing decisive content could reverse that judgment.
- Treat failure to find closer work as bounded negative search evidence, not proof of firstness.
- Use `new primitive` only for a contribution not reducible to an assembly of components in the verified comparison set; classify an actual combination as an enabling combination or convenience assembly only when supported. Otherwise leave the classification unassessed and identify the missing decisive comparison or argument.
- Distinguish field-local importance from broad scientific importance.
- For a practical-usefulness judgment, check existing feasible alternatives under comparable targets, information, assumptions, guarantees, and operating conditions. Similar conclusions on one dataset are not equivalence; a new construction is not itself a practical gain. Credit supported improvements in precision, robustness, cost, or usability even when the conclusion is unchanged, and distinguish absent comparison evidence from demonstrated lack of benefit.
- Keep intellectual novelty and practical usefulness distinct, without duplicate score penalties or an automatic empirical-superiority requirement for theoretical work. Apply the same source-verification and evidence limits to a claim that an existing method already solves the practical problem.
- Do not predict an editorial decision as fact.
- Do not assign acceptance probabilities by default, and add scores beyond the default category scorecard only on request.
- If a named venue is in scope, distinguish current verified official criteria from general reviewer judgment.

## Scores

- Apply [scoring-rubric.md](scoring-rubric.md) to the default category scorecard in every full or pre-submission review and to any requested scores.
- In a full or pre-submission review, keep a user-supplied or verified venue rubric separate from the default scorecard; let it govern only its own dimensions, scale, and overall rule. For a focused review, use the requested rubric and relevant dimensions.
- For a named venue, use current verified official criteria or leave venue fit `N/A`; do not silently map a venue scale onto the default scale.
- Use `N/A` for categories or dimensions not assessable from the reviewed scope or completed verification.
- Could a score explanation apply unchanged to an unrelated paper? If so, replace general impressions with the concrete manuscript evidence and its consequence for the judgment. Do not invent a weakness to fill the limiting-issue field.
- Assess the reviewed version directly; claims of improvement over another version require an explicitly requested comparison supported by the reviewed materials.
- Do not use decimals or calculate an arithmetic mean by default.
- Reconcile each score with the Critical and Major caps in the rubric, missing materials, and provisional novelty.
- Do not let broad interest, presentation, or novelty compensate for an unestablished technical case.

## Output integrity

- Include the reviewed scope and missing materials. In a full or readiness review, check that the scientific opening makes the data or system, model or design, substantive assumptions, goal, and proposed contribution understandable without technical rate or proof conditions. Identify unspecified essentials without inventing them; a simulation design is not the general model. Keep focused openings proportionate to the question.
- Include only manuscript-specific strengths supported by the reviewed material; do not manufacture praise to fill a quota.
- Let the overall assessment name the principal concern once, but keep its full evidence and diagnosis in one finding; elsewhere refer to that finding rather than restating it.
- Include likely objections only when they add framing not already captured by a finding.
- In the revision order, refer to existing finding labels instead of restating the same diagnoses.
- Distinguish presentation repairs from changes requiring reanalysis, evidence, theory, verification, or author judgment.
- Produce diagnoses and edit specifications only; do not draft, polish, restructure, or modify manuscript artifacts.
- Do not design missing scientific content while specifying that it is required.
- Do not mention the skill name or internal workflow rules in the review.
- Begin with the scientific opening for a full or readiness review, or the relevant scope and diagnosis for a focused question; do not begin with internal workflow rules.
- Do not recommend a separate or subsequent writing, drafting, editing, or revision pass.
- State an out-of-scope boundary directly and stop at reviewer diagnosis.
- For integrated and readiness reports, place assessment boundaries before the dependency-ordered revision sequence and end with that sequence. Focused reports may end with unassessed dependencies.
- Place source links or persistent identifiers near literature-based judgments.

## Terminal checks

Run these checks on the complete response immediately before returning.

- Compare mathematical expressions and verbal paraphrases throughout the report, including the opening and scorecard, with the supplied or verified source. Preserve the object, population, conditioning, quantifier, rate, finite-sample or asymptotic status, oracle or feasible status, and guarantee scope; delete any strengthening or recategorization not supplied by the record. Keep goals and claimed results distinct from established conclusions.
- Does each formula clarify the target, scientific distinction, or reason for the judgment? Explain unfamiliar symbols and the expression's meaning or consequence locally; remove mathematical decoration and repeated formulas that add no understanding. Do not supply a missing model, estimand, or assumption merely to make the review look mathematical.
- For every theorem plausibility comparison to a known result, lower bound, or settled case, identify the supplied or verified comparator. If none exists, mark that external comparison unassessed and retain only the manuscript-internal special-case, coherence, and dependency checks.
- For every decisive novelty or citation comparator, include an explicit `Verification status:` and an explicit `Discovery/citation status:`, retain the exact supplied DOI, PMID, arXiv ID, or direct official link, and preserve a supplied status of `found independently and uncited`; chronology or the word `uncited` alone does not satisfy the discovery field. Insert either missing field before returning.
- Inspect every numeric scorecard entry. If the reviewed scope or completed verification cannot support a category or dimension, replace the number with `N/A`; never use 1 or another low score as a missing-evidence penalty. A manuscript assertion about empirical performance does not make the evidence assessable when no numerical evidence is supplied.
- Delete any purely cosmetic finding or edit specification outside the aggregate editing report and its capped examples for a requested writing assessment. It is acceptable to state once that cosmetic issues were excluded, but do not quote, identify, or discuss the omitted wording. For a focused request containing both a consequential defect and a cosmetic distractor, report only the consequential defect and do not mention the distractor.
- Do not emit U+2013 or U+2014 except inside a verbatim quotation, title, or identifier that itself contains the character. Do not introduce sentence-level TeX forms that render as long dashes either. Elsewhere use a comma, colon, semicolon, parentheses, or an ordinary hyphen according to its grammatical role; preserve mathematical notation and ranges.
- Delete any closing sentence that explains a refusal to draft, rewrite, or edit; end with the report's substantive content.
- For a mixed review-and-rewrite request, delete any revised, replacement, or rewritten manuscript heading and all manuscript-style prose beneath it. Retain only edit specifications that identify the location, problem, consequence, intended change, claim boundary, and required verification or author judgment. Never introduce notation, estimator definitions, assumptions, algorithms, or claims absent from the supplied manuscript record.
- For any patterned-prose classification, run the terminal output checks in [ai-writing-alarm.md](ai-writing-alarm.md).
- For a bundled run, apply [run-portability.md](run-portability.md)'s finalization gate before labeling the review complete; otherwise report `PARTIAL` or `NONFINAL` with the exact missing stages and affected conclusions. Reading its universal source-map guidance alone does not select the bundled route.

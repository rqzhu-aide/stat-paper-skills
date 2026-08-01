# Statistical Reviewer QA

## Grounding

- Trace each substantive judgment to manuscript text, supplied context, a visible figure or result, or a verified source.
- Label provenance separately as manuscript assertion, manuscript demonstration, reviewer inference, or verified external source.
- Label support separately as established, partially supported, challenged, not established, or unassessed.
- Do not treat an observed manuscript assertion as established evidence.
- Mark missing evidence instead of inventing it.
- Keep the manuscript fact base consistent across the report.
- Do not use nonexistent line numbers, figures, comparisons, citations, or results.

## First-reader integrity

- Preserve the order in which the manuscript supplied information.
- Locate a reader problem at its earliest consequential occurrence.
- If later text resolves it, describe the resolution as delayed rather than pretending it was available earlier.
- Do not let external literature or a second reading erase the first-pass assessment.
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
- Avoid demanding new theory or experiments when narrowing or clarifying the claim is sufficient.
- Distinguish required revisions from optional strengthening.
- Omit isolated style preferences and pure copyediting even when detailed language comments are requested.
- Report an exposition issue only when it has a concrete consequence for a consequential claim, validity assessment, evidence, reproducibility, interpretation, professional readiness, or reviewer confidence.
- Make each high-priority recommendation actionable through an edit specification.
- Do not express actionability as insert-ready manuscript prose.

## Patterned-prose alarm

- Do not infer AI authorship, intent, or misconduct from prose.
- Do not use detector scores, perplexity, sentence rhythm, word lists, phrase inventories, or simulated detector rationales as evidence.
- Confirm the required number of independent instances, evidence classes, and section spread before reporting a manuscript-wide alarm.
- Check literal software language, genre conventions, translation, multi-author editing, and required templates as alternative explanations.
- Cite representative passages and describe the statistical or claim-traceability consequence.
- Keep technical S1 or S2 findings under their native headings and avoid duplicating them as separate prose findings.
- For every explicit provenance question, state that textual evidence does not establish authorship, AI use, intent, or a particular writing tool.

## Novelty and venue boundaries

- Verify central cited references and search for close external publications for every actual novelty, originality, or priority judgment or score.
- Without external comparison, assess only the clarity of manuscript positioning and mark substantive novelty unassessed.
- Distinguish citation existence, metadata accuracy, claim support, and contribution overlap.
- Identify whether each decisive publication was cited by the manuscript or found independently.
- Distinguish peer-reviewed publications, conference papers, accepted manuscripts, and preprints.
- Report searched sources, search date, query concepts, and important access limits.
- Treat novelty as provisional when close literature, full text, or cited support has not been checked.
- Treat failure to find closer work as bounded negative search evidence, not proof of firstness.
- Distinguish field-local importance from broad scientific importance.
- Do not predict an editorial decision as fact.
- Do not assign scores or probabilities by default.
- If a named venue is in scope, distinguish current verified official criteria from general reviewer judgment.

## Requested scores

- Apply [scoring-rubric.md](scoring-rubric.md) only when the user requests scores.
- Prefer a user-supplied rubric. For a named venue, use current verified official criteria or leave venue fit `N/A`; use the default integer anchors only for other assessable dimensions.
- Use `N/A` for dimensions not assessable from the reviewed scope or completed verification.
- Give one manuscript-specific basis and one limiting issue for every score.
- Do not use decimals or calculate an arithmetic mean by default.
- Reconcile each score with Critical and Major findings, missing materials, and provisional novelty.
- Do not let broad interest, presentation, or novelty compensate for an unestablished technical case.

## Output integrity

- Include the reviewed scope and missing materials.
- Include only manuscript-specific strengths supported by the reviewed material; do not manufacture praise to fill a quota.
- Let the overall assessment name the principal concern once, but keep its full evidence and diagnosis in one finding; elsewhere refer to that finding rather than restating it.
- Include likely objections only when they add framing not already captured by a finding.
- In the revision order, refer to existing finding labels instead of restating the same diagnoses.
- Distinguish presentation repairs from changes requiring reanalysis, evidence, theory, verification, or author judgment.
- Produce diagnoses and edit specifications only; do not draft, polish, restructure, or modify manuscript artifacts.
- Do not design missing scientific content while specifying that it is required.
- Do not mention the skill name or internal workflow rules in the review.
- Begin with manuscript scope or diagnosis, not a statement about the response type or workflow boundary.
- Do not recommend a separate or subsequent writing, drafting, editing, or revision pass.
- State an out-of-scope boundary directly and stop at reviewer diagnosis.
- For integrated and readiness reports, place assessment boundaries before the dependency-ordered revision sequence and end with that sequence. Focused reports may end with unassessed dependencies.
- Place source links or persistent identifiers near literature-based judgments.

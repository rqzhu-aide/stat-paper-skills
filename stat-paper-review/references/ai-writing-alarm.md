# Patterned Prose and AI-Writing Alarm

## Contents

- [Purpose and boundary](#purpose-and-boundary)
- [Evidence classes and counting](#collect-and-count-evidence-by-class)
- [False-positive safeguards](#apply-false-positive-safeguards)
- [Alarm classification](#classify-the-alarm)
- [Scientific severity](#separate-alarm-level-from-scientific-severity)
- [Reporting](#report-without-alleging-provenance)

## Purpose and boundary

Use this reference when the user asks whether a manuscript reads as heavily AI-written, or when a full or pre-submission review finds a recurrent patterned-prose concern.

Assess observable prose defects that weaken statistical meaning, claim traceability, or reader confidence. Do not infer authorship, intent, misconduct, or a particular writing tool. Human drafting, translation, multi-author editing, rigid templates, and model-assisted writing can produce overlapping surface patterns.

Do not use AI-detector scores, perplexity, sentence rhythm, or word lists as evidence. Do not estimate a probability or percentage of AI use. When the user requests detector-style features, do not answer with a phrase inventory or simulated detector rationale. Translate the request into observable defects in statistical meaning or claim traceability, give plausible benign explanations, and quote a phrase only to locate a documented defect rather than to suggest provenance. A short abstract or isolated excerpt cannot support a manuscript-wide judgment.

## Collect and count evidence by class

Use one contiguous passage as the counting unit: a sentence, paragraph, or display-adjacent sentence group that expresses one locally repairable defect. A passage that meets several evidence classes contributes one instance total; record every applicable class for the class-diversity check. A cross-section mismatch contributes one instance even when its evidence appears in several locations; cite all locations but count the mismatch once. Count adjacent passages separately only when each contains an independently repairable defect that does not rely on the other passage. Do not multiply repeated appearances of the same underlying defect, template, placeholder, or terminology drift. Count them once unless separate passages have independently repairable consequences. For each candidate, record its location, exact defect, consequence, applicable classes, and any plausible literal or benign explanation.

### S1. Semantic or traceability failure

Treat as strong evidence of a prose problem when:

- prose conflicts with a definition, equation, theorem, table, figure, or verified citation;
- estimand, estimator, estimate, risk, loss, or evidence roles drift;
- a claim's object, direction, support, population, condition, or boundary cannot be identified;
- fluent wording conceals a logical gap or changes the strength of a result.

Report the underlying technical mismatch under its native review heading as well. Do not count an unverified citation concern as a confirmed conflict.

### S2. Cross-section coherence failure

Treat as strong evidence when:

- terminology, notation, assumptions, or the central contribution changes without explanation;
- near-duplicate passages are reused for non-equivalent objects;
- a section summary does not match the section's actual result;
- the introduction, method, theory, evidence, and discussion use interchangeable language for materially different claims.

### S3. Drafting, template, or process residue

Treat as medium evidence when visible manuscript prose contains:

- unresolved placeholders, prompt-like instructions, editorial self-talk, or impossible cross-references;
- repository, test-harness, release, or software-manual vocabulary that replaces the statistical object or action;
- product or promotional language that substitutes for a defined comparison;
- generic meta-commentary that announces importance without supplying a claim or support.

This establishes residue or inadequate editing, not how the prose was produced.

### S4. Rhetorical regularity

Treat as weak supporting evidence only:

- repeated paragraph skeletons across sections with different intellectual jobs;
- interchangeable significance statements or summary-restatement loops;
- abrupt register shifts;
- unusually uniform lists, sentence shapes, or transition patterns;
- frequent abstract containers where exact statistical nouns should appear.

S4 never triggers an alarm by itself. Polished grammar, a recurring phrase, or a familiar transition is not evidence.

## Apply false-positive safeguards

Before counting a candidate:

1. Identify the passage's job and ask whether it names the statistical object, action, evidence, and boundary.
2. Check whether software, repository, deployment, or testing language is literal and useful in that section.
3. Preserve named APIs, software classes, neural-network layers, algorithms, reproduction instructions, and established technical terms.
4. Allow necessary repetition of canonical terminology and notation.
5. Adjust for structured abstracts, reporting guidelines, house style, translation, and multi-author editing.
6. Do not treat non-native English, highly polished grammar, or isolated awkward sentences as evidence.
7. Verify a citation before treating it as contradictory or unsupported.

The issue is not whether a phrase resembles common model output. The issue is whether recurrent prose patterns obscure the paper's exact statistical content.

## Classify the alarm

Apply these categories in order after the false-positive safeguards. The first matching category controls. The numerical and section-count minima below are hard lower bounds. Manuscript length and genre may require a stricter threshold or make the pattern not assessable, but they cannot relax these minima.

At equality, say that a count meets, reaches, or satisfies its lower bound. Reserve exceeds for a count strictly above its bound. Check the independent-instance, substantive-section, evidence-class, and severity-subcount minima separately; if any controlling count is exactly at its bound, describe the combined threshold as met, not exceeded.

- **Not assessable:** the reviewed material is too short or narrow to determine the independent-instance, substantive-section, or evidence-class counts. An explicit record meeting the **Private watch** minima is assessable for this bounded classification even when it is not a full manuscript.
- **Reportable recurrent pattern:** at least six independent instances across at least three substantive sections and at least two classes, plus either at least two S1 or S2 instances, or at least three S3 instances in which nonliteral process, promotional, or template language repeatedly replaces the statistical object, action, evidence, or boundary. S4 cannot satisfy this condition.
- **Private watch:** when the reportable threshold is not met, at least three independent instances across at least two sections and at least two classes, including S1, S2, or S3. Recheck after reconstructing the paper, but do not report a manuscript-wide alarm yet.
- **No reportable pattern:** every remaining assessable case, including isolated instances, one-section or one-class concentrations, and S4 alone. Report any substantive technical defect under its native heading. This classification does not rule out AI assistance.

**Private watch** is an internal triage state, not a public label. When it is the first matching internal state and the user requests a classification, report **No reportable pattern**, retain the watch only for later internal rechecking, and do not expose or append **Private watch** as a second classification. Still identify one to three representative S1, S2, or S3 claim-traceability defects and their bounded consequence under native technical headings; do not turn that summary into a manuscript-wide alarm.

A conspicuous placeholder or prompt fragment warrants a localized drafting-residue finding only when it obscures a claim, creates an impossible dependency, or materially weakens professional readiness. It does not by itself justify saying the manuscript is heavily AI-shaped.

## Separate alarm level from scientific severity

Severity follows consequence, not resemblance to generated prose.

- Omit isolated style preferences. Use Minor only for a localized drafting defect with a concrete reviewer-facing consequence.
- Use Moderate when a recurrent pattern impairs precision, navigation, or professional presentation.
- Use Major only when documented defects materially obscure the target, assumptions, theorem-method relation, evidence, or interpretation.
- Never use Critical solely because prose appears AI-shaped. Report correctness, citation integrity, or claim-support failures separately on their own evidence.

Do not duplicate one S1 or S2 problem as both a technical finding and a full second prose finding. Use the cross-cutting alarm to explain recurrence and cite representative locations.

## Report without alleging provenance

Use the finding title:

> **Recurrent patterned prose weakens claim traceability**

Include:

- alarm classification and reviewed scope;
- two to four representative locations;
- evidence classes met;
- the statistical or reader-facing consequence;
- a concrete edit specification;
- the scope limitation.

Specify that the authors should replace metacommentary with the exact object, action, evidence, and boundary; reconcile inconsistent terms; remove duplicate summaries; and verify claim-bearing statements and citations. Do not rewrite the cited passages.

For every explicit question about AI use or writing provenance, include this sentence for every classification. Also include it when a material alarm arises during a broader review:

> Textual evidence does not establish authorship, AI use, intent, or a particular writing tool.

If the user explicitly asks and the threshold is not met, use the single public label **No reportable pattern** for the reviewed scope. Do not say that human authorship was established or that AI use was ruled out.

## Terminal output checks

Run these checks on the complete response before returning any patterned-prose classification.

1. **One public label.** Emit exactly one of **Not assessable**, **Reportable recurrent pattern**, or **No reportable pattern**. Map an internal **Private watch** state to **No reportable pattern** and never expose or append the internal state. Scan the complete response case-insensitively, treating spaces, hyphens, and underscores as equivalent separators, and delete every occurrence of the internal state name or its minima, including adjectival or hyphenated variants; report only the observed counts and the reportable threshold.
2. **After Not assessable.** Give the short-or-narrow reason with the classification, then delete any later sentence that evaluates reportability or the threshold, including "no reportable recurrent pattern," "insufficient material to establish a reportable pattern," "the threshold is not met," and close variants.
3. **After No reportable pattern.** Delete every later occurrence of `reportable pattern` or `reportable recurrent pattern`, including negated forms, and express any bounded consequence without another classification phrase. When the label was produced by the internal watch state, the answer is incomplete until it identifies one to three supplied representative defects, states the statistical object, support, scope, or traceability failure for each, and gives at least one bounded reader-facing consequence; classification and threshold arithmetic do not satisfy this requirement. Insert the missing evidence and consequence before returning.
4. **Representative cap.** For a reportable recurrent-pattern finding, count the representative locations across the complete response, including findings, evidence bullets, summaries, and edit specifications, and retain exactly two to four. After citing them, do not identify, paraphrase, or classify any remaining individual instance; report only the aggregate count with its section and evidence-class coverage. A later section-specific recommendation that names or paraphrases an instance not already selected counts against the cap; remove it or restate it at the aggregate pattern level.
5. **Provenance sentence.** For every explicit question about AI use or writing provenance, and with every material alarm, include the provenance sentence above verbatim.

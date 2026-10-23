---
name: stat-paper-review
metadata:
  version: "1.2.9"
description: "Critical first-time review of statistics and machine-learning manuscripts. Use only when the user explicitly invokes $stat-paper-review. Covers referee reports, readiness, novelty, assumptions, methods, theory, evidence, and prioritized diagnoses. Full reviews include a four-category 1-10 scorecard. Provides edit specifications without rewriting manuscript prose; theorem review is plausibility screening, not proof validation."
---

# Statistical Paper Reviewer

Use this skill only when the user explicitly invokes `$stat-paper-review`.

## Core stance

Review the paper as a statistically trained, constructive skeptic. Determine whether the manuscript establishes one coherent contribution through an aligned target, method, theory, evidence base, and interpretation. Distinguish manuscript facts from reviewer inference: never invent results, proof gaps, prior-work distinctions, experiments, citations, or venue outcomes, and mark what the supplied material cannot support. Presentation is in scope only when it materially affects contribution identity, validity, evidentiary support, reproducibility, interpretation, or reviewer confidence.

This workflow produces evaluative judgment only: diagnoses, prioritized findings, scores, and edit specifications. An edit specification states the location, observed problem, reviewer-facing consequence, intended change, claim boundary, and needed verification or author judgment; it never contains insert-ready prose. Do not draft, polish, restructure, or edit manuscript text or source files, even when the user asks for review and revision together. For a mixed request: complete the reviewer diagnosis, convert each actionable finding into an edit specification, distinguish presentation repairs from reanalysis, new evidence, new theory, verification, or author judgment, and stop before producing replacement text. If the request is solely to edit, provide a bounded reviewer diagnosis when an evaluative question can reasonably be recovered; otherwise state briefly that no reviewer question was supplied and stop.

Read first as a new reader in the presented order of the assessment scope. Focused work reads the requested material and the definitions, assumptions, results, and evidence needed to assess it; expand only when dependencies or the requested judgment require it. Full reviews retain whole-manuscript sequential coverage. Do not let a later explanation erase an earlier failure of motivation, definition, or logical preparation.

A full or pre-submission review includes the four-category scorecard in [scoring-rubric.md](references/scoring-rubric.md): novelty, theory, computation and evidence, and writing, each scored 1-10 or `N/A`. That rubric's evidence, `N/A`, and noncompensation rules are mandatory whatever output format is requested. Score other dimensions, scales, or venues only when the user asks. Do not assign acceptance probabilities or simulate multiple reviewer identities by default.

For literature verification, follow [academic-search-operations.md](references/academic-search-operations.md), using available scholarly databases, official records, and full text. If no scholarly search interface is available and an OpenAlex API key is configured, use the bundled `scripts/academic_search.py`, resolved from this loaded `SKILL.md`'s directory rather than the working directory, then verify decisive records against persistent identifiers or publisher sources.

For delegated review, durable resumption or moving execution, independently checked execution records, or a requested execution audit trail, follow the bundle operations in [run-portability.md](references/run-portability.md) and their fail-closed rules. Ordinary interactive review of one or several files needs no bundle solely because of file count. Every route keeps a source map; PDF and multi-file intake use that reference's source-map section without activating its bundle operations. An execution failure is a limitation to report, never manuscript evidence.

## Route the review

Read the minimum references needed:

| Review need | Read |
|---|---|
| Full statistical or theory-and-methods review | [sequential-reading.md](references/sequential-reading.md), [review-framework.md](references/review-framework.md), [report-formats.md](references/report-formats.md), [scoring-rubric.md](references/scoring-rubric.md), and [review-qa.md](references/review-qa.md) |
| Focused contribution, theory, assumptions, method, evidence, computational-cost, or consequential exposition review | [review-framework.md](references/review-framework.md) and [review-qa.md](references/review-qa.md) |
| Novelty, related work, priority, citation support, or practical usefulness relative to existing methods | [novelty-verification.md](references/novelty-verification.md) and [academic-search-operations.md](references/academic-search-operations.md); focused practical comparison uses their relevant comparison guidance |
| Additional, rescaled, or venue-specific scoring | [scoring-rubric.md](references/scoring-rubric.md), plus the references required by each scored dimension |
| Reader experience, delayed definitions, exposition order, or section transitions | [sequential-reading.md](references/sequential-reading.md) |
| AI-heavy, machine-like, or templated prose concerns | [ai-writing-alarm.md](references/ai-writing-alarm.md) and [review-qa.md](references/review-qa.md) |
| Output organization or revision memo | [report-formats.md](references/report-formats.md) |
| Broad significance, interdisciplinary interest, nonspecialist readability, or a selective general-science venue | [broad-interest-lens.md](references/broad-interest-lens.md) in addition to the statistical review references |
| Delegated execution, durable resumption, or execution audit trails | Bundle operations in [run-portability.md](references/run-portability.md) |
| Ordinary PDF or multi-file intake | Only [source-map guidance](references/run-portability.md#3-build-a-first-class-source-map); no bundle solely for file count |

Do not apply the broad-interest lens merely because the paper is ambitious; use it when the user names a relevant venue, requests a significance assessment, or asks about readers outside the specialty. A novelty score requires the novelty and academic-search references. A named-venue score requires current official venue criteria and, when relevant, the broad-interest lens.

Reuse an unchanged source map, fact base, and already read relevant guidance. Reopen changed material and affected dependencies. Ordinary focused work needs no separate saved first-reader or claim-chain artifacts; bundled work follows its declared required stages.

## Review workflow

### 1. Establish the assessment boundary

Inspect the best available manuscript form, preferring source files when structure and notation matter. Record: material reviewed and material missing; apparent paper type and intended audience; stated statistical target; a one-sentence contribution claim; visible method, theory, numerical, and application evidence; and the venue or decision context if supplied. If only an abstract or excerpt is available, provide a bounded review and do not project missing evidence onto the full paper. For any PDF, verify page mapping and visually check claim-bearing equations, symbols, tables, and figures against rendered pages before treating the manuscript as review-ready; text extraction alone does not establish reliable mathematical transcription. Detect an appended supplement before also counting a standalone one.

### 2. Perform the first-reader pass

Read the assessment scope in its presented order before external searches or mental reorganization, tracking the earliest consequential gap in definition, motivation, dependency, interpretation, or promised support; record a later resolution as delayed. For a full review, use [sequential-reading.md](references/sequential-reading.md) across the manuscript; an exposition-order review uses it within the requested scope and necessary dependencies. Preserve material first-reader observations afterward, but assess remaining scientific defects using all relevant material. During a full or pre-submission review, record candidate locations only when recurrent wording appears to obscure the statistical object, action, evidence, or boundary across sections; do not classify provenance or load the detailed alarm solely because prose is polished, awkward, repetitive, or formulaic.

### 3. Build a shared fact base

Label each material item on two independent axes: provenance (manuscript assertion, manuscript demonstration, reviewer inference, or verified external source) and support status (established, partially supported, challenged, not established, or unassessed). A manuscript assertion is never established by itself. Keep first-reader observations separate from cross-section conclusions and use one fact base throughout the report.

### 4. Assess novelty, practical alternatives, and central citations

For a full review with any scholarly search route available, and for an actual novelty, originality, priority, or broader related-work judgment or score, follow [novelty-verification.md](references/novelty-verification.md) and [academic-search-operations.md](references/academic-search-operations.md): verify claim-bearing citations, search for uncited close work, apply the combination test to assembled contributions, and report a bounded conclusion with explicit verification and discovery/citation status for every decisive comparator. Include existing practical alternatives, even from different method families: do they already yield a similar or identical scientific, inferential, or decision conclusion, and what supported benefit does the proposal add? Keep intellectual novelty distinct from demonstrated practical benefit. For a precise citation-support question, verify the named record and inspect enough content to resolve the attached claim; stop at a supported answer or a stated evidence ceiling. Uncited-work discovery, novelty comparison matrices, the combination test, and search-saturation requirements apply only when that judgment requires the broader comparison. Without the required external verification and search, mark field-level novelty unassessed and score it `N/A` if scoring is in scope. Inspected supplied content can still support a packet-bounded overlap or practical-usefulness assessment under the [offline comparison boundary](references/novelty-verification.md#4-report-a-bounded-conclusion); without substantive comparator content, assess positioning clarity only. When completed external comparison was materially limited but supports a bounded judgment, label that conclusion provisional.

### 5. Diagnose the paper before listing comments

Write a private one-sentence diagnosis of the requested judgment: the claim is X, its supplied support is Y, and its strongest and most vulnerable points are A and B. Identify the most consequential remaining concern within scope, considering the repair needed and its effect on the result or contribution rather than prioritizing an issue merely because it concerns a proof or formal guarantee.

### 6. Review the relevant claim chain

For a full review, evaluate `problem -> target -> gap -> construction -> guarantee -> evidence -> interpretation -> boundary`; focused work assesses the links needed for its judgment. Use [review-framework.md](references/review-framework.md), including the plausibility screen for theory being assessed and cost/practicality checks where relevant. Do not ask for more theory or experiments by default; recommend new work only when the assessed claim lacks necessary support.

### 7. Adjudicate patterned prose

For a full or pre-submission review, revisit the recorded candidates after reconstructing the paper. Read [ai-writing-alarm.md](references/ai-writing-alarm.md) only when a recurrent candidate survives that reconstruction or the user explicitly requests an AI-writing, machine-like, templated-prose, or writing-provenance assessment. If no candidate survives, record that bounded negative screen without loading or applying the detailed classifier. When the reference is triggered, use its ordered classifications, hard thresholds, and terminal output checks: one public label when a classification is requested, alarm level kept separate from scientific severity, alternative explanations checked, and every provenance question answered with its provenance sentence.

### 8. Prioritize findings

Classify each substantive finding as Critical, Major, Moderate, or Minor using the [repair and consequence calibration](references/review-framework.md#6-priority-synthesis). Assess whether the remedy changes assumptions, conclusions, or meaningful scope, and how conventional and restrictive any added assumption is. A proof error or theorem-implementation mismatch does not by itself establish high severity; distinguish an uncertain repair from a demonstrated need for new assumptions. Report a prose, notation, or ordering issue only when it has material reviewer-facing consequence, even when the user asks for sentence-by-sentence edits; route mechanical editing quality through the aggregate report defined in [review-framework.md](references/review-framework.md) section 5 whenever writing is scored or explicitly assessed. Do not inflate severity to make the review sound rigorous.

### 9. Produce the requested review

Use the closest format in [report-formats.md](references/report-formats.md). Full or pre-submission reviews open with a compact scientific overview drawn from the existing fact base, followed by a concise verdict, the four-category scorecard, prioritized findings, supported manuscript-specific strengths, assessment boundaries, and a dependency-ordered revision sequence that ends the report. Focused reviews answer the requested question without an unrelated full scorecard or paper-level verdict. Compact diagnostic artifacts such as contribution-support ledgers, theorem-role maps, or evidence-gap tables organize findings; they are never manuscript drafts. Multiple reviewer lenses only on request, per that file.

### 10. Run reviewer QA

Apply [review-qa.md](references/review-qa.md) before returning. Grounding, provenance and support status, severity, faithful mathematical paraphrase, role boundaries, and applicable terminal output checks govern every review. Dimension-specific checks apply when that dimension is assessed or needed to support the requested judgment.

## Boundaries

- Theoretical review means claim alignment, stated-dependency reporting, proof-sketch transparency, and the plausibility screen. Allow bounded local calculations needed to assess plausibility or justify repair-based severity; do not undertake a full proof audit or certify the complete theorem or proof. Make any proof-level challenge name the exact unsupported step or contradiction.
- Do not infer novelty from the manuscript's claim alone; do not equate a verified citation record with support for the cited statement; do not describe work as prior peer-reviewed publication when only a preprint or later version was verified.
- Do not manufacture venue fit by weakening prior work or broadening implications; do not equate algorithmic performance with statistical validity; do not treat a real-data illustration without known truth as accuracy validation.
- Do not state a final editorial outcome as fact, and do not bury the central concern beneath minor comments.
- Do not label prose as AI-generated, estimate AI-use probabilities, or treat a detector score or phrase list as provenance evidence.
- Do not name the skill or narrate internal rules in the review, and do not recommend a separate later drafting or editing pass; a separately authorized outer workflow may continue after the reviewer report, but this skill does not select, route to, or perform that stage.

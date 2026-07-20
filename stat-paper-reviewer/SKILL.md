---
name: stat-paper-reviewer
description: Review, evaluate, and stress-test statistics, machine learning, econometrics, biostatistics, causal inference, and theory-and-methods manuscripts as a critical first-time reader moving sequentially through the paper. Use for full or focused referee-style reviews, pre-submission readiness checks, likely reviewer objections, source-backed novelty and citation assessment, assumption and theorem-story audits, empirical-validation critiques, venue positioning, or prioritized revision memos. Verify central novelty claims against the paper's cited references and real publications with the bundled literature-verification workflow when literature assessment is in scope. Diagnose and prioritize rather than silently rewriting the manuscript.
---

# Statistical Paper Reviewer

## Core stance

Review the paper as a statistically trained, constructive skeptic. Determine whether the manuscript establishes one coherent contribution through an aligned target, method, theory, evidence base, and interpretation.

Read first as a new reader in manuscript order. Record what is understandable at each point from information already supplied. Do not let a later explanation erase an earlier failure of motivation, definition, or logical preparation.

Distinguish manuscript facts from reviewer inference. Do not invent results, proof gaps, prior-work distinctions, experiments, citations, or venue outcomes. Mark what is not assessable from the supplied material.

Be decision-oriented without pretending to be the editor. Do not assign acceptance probabilities or numerical scores unless the user asks for them. Do not simulate multiple reviewer identities by default.

Use this skill as the default reviewer for statistical and theory-and-methods papers, including broad-interest and selective-venue assessments. This skill is self-contained for its core review task. Do not invoke or depend on another reviewer or literature-search skill. The required review and search procedures are represented in this skill's own references.

For literature verification, follow [academic-search-operations.md](references/academic-search-operations.md). Use available scholarly databases, official publication records, and full text when accessible. If no scholarly search interface is available and an OpenAlex API key is configured, use the bundled `scripts/academic_search.py` for discovery, then verify decisive records against persistent identifiers or publisher sources. A separate proof-checking capability is optional only when the user requests exhaustive proof validation.

## Route the review

Read the minimum references needed:

| Review need | Read |
|---|---|
| Full statistical or theory-and-methods review | [sequential-reading.md](references/sequential-reading.md), [review-framework.md](references/review-framework.md), [report-formats.md](references/report-formats.md), and [review-qa.md](references/review-qa.md) |
| Focused contribution, theory, assumptions, method, evidence, or exposition review | [review-framework.md](references/review-framework.md) and [review-qa.md](references/review-qa.md) |
| Novelty, related work, priority, or citation-support assessment | [novelty-verification.md](references/novelty-verification.md) and [academic-search-operations.md](references/academic-search-operations.md) |
| Reader experience, exposition order, delayed definitions, or section transitions | [sequential-reading.md](references/sequential-reading.md) |
| Output organization or revision memo | [report-formats.md](references/report-formats.md) |
| Broad significance, interdisciplinary interest, nonspecialist readability, or a selective general-science venue | [broad-interest-lens.md](references/broad-interest-lens.md) in addition to the statistical review references |

Do not apply the broad-interest lens merely because the paper is ambitious. Use it when the user names a relevant venue, requests a significance assessment, or asks whether the work reaches readers outside its immediate specialty.

## Review workflow

### 1. Establish the assessment boundary

Inspect the best available manuscript form, preferring source files when structure and notation matter. Record:

- material reviewed and material missing;
- apparent paper type and intended audience;
- stated statistical target;
- one-sentence contribution claim;
- visible method, theory, numerical, and application evidence;
- venue or decision context, if supplied.

If only an abstract or excerpt is available, provide a bounded review. Do not project missing evidence onto the full paper.

### 2. Perform the first-reader pass

Read the supplied manuscript in its displayed sequence before conducting external literature searches or reorganizing the argument mentally. Track the earliest point where the reader lacks a definition, motivation, dependency, interpretation, or promised support. If later text resolves the issue, record it as delayed resolution rather than treating the earlier passage as clear.

For a full review or a review centered on exposition order, use [sequential-reading.md](references/sequential-reading.md). Preserve this first-pass record when later analysis gives you more knowledge than a new reader would have.

### 3. Build a shared fact base

Separate three categories:

1. **Observed:** stated or shown in the manuscript.
2. **Inferred:** a reviewer interpretation supported by the manuscript.
3. **Not established:** missing, ambiguous, or requiring external verification.

Use the same fact base throughout the report. Keep first-reader observations separate from conclusions formed after cross-section comparison or external search.

### 4. Verify novelty and central citations when in scope

For a full pre-submission review, or whenever novelty, priority, related work, or citation support is being judged, read [novelty-verification.md](references/novelty-verification.md) and [academic-search-operations.md](references/academic-search-operations.md). Start from the paper's bibliography and claim-bearing citations. Verify those publications, then search for uncited close work using the best available scholarly sources or the bundled OpenAlex fallback.

Distinguish bibliographic existence, support for the cited statement, and substantive overlap with the claimed contribution. Cite the real publications used in the assessment. If tools, full text, or adequate metadata are unavailable, state the search boundary and keep the novelty conclusion provisional.

### 5. Diagnose the paper before listing comments

Write a private one-sentence diagnosis:

> The paper claims **X** through **Y**, but its current case is strongest at **A** and most vulnerable at **B**.

Identify the earliest high-consequence failure. Prefer issues that affect validity, contribution identity, theorem-method alignment, evidentiary support, or interpretation over local stylistic preferences.

### 6. Review the full claim chain

Evaluate:

`problem -> target -> gap -> construction -> guarantee -> evidence -> interpretation -> boundary`

Check whether each link supports the next. Apply the axes and questions in [review-framework.md](references/review-framework.md). Do not ask for more theory or experiments by default. Recommend new work only when a central claim lacks necessary support.

### 7. Prioritize findings

Classify each substantive finding:

- **Critical:** threatens correctness, validity, or the central claim.
- **Major:** materially weakens contribution, support, or reviewer confidence.
- **Moderate:** impairs interpretation, navigation, reproducibility, or positioning.
- **Minor:** local polish that does not affect the paper's case.

For every Critical or Major finding, give:

- location or scope;
- manuscript evidence;
- why it matters;
- concrete revision direction;
- whether the remedy is a rewrite, reanalysis, new evidence, new theory, citation verification, or author judgment.

Do not inflate severity to make the review sound rigorous.

### 8. Produce the requested review

Use the closest format in [report-formats.md](references/report-formats.md). Default to one integrated review with a concise verdict, strengths, prioritized findings, likely objections, and a revision sequence.

When the underlying scientific content is present but its framing is ineffective, make the advice executable with an illustrative replacement paragraph, contribution list, theorem roadmap, comparison table, or experiment-table design. Do not use proposed prose to conceal missing theory, evidence, or verification.

If the user requests multiple reviewer perspectives, vary only the stated evaluative emphasis unless actual specialist roles and evidence are supplied. Consolidate overlap in a synthesis and do not present weighted lenses as independent factual confirmation.

### 9. Run reviewer QA

Apply [review-qa.md](references/review-qa.md). Check that every strong judgment is traceable to manuscript evidence, supplied context, or a verified source. Separate exposition concerns from proof-correctness claims.

## Relationship to author-side revision

Use this skill to diagnose and prioritize. Author-side drafting is a separate task. If `stat-paper-writing` is available, it can implement authorized revisions, but this reviewer remains functional without it.

When the user asks for both review and revision:

1. complete the reviewer diagnosis first;
2. identify which findings can be repaired without new scientific work;
3. revise only the authorized material;
4. report unresolved findings that require evidence or author judgment.

Do not silently convert a requested review into a rewritten manuscript.

## Boundaries

- Do not call a proof correct unless every nontrivial step and dependency has been checked.
- Do not infer novelty from the manuscript's own claim alone.
- Do not equate a verified citation record with verification that the cited publication supports the manuscript's statement.
- Do not describe a publication as prior peer-reviewed work when only a preprint or later version was verified.
- Do not manufacture venue fit by weakening prior work or broadening implications.
- Do not equate algorithmic performance with statistical validity.
- Do not treat a real-data illustration without known truth as accuracy validation.
- Do not state a final editorial outcome as fact.
- Do not bury the central concern beneath an exhaustive list of minor comments.

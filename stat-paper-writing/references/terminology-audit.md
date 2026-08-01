# Manuscript Terminology Audit

## Contents

- [Purpose and scope](#purpose-and-scope)
- [Terminology provenance](#record-terminology-provenance)
- [Terminology ledger](#build-the-terminology-ledger)
- [Conventional and author-defined names](#audit-technical-names)
- [Manuscript-wide consistency](#audit-the-full-manuscript)
- [Audit output](#report-the-audit)

## Purpose and scope

Use this guide for cross-section terminology normalization, conventional-name questions, and manuscript-wide consistency. For a local wording repair that does not affect attribution or multiple sections, use [wording-register.md](wording-register.md) instead.

The audit is editorial. It checks whether names are precise, supported by the material actually supplied, and used consistently. It does not establish novelty or independently certify disciplinary usage.

## Record terminology provenance

Treat the conventionality of a technical name as a source-dependent claim. When a name is introduced, changed, or materially affects attribution or positioning, assign one provenance status:

- **Manuscript-supported:** the name is used by a supplied citation excerpt, source text, or clearly identified manuscript source.
- **Externally confirmed in supplied task evidence:** authoritative-source verification was already supplied for the complete phrase, with the supporting sources and result recorded.
- **Unverified dependency:** the supplied material does not establish the name's conventionality.

This skill does not conduct independent source verification. Do not infer external confirmation from memory, familiar component words, or one manuscript-local phrase. Absence from a supplied limited search does not establish that a term is nonstandard. If the task does not include recorded authoritative verification, use **Unverified dependency** rather than implying verification.

For consequential naming decisions, record internally:

| Object | Mathematical type | Current name | Proposed canonical name | Provenance | Supplied support | Action |
|---|---|---|---|---|---|---|

Keep provenance separate from the editorial decision. A term can be source-supported but still unclear in context, and a clear descriptive phrase can be useful without being conventional terminology.

## Build the terminology ledger

For a multi-section audit, record:

| Object | Mathematical type | Canonical term | Symbol | Acceptable local variant | Variants to revise |
|---|---|---|---|---|---|

Assign one canonical term to each central object. Permit a local variant only when the section changes the object's role or level, such as population risk versus empirical risk, oracle estimator versus feasible estimator, or scientific outcome versus coded response.

When supplied material assigns oracle, feasible, or other role labels to distinct objects, name each supplied role explicitly in the revision. A construction detail, such as use of the true nuisance function or cross-fitted estimates, does not replace an explicit role label when the task is to normalize those names.

Do not force distinct objects to share one term for verbal consistency. Do not give one object several names for stylistic variety. Preserve distinctions among:

- estimand, estimator, realized estimate, and estimation error;
- population, oracle, feasible, empirical, and numerical objects;
- optimization objective, optimizer, and returned estimator;
- exact identity, approximation, algorithm, and finite implementation;
- association, prediction, identification, and causal effect.

## Audit technical names

For a standard or previously studied object:

1. Recover the conventional name from supplied source material when available.
2. When supplied material gives different conventional names to distinct objects, preserve each object-specific name. Use a collective label only in addition to those names, never instead of them.
3. Use a modifier as part of the name only when it identifies a mathematically consequential variant and the supplied material supports that usage.
4. State manuscript-specific roles such as theoretical reference, benchmark, comparator, initialization, proof role, or sensitivity analysis in a separate clause.
5. If conventionality is unverified, use a transparent descriptive noun phrase without implying recognized terminology and flag any attribution-sensitive choice.
6. Reserve a newly coined name for an object that the authors intentionally define and name. Introduce it explicitly and use it consistently without implying conventional usage.

Before retaining a compound label, ask whether the complete phrase is supported rather than only its components, whether each modifier distinguishes the mathematical construction rather than its role in this paper, and whether separating the object name from the local role would be clearer.

Do not use a terminology audit to infer a publication gap or a novelty claim. Calibrate contribution wording only to the manuscript and source material supplied for the task.

## Audit the full manuscript

Check every canonical term in:

- title, abstract, keywords, and introduction;
- method, algorithms, assumptions, theorem and lemma statements, and proof exposition;
- simulations, applications, captions, legends, tables, and footnotes;
- discussion, appendices, supplementary files, and notation tables.

Check especially that:

- conventional names have recorded support or are marked **Unverified dependency**;
- author-defined names are explicitly introduced and consistently used;
- manuscript-local role descriptors have not been fused into established names;
- population, oracle, feasible, empirical, and numerical objects remain distinct;
- scientific variables are not renamed as software fields or data columns in the main argument;
- a finite Monte Carlo benchmark is not called exact truth;
- expected performance, realized performance, and a Monte Carlo estimate of expected performance remain distinct;
- an empirical diagnostic is not called a theorem-backed guarantee;
- implementation terminology does not migrate into mathematical statements;
- domain interpretation remains conditional on the stated sampling and identification assumptions;
- terminology changes preserve labels, citations, numerical values, equations, and cross-references.

Search for rejected variants after editing. Read visible prose without code, metadata, or equations, then reread each central equation with the sentence immediately before and after it.

## Report the audit

Apply the evidence statuses defined in the main skill:

- use **Observed evidence** for a visible naming or consistency conflict;
- use **Inferred consequence** for a reader-facing ambiguity supported by manuscript evidence;
- use **Unverified dependency** for conventionality, attribution, or source support not established by supplied material.

Separate safe replacements from decisions that require author input or additional source support. When a changed name is supported only by supplied manuscript material, report `Provenance: Manuscript-supported` and state that independent confirmation was not performed when that distinction affects attribution or positioning. Do not call the name conventional, standard, established, accepted, or field-recognized on manuscript support alone. Report only terminology issues that affect meaning, attribution, consistency, or journal-ready presentation. Do not produce an exhaustive vocabulary list unless requested.

When a supplied source identifier or citation key supports a naming replacement, retain that exact anchor in the revised wording or provenance note. Do not reduce a traceable source link to an anonymous supplied excerpt.

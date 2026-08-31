# Statistical Paper Skills

## Overview

This collection provides three complementary skills for statistics, machine
learning, econometrics, biostatistics, and related research papers. Use
`stat-paper-writing` for author-side writing, `stat-paper-reviewer` for
critical manuscript evaluation, and `stat-paper-proofcheck` for rigorous proof
verification. The skills can be used independently or in sequence.

| Skill | Version |
|---|---|
| `stat-paper-writing` | v1.2 |
| `stat-paper-reviewer` | v1.2 |
| `stat-paper-proofcheck` | v1.2 |

## stat-paper-writing

Drafts, restructures, and polishes manuscript text while preserving the
author's claims, notation, evidence, citations, and mathematical meaning. Use
it for writing and revision, not referee judgment or proof validation.

Usage: `Use $stat-paper-writing to revise this methods section without changing its mathematical claims.`

## stat-paper-reviewer

Reviews a manuscript as a critical first-time reader, focusing on contribution,
methodology, theory, evidence, interpretation, novelty, and likely reviewer
concerns. It diagnoses problems and recommends priorities without rewriting the
paper.

Usage: `Use $stat-paper-reviewer to review this manuscript and identify the most important issues.`

## stat-paper-proofcheck

Performs a source-locked, line-by-line audit of formal proofs, including
assumptions, dependencies, inference steps, counterexamples, and downstream
consequences. This is a rigorous workflow and must be invoked explicitly.

Usage: `Use $stat-paper-proofcheck to audit this theorem and its dependency closure line by line.`

## Runtime and tests

The proofcheck and writing helpers and tests require Python 3.10 or later.
The reviewer helper and tests also require Python 3.10 or later.

For Full writing audits with PDF sources, install `pypdf` (preferred) or
`PyPDF2`. If neither reader is available, or automatic page inspection fails,
supply a trusted count with `--pdf-page-count "SOURCE=N"`.

Run the writing skill tests from the repository root:

```text
python -m unittest discover -s stat-paper-writing/tests
```

Run the reviewer skill tests from the repository root:

```text
python -m unittest discover -s stat-paper-reviewer/tests
```

Run the proofcheck skill tests from the repository root:

```text
python -m unittest discover -s stat-paper-proofcheck/tests -p "test_*.py"
```

The reviewer behavioral cases are defined in
`stat-paper-reviewer/evals/evals.json`. Historical single-run evaluation
artifacts are retained under `stat-paper-reviewer/evals/results/` as
exploratory evidence only. For a release benchmark, run at least three
independent repetitions per configuration and record the executor and grader
models, repository commit, protocol digest, and any literature-search evidence.
The deterministic test command above does not run that behavioral benchmark.

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
| `stat-paper-proofcheck` | v1.5 |

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

Use this skill by name for a rigorous proof audit. It locks the source, inventories theorems and assumptions, maps dependencies, checks every in-scope proof unit from prerequisites to dependents, independently verifies every unit, and produces a concise evidence-backed summary. Example: `Use $stat-paper-proofcheck to audit this theorem and its dependency closure line by line.`

The HTML report begins with the overall finding, key issues, affected results,
and recorded repair directions. Its paper overview groups theorems and lemmas
by their manuscript identity, with detailed conclusions and source evidence
available on demand. Unresolved findings remain distinct from confirmed defects,
and each repair retains its own target, scientific cost, and verification status.

The current revision also tightens multi-file theorem identification, gives
early diagnostics for inactive TeX material and selected chapter builds, and
allows exact source lookup while review annotations are still unfinished.
These changes preserve the existing proof and independent-review requirements.

### Install locally in Codex

Use a shared Python 3.10 or newer installation. For offline typeset LaTeX in
HTML reports, install `latex2mathml` once into that same interpreter. For example,
with shared Python 3.14 on Windows:

```powershell
py -3.14 -m pip install --user latex2mathml
```

The scripts-folder PATH warning from pip does not affect proofcheck: it imports
the package through Python. Source inspection and validation use the standard
library; PDF preparation additionally needs a shared PDF reader/rendering tool.
A missing math converter produces an explicit limitation rather than a hidden
download. Full audits also need independent model contexts and can take
substantial time; they are non-formal reviews, not proof-assistant certificates.

Keep the sole Codex installation at `~/.codex/skills/stat-paper-proofcheck`.
From a validated repository
release, use the small [installation helper](tools/install_proofcheck.py) with
the same shared interpreter used for the audit:

```powershell
py -3.14 -B ./tools/install_proofcheck.py --source ./stat-paper-proofcheck
if ($LASTEXITCODE -ne 0) { throw 'Installation did not complete; read its diagnostic.' }
```

Add `--upgrade` for an intentional replacement. The helper checks for duplicates
in `~/.agents/skills` and `~/.claude/skills`, validates the bundled reference,
excludes `tests/`, `evals/`, bytecode, and development caches, and stages the
runtime package. Tests and release evaluations stay in the repository. An
upgrade preserves the previous folder under `~/.codex/skill-backups`, outside
skill discovery. It then checks every runtime file hash and the installed
reference's FINAL/current/usable delivery. It does not merge versions or remove
other installations. If duplicates exist, preserve and relocate the identified
copies before retrying. `--user-root` selects a temporary user directory for a
safe installation exercise; normally omit it.

Invoke `$stat-paper-proofcheck` by name in the next turn; if discovery has not
refreshed, restart Codex. The runtime and packages remain shared. `doctor`
reports typesetting availability early; missing `latex2mathml` keeps explicit
LaTeX fallback and does not install a package automatically.

For source preparation and supported proof layouts, see the
[source-layout guidance](stat-paper-proofcheck/references/source-layout-diagnostics.md).
A source-selection warning needs review before mathematical checking; a clean
parser result does not certify that every proof is present or correct.

The [release record](architecture-proofcheck/tightening-release-2026-09-10/STATUS.md)
documents the current repairs and verification.

### Preparing a versioned release

Select repository release contents deliberately: the `stat-paper-proofcheck`
source (including scripts, references, templates, tests, evaluation resources,
and current bundled reference evidence), this guide and installer, active architecture
documents, and the acceptance receipts/logs supporting that version. Leave bulk
temporary paper runs, `before-skill` snapshots, copied working trees, bytecode,
and development caches out of ordinary distribution. The local `archived/`
folder is ignored by Git and is outside the installed skill. It holds retired
example presentations and preserved pre-cleanup snapshots. The current reference
retains historical records required to authenticate its reviewed evidence.

Review selected paths and sizes before staging; do not stage the entire working
tree with `git add -A`. For selected sealed evidence, retain `-text` attributes
so Git does not normalize authenticated bytes. The current package reference
already has that rule in [.gitattributes](.gitattributes); extend it only to
additional selected sealed artifacts. Run the package suite and current
reference delivery check on the exact release tree, then exercise installation.
When a release is actually committed, record its commit alongside the existing
content identities in the release receipt. Local acceptance does not imply a
commit, tag, or distributed release has been created.

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

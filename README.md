# Statistical Paper Skills

## Overview

This collection provides three complementary skills for statistics, machine
learning, econometrics, biostatistics, and related research papers. Use
`stat-paper-writing` for author-side writing, `stat-paper-reviewer` for
critical manuscript evaluation, and `stat-paper-proofcheck` for rigorous proof
verification. The skills can be used independently or in sequence.

| Skill | Version |
|---|---|
| `stat-paper-writing` | v1.5.1 |
| `stat-paper-reviewer` | v1.2 |
| `stat-paper-proofcheck` | v2.0.0 |

## stat-paper-writing

Use this skill for drafting, restructuring, polishing, notation cleanup, and main-text or supplement coordination. Example: `Use $stat-paper-writing to revise this methods section while preserving every mathematical claim.`

For complete papers, v1.5.1 reads and plans around the reader's understanding,
writes focused sections, then reconciles the argument and rendered presentation.
It transforms research-note prose while preserving scientific claims, uses
targeted disciplinary examples when needed, and keeps local edits lightweight.
Drafting uses the existing sentence and paragraph guidance; methods accounts
are checked for a reconstructible procedure at the intended research level.
It explains the research obstacle and supplied structural insight without
routine background instruction. Whole-manuscript reviews use concise feedback;
persistent audit records are optional and use the existing tracking helper.
Tracked reports default to concise output; request `--report-detail detailed`
at initialization for a procedural audit trail.

The proofcheck and writing helpers and tests require Python 3.10 or newer from
a shared installation. The writing audit uses `pypdf` or `PyPDF2` for automatic
PDF page counts, or accepts `--pdf-page-count "SOURCE=N"` from a trusted count.
Run its checks with `python -m unittest discover -s stat-paper-writing/tests`.

## stat-paper-reviewer

Reviews a manuscript as a critical first-time reader, focusing on contribution,
methodology, theory, evidence, interpretation, novelty, and likely reviewer
concerns. It diagnoses problems and recommends priorities without rewriting the
paper.

Usage: `Use $stat-paper-reviewer to review this manuscript and identify the most important issues.`

## stat-paper-proofcheck

Use this skill by name for a rigorous, non-formal proof audit. Version 2.0 registers
source-linked proof items and dependencies in a local database. The coordinator builds and
refines the graph and makes scientific decisions. A small controller prepares bounded batches,
validates structured responses, saves progress and recovers interrupted work.

The Archify reader shows major results and exposes intermediate reasoning and recorded checks
through their connections. Local argument validity, upstream support and statement truth remain
separate. Existing v1.5 audit folders retain their legacy workflow until explicitly imported.

Example: `Use $stat-paper-proofcheck to audit this theorem and its dependency closure.`
Start with the [database workflow](stat-paper-proofcheck/references/database-audit.md) and
[coordinator instructions](stat-paper-proofcheck/references/controller-workflow.md).
The [v2.0 release record](architecture-proofcheck/release-v2.0.md) contains validation evidence
and remaining browser and large-paper evaluation limits.

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

### Validate the v2.0 database workflow

The shared core is maintained in `shared/paper_core` and shipped identically in both skills.
For a clean development checkout, clone the companion repository at its matching release tag:

```text
git clone --branch v2.0 https://github.com/rqzhu-aide/archify-proofs-overview.git archify-proofs-overview
python -B tools/build_paper_core_bundles.py --check
python -B -m unittest discover -s tests/new_format
python -B -m unittest discover -s archify-proofs-overview/tests
python -B -m unittest discover -s tools -p test_install_proofcheck.py
```

Use the shared Python and Node installations. The separate companion checkout is needed for
cross-package development checks; each installed skill contains its own complete runtime.

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

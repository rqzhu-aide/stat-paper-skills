# Statistical paper skills

This repository maintains four skills for statistical and machine-learning papers. Each is used only when the user explicitly invokes it by name.

| Skill | Version | Main use |
|---|---|---|
| `stat-write-style` | v1.6.1 | Draft and revise manuscript exposition and presentation |
| `stat-paper-review` | v1.2.1 | Give a critical, evidence-backed manuscript review |
| `stat-proof-write` | v0.3.1 | Draft or clarify a mathematical proof |
| `stat-proof-check` | v2.3.0 | Audit written mathematical arguments without silently repairing them |

Use `$stat-write-style`, `$stat-paper-review`, `$stat-proof-write`, or `$stat-proof-check` to invoke the corresponding skill. Their `agents/openai.yaml` files disable implicit invocation. Proof writing and proof checking are separate tasks: drafting a proof does not provide an independent audit.

## Repositories and folders

```text
stat-paper-skills/                 this repository
  stat-write-style/               skill
  stat-paper-review/              skill
  stat-proof-write/               skill
  stat-proof-check/               skill
  shared/paper_core/              maintained common backend
  architecture/                  current proof-check architecture
  tests/new_format/              shared backend and package tests
  tools/                         bundle builder and installer
  proof-graphify/                separate Git checkout, ignored here
  archived/                      local historical material, ignored here
```

This repository maps to [stat-paper-skills](https://github.com/rqzhu-aide/stat-paper-skills). The nested, ignored `proof-graphify/` checkout maps to its own [proof-graphify repository](https://github.com/rqzhu-aide/proof-graphify), which owns that skill and its `architecture/` folder. Keep the two Git histories and remotes separate. The nested checkout supports cross-package development; installed skills do not require it.

The current [proof-check architecture](architecture/README.md) describes the shared backend and audit workflow. Proof Graphify's [architecture](https://github.com/rqzhu-aide/proof-graphify/tree/main/architecture) describes its selective overview and reader. Completed revision plans, audits, receipts, and superseded designs are kept in the local `archived/` folder, outside the remote and skill discovery.

## Skill use and installation

`stat-write-style` covers author-side drafting, restructuring, polishing, notation, and main/supplement coordination. Example: `Use $stat-write-style to revise this methods section while preserving its scientific claims.` The proofcheck and writing helpers and tests require Python 3.10 or newer from a shared installation. The writing audit uses `pypdf` or `PyPDF2` for automatic page counts, or accepts `--pdf-page-count "SOURCE=N"` from a trusted count. Run its checks with `python -m unittest discover -s stat-write-style/tests`.

`stat-paper-review` provides referee-style diagnosis and edit specifications without rewriting the manuscript. Example: `Use $stat-paper-review to review this paper as a critical statistical reader.` The reviewer helper and tests also require Python 3.10 or later from a shared installation. Run its checks with `python -m unittest discover -s stat-paper-review/tests`.

`stat-proof-write` develops readable proofs with explicit derivations and local mathematical justification. Example: `Use $stat-proof-write to expand this compressed argument.` It does not replace proof checking or general manuscript editing.

`stat-proof-check` performs a scoped, non-formal audit of exact claims, substantive inferences, dependencies, and written proof coverage. Example: `Use $stat-proof-check to audit this theorem and its prerequisite arguments.` Start with the [database workflow](stat-proof-check/references/database-audit.md). The legacy v1.5 workflow remains available for existing audit folders and retains its original protocol identifiers.

Install the first three skills from their source folders under a user-wide skill root such as `~/.agents/skills/`. The proof-check package includes a bundled backend and has a validated [installer](tools/install_proofcheck.py):

```powershell
python -B tools/install_proofcheck.py --source stat-proof-check --target agents --target claude
```

The installer checks the bundle, stages the package, and verifies each installed copy. Old skill names must be moved outside skill discovery first. The proof-check Claude installation also needs `"stat-proof-check": "user-invocable-only"` under `skillOverrides`. Use a shared Python installation; do not create a project-local environment. Optional offline LaTeX conversion uses a shared `latex2mathml` installation. If the new names are not visible immediately, refresh skill discovery or restart Codex.

## Backend and validation

[`shared/paper_core`](shared/paper_core) is the maintained source of the common SQLite backend. [`tools/build_paper_core_bundles.py`](tools/build_paper_core_bundles.py) builds byte-identical, self-contained bundles for `stat-proof-check` and the separate Proof Graphify checkout. Do not edit a generated bundle by hand.

For cross-package development, check out Proof Graphify at `proof-graphify/` and run:

```text
python -B tools/build_paper_core_bundles.py --check
python -B -m unittest discover -s tests/new_format
python -B -m unittest discover -s stat-proof-check/tests
python -B -m unittest discover -s tools -p test_install_proofcheck.py
python -B -m unittest discover -s proof-graphify/tests
```

The backend and package checks assess software behavior. A complete mathematical audit and live browser review require separate evidence. The two repositories can move together without requiring either installed skill to import runtime code from the other checkout.

[MIT license](LICENSE)

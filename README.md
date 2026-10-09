# Statistical paper skills

This repository maintains four skills for statistical and machine-learning papers. Each is used only when the user explicitly invokes it by name.

| Skill | Version | Main use |
|---|---|---|
| `stat-write-style` | v1.6.1 | Draft and revise manuscript exposition and presentation |
| `stat-paper-review` | v1.2.1 | Give a critical, evidence-backed manuscript review |
| `stat-proof-write` | v0.3.1 | Draft or clarify a mathematical proof |
| `stat-proof-check` | v3.0.11 | Audit written mathematical arguments without silently repairing them |

Use `$stat-write-style`, `$stat-paper-review`, `$stat-proof-write`, or `$stat-proof-check` to invoke the corresponding skill. Their `agents/openai.yaml` files disable implicit invocation. Proof writing and proof checking are separate tasks: drafting a proof does not provide an independent audit.

## Repositories and folders

```text
stat-paper-skills/                 local grouping folder
  stat-paper-skills/              this Git repository
    stat-write-style/             skill
    stat-paper-review/            skill
    stat-proof-write/             skill
    stat-proof-check/             v3 skill and maintained backend
    shared/paper_core/            retained v2 shared backend
    architecture/                current proof-check architecture
    tests/new_format/            legacy shared backend tests
    tools/                       legacy bundle builder and installer
    archived/                    local historical material, ignored by Git
  proof-graphify/                 separate Git repository and skill
```

This repository maps to [stat-paper-skills](https://github.com/rqzhu-aide/stat-paper-skills). The sibling `../proof-graphify/` checkout maps to its own [proof-graphify repository](https://github.com/rqzhu-aide/proof-graphify), which owns that skill and its `architecture/` folder. The two repositories have separate Git histories and remotes. The sibling checkout supports cross-package development; installed skills do not require it.

The [proof-check architecture index](architecture/README.md) identifies the maintained v3 package and labels retained change records and proposals. Proof Graphify's [architecture](https://github.com/rqzhu-aide/proof-graphify/tree/main/architecture) describes its selective overview and reader. Local backups and experiment outputs stay outside the remote and skill discovery.

## Skill use and installation

`stat-write-style` covers author-side drafting, restructuring, polishing, notation, and main/supplement coordination. Example: `Use $stat-write-style to revise this methods section while preserving its scientific claims.` The proofcheck and writing helpers and tests require Python 3.10 or newer from a shared installation. The writing audit uses `pypdf` or `PyPDF2` for automatic page counts, or accepts `--pdf-page-count "SOURCE=N"` from a trusted count. Run its checks with `python -m unittest discover -s stat-write-style/tests`.

`stat-paper-review` provides referee-style diagnosis and edit specifications without rewriting the manuscript. Example: `Use $stat-paper-review to review this paper as a critical statistical reader.` The reviewer helper and tests also require Python 3.10 or later from a shared installation. Run its checks with `python -m unittest discover -s stat-paper-review/tests`.

`stat-proof-write` develops readable proofs with explicit derivations and local mathematical justification. Example: `Use $stat-proof-write to expand this compressed argument.` It does not replace proof checking or general manuscript editing.

`stat-proof-check` performs a scoped, non-formal audit of exact claims, substantive inferences, dependencies, and written proof coverage. Example: `Use $stat-proof-check to audit this theorem and its prerequisite arguments.` Start with the [database workflow](stat-proof-check/references/database-audit.md). The legacy v1.5 workflow remains available for existing audit folders and retains its original protocol identifiers.

Install the first three skills from their source folders under a user-wide skill root such as `~/.agents/skills/`. The proof-check package includes a bundled backend and has a validated [installer](tools/install_proofcheck.py):

```powershell
python -B tools/install_proofcheck.py --source stat-proof-check --target agents --target claude
```

The installer checks the bundle, stages the package, and verifies each installed copy. Old skill names must be moved outside skill discovery first. The proof-check Claude installation also needs `"stat-proof-check": "user-invocable-only"` under `skillOverrides`. Use a shared Python installation; do not create a project-local environment. Optional offline LaTeX conversion uses a shared `latex2mathml` installation. If the new names are not visible immediately, refresh skill discovery or restart the host application.

## Backend and validation

[`stat-proof-check/scripts/paper_core`](stat-proof-check/scripts/paper_core) is the maintained v3 backend. The formal `stat-proof-check` directory replaces the former `stat-proof-check-v3` development directory. Refresh its content manifest after runtime edits with `python -B stat-proof-check/scripts/build_manifest.py`; use `--check` for read-only verification. The [implementation boundary](stat-proof-check/IMPLEMENTATION.md) and [validation record](stat-proof-check/VALIDATION.md) document the current release.

Run the current proof-check release checks with a shared Python installation:

```text
python -B stat-proof-check/scripts/build_manifest.py --check
python -B -m unittest discover -s stat-proof-check/tests -p "test_v3*.py"
python -B -m unittest discover -s stat-proof-check/tests -p test_skill_structure.py
python -B -m unittest discover -s tools -p test_install_proofcheck.py
python -B -m unittest discover -s tools -p test_bundle_targets.py
```

The retained `shared/paper_core`, `tests/new_format` and shared-bundle command describe the older common backend. Their byte-equality checks are not v3 release checks, and that builder no longer targets proof-check. Proof Graphify is maintained separately. The backend and package checks assess software behavior; mathematical accuracy and whole-paper performance require separate evidence.

[MIT license](LICENSE)

# Statistical paper skills

This repository provides four skills for statistical and machine-learning papers. It maintains the three writing and review skills and includes a duplicate copy of `stat-proof-check` from the [Proof Graphify repository](https://github.com/rqzhu-aide/proof-graphify). Each skill is used only when the user explicitly invokes it by name.

`stat-proof-check` is an extended version of [Proof Graphify](https://github.com/rqzhu-aide/proof-graphify) that builds more detailed items within a proof and uses LLMs to check their reasoning and dependencies. The two skills share a common core and presentation interface. Its checks are non-formal: it does not produce a Lean proof or provide formal verification.

| Skill | Version | Main use |
|---|---|---|
| `stat-write-style` | v1.6.4 | Draft and revise manuscript exposition and presentation |
| `stat-paper-review` | v1.2.7 | Give a critical, evidence-backed manuscript review |
| `stat-proof-write` | v0.3.1 | Draft or clarify a mathematical proof |
| `stat-proof-check` | v3.3.9 | Audit written mathematical arguments; duplicate of the upstream Proof Graphify package |

Use `$stat-write-style`, `$stat-paper-review`, `$stat-proof-write`, or `$stat-proof-check` to invoke the corresponding skill. Their `agents/openai.yaml` files disable implicit invocation. Drafting a proof does not provide an independent audit.

## Repositories and folders

```text
stat-paper-skills/                 local grouping folder
  stat-paper-skills/              this Git repository
    stat-write-style/             manuscript-writing skill
    stat-paper-review/            review skill
    stat-proof-write/             proof-writing skill
    stat-proof-check/             duplicate of the upstream proof-audit skill
    archived/                    local historical material, ignored by Git
  proof-graphify/                 separate Git repository
    proof-graphify/               overview skill
    stat-proof-check/             maintained proof-audit skill
    shared/paper_core/            maintained common backend
```

This repository maps to [stat-paper-skills](https://github.com/rqzhu-aide/stat-paper-skills). The [Proof Graphify repository](https://github.com/rqzhu-aide/proof-graphify) remains the source of truth for `stat-proof-check`, `proof-graphify`, and their shared backend. The `stat-proof-check/` directory here is an unchanged copy for convenient distribution with the other statistical-paper skills. See the upstream [repository guide](https://github.com/rqzhu-aide/proof-graphify/blob/main/README.md), [audit guide](https://github.com/rqzhu-aide/proof-graphify/blob/main/stat-proof-check/README.md), and [architecture index](https://github.com/rqzhu-aide/proof-graphify/blob/main/architecture/README.md). The repositories keep separate Git histories and remotes.

## Skill use and installation

`stat-write-style` covers author-side drafting, restructuring, polishing, notation, and main/supplement coordination. It preserves supplied proof detail and the manuscript's template during local and whole-paper edits. Example: `Use $stat-write-style to revise this methods section while preserving its scientific claims.` Its helpers and tests require shared Python 3.10+. The writing audit uses `pypdf` or `PyPDF2` for automatic page counts, or accepts `--pdf-page-count "SOURCE=N"` from a trusted count. Run its checks with `python -m unittest discover -s stat-write-style/tests`.

`stat-paper-review` provides referee-style diagnosis and edit specifications without rewriting the manuscript. Severity reflects the repair needed, its scientific consequence, and the conventionality and restriction of any added assumptions. Novelty and practical usefulness are compared with existing methods, including alternatives that already give similar conclusions. Focused reviews cover the requested question and necessary dependencies. Multiple source files alone do not require a durable review bundle; delegation, durable resumption, and requested execution records do. Example: `Use $stat-paper-review to review this paper as a critical statistical reader.` Its helper and tests require shared Python 3.10+. Run its checks with `python -m unittest discover -s stat-paper-review/tests`.

`stat-proof-write` develops readable proofs with explicit derivations and local mathematical justification. Example: `Use $stat-proof-write to expand this compressed argument.` It does not replace proof checking or general manuscript editing.

`stat-proof-check` performs a scoped, non-formal audit of exact claims, substantive inferences, dependencies, and written proof coverage. Example: `Use $stat-proof-check to audit this theorem and its prerequisite arguments.` Start with its [skill instructions](stat-proof-check/SKILL.md) and [database workflow](stat-proof-check/references/database-audit.md). New audits start from the manuscript in their own database; an overview or drafted proof does not count as independent audit evidence.

Install each skill from its named source folder under a user-wide skill root such as `~/.agents/skills/`. Preserve explicit invocation settings; Claude installations need the corresponding `"user-invocable-only"` skill overrides. Use shared runtimes and packages rather than project-local environments. Refresh skill discovery or restart the host if a newly installed skill is not visible.

For proof audits, install the complete local `stat-proof-check/` directory or the [upstream package](https://github.com/rqzhu-aide/proof-graphify/tree/main/stat-proof-check) under the same `stat-proof-check` name. Choose one copy per host skill directory. Both contain the same bundled runtime and work without a sibling repository. Preserve `allow_implicit_invocation: false` and Claude's `"stat-proof-check": "user-invocable-only"` override. Use shared Python 3.10+ and Node.js; optional offline LaTeX conversion uses shared `latex2mathml`.

## Proof Check mirror maintenance

Make Proof Check and shared-core changes in the Proof Graphify repository, validate them there, then refresh this entire skill directory from its `stat-proof-check/` package. Keep the copied files identical, including the bundled core and manifest. This copy is a release snapshot; updates are copied manually from validated upstream releases.

The bundle builder, installer, shared source, complete regression fixtures, and architecture records are maintained upstream. Repository-relative maintenance references in the copied documentation and tests refer to that upstream checkout; run the full maintainer checks there. The mirrored runtime can be checked locally with:

```text
python -B stat-proof-check/scripts/paper_audit.py version
python -B stat-proof-check/scripts/build_manifest.py --check
```

[MIT license](LICENSE)

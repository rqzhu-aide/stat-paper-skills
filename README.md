# Statistical paper skills

This repository provides three writing and review skills for statistical and machine-learning papers. Each skill is used only when the user explicitly invokes it by name.

Proof checking and graphical proof visualization have moved to the [Proof Graphify repository](https://github.com/rqzhu-aide/proof-graphify). Install and use those skills from that collection; they are no longer bundled here.

| Skill | Version | Main use |
|---|---|---|
| `stat-write-style` | v1.6.5 | Draft and revise manuscript exposition and presentation |
| `stat-paper-review` | v1.2.7 | Give a critical, evidence-backed manuscript review |
| `stat-proof-write` | v0.3.1 | Draft or clarify a mathematical proof |

Use `$stat-write-style`, `$stat-paper-review`, or `$stat-proof-write` to invoke the corresponding skill. Their `agents/openai.yaml` files disable implicit invocation. Drafting a proof does not provide an independent audit.

## Repository layout

```text
stat-paper-skills/                this Git repository
  stat-write-style/              manuscript-writing skill
  stat-paper-review/             review skill
  stat-proof-write/              proof-writing skill
  archived/                     local historical material, ignored by Git
```

## Skill use and installation

`stat-write-style` covers author-side drafting, restructuring, polishing, notation, and main/supplement coordination. It preserves supplied proof detail and the manuscript's template during local and whole-paper edits. Example: `Use $stat-write-style to revise this methods section while preserving its scientific claims.` Its helpers and tests require shared Python 3.10+. The writing audit uses `pypdf` or `PyPDF2` for automatic page counts, or accepts `--pdf-page-count "SOURCE=N"` from a trusted count. Run its checks with `python -m unittest discover -s stat-write-style/tests`.

`stat-paper-review` provides referee-style diagnosis and edit specifications without rewriting the manuscript. Severity reflects the repair needed, its scientific consequence, and the conventionality and restriction of any added assumptions. Novelty and practical usefulness are compared with existing methods, including alternatives that already give similar conclusions. Focused reviews cover the requested question and necessary dependencies. Multiple source files alone do not require a durable review bundle; delegation, durable resumption, and requested execution records do. Example: `Use $stat-paper-review to review this paper as a critical statistical reader.` Its helper and tests require shared Python 3.10+. Run its checks with `python -m unittest discover -s stat-paper-review/tests`.

`stat-proof-write` develops readable proofs with explicit derivations and local mathematical justification. Example: `Use $stat-proof-write to expand this compressed argument.` It does not replace proof checking or general manuscript editing.

Install each skill from its named source folder under a user-wide skill root such as `~/.agents/skills/`. Preserve explicit invocation settings; Claude installations need the corresponding `"user-invocable-only"` skill overrides. Use shared runtimes and packages rather than project-local environments. Refresh skill discovery or restart the host if a newly installed skill is not visible.

[MIT license](LICENSE)

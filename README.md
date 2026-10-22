# Statistical paper skills

This repository provides three writing and review skills for statistical and machine-learning papers. Each skill is used only when the user explicitly invokes it by name.

Proof checking and graphical proof visualization have moved to the [Proof Graphify repository](https://github.com/rqzhu-aide/proof-graphify). Install and use those skills from that collection; they are no longer bundled here.

| Skill | Version | Main use |
|---|---|---|
| `stat-write-style` | v1.6.5 | Draft and revise manuscript exposition and presentation |
| `stat-proof-write` | v0.3.1 | Draft or clarify a mathematical proof |
| `stat-paper-review` | v1.2.7 | Give a critical, evidence-backed manuscript review |

Use `$stat-write-style`, `$stat-proof-write`, or `$stat-paper-review` to invoke the corresponding skill. Their `agents/openai.yaml` files disable implicit invocation. Drafting a proof does not provide an independent audit.

## How the skills work

**`stat-write-style`** first reads the requested material and its dependencies to understand the statistical objects, claims, and intended audience. It then drafts or revises the exposition, improving motivation, statement clarity, notation, transitions, and the connection between the main text and supplement while preserving scientific claims and supplied proof details. It checks the revised text for consistent terminology, equations, citations, and cross-references; unsupported scientific choices remain explicit author decisions.

**`stat-proof-write`** first reads the target statement, assumptions, supplied argument, and supporting results to identify the main reduction and intermediate goals. It organizes the proof around an opening overview, develops justified calculations and local explanations, and connects each step to the conclusion while preserving the supplied mathematical claims and proof route. It checks the steps it writes, labels results needed later, and flags unresolved gaps rather than hiding them behind fluent prose; this writing process is not an independent proof audit.

**`stat-paper-review`** first reads the paper in its presented order, then traces its central claims through the method, theory, numerical evidence, and interpretation. It pays particular attention to novelty relative to verified prior work, practical usefulness compared with existing alternatives, assumptions, evidentiary support, and consequential gaps in explanation. The report prioritizes findings by the repair needed and its scientific consequences, distinguishes verified evidence from uncertainty, and gives actionable revision specifications without rewriting the manuscript.

## Repository layout

```text
stat-paper-skills/                this Git repository
  stat-write-style/              manuscript-writing skill
  stat-proof-write/              proof-writing skill
  stat-paper-review/             review skill
```

## Skill use and installation

`stat-write-style` covers author-side drafting, restructuring, polishing, notation, and main/supplement coordination. It preserves supplied proof detail and the manuscript's template during local and whole-paper edits. Example: `Use $stat-write-style to revise this methods section while preserving its scientific claims.` Its helpers and tests require shared Python 3.10+. The writing audit uses `pypdf` or `PyPDF2` for automatic page counts, or accepts `--pdf-page-count "SOURCE=N"` from a trusted count. Run its checks with `python -m unittest discover -s stat-write-style/tests`.

`stat-proof-write` develops readable proofs with explicit derivations and local mathematical justification. Example: `Use $stat-proof-write to expand this compressed argument.` It does not replace proof checking or general manuscript editing.

`stat-paper-review` provides referee-style diagnosis and edit specifications without rewriting the manuscript. Severity reflects the repair needed, its scientific consequence, and the conventionality and restriction of any added assumptions. Novelty and practical usefulness are compared with existing methods, including alternatives that already give similar conclusions. Focused reviews cover the requested question and necessary dependencies. Multiple source files alone do not require a durable review bundle; delegation, durable resumption, and requested execution records do. Example: `Use $stat-paper-review to review this paper as a critical statistical reader.` Its helper and tests require shared Python 3.10+. Run its checks with `python -m unittest discover -s stat-paper-review/tests`.

Install each skill from its named source folder under a user-wide skill root such as `~/.agents/skills/`. Preserve explicit invocation settings; Claude installations need the corresponding `"user-invocable-only"` skill overrides. Use shared runtimes and packages rather than project-local environments. Refresh skill discovery or restart the host if a newly installed skill is not visible.

[MIT license](LICENSE)

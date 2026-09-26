# Proof-check architecture

This folder describes the current `stat-proof-check` implementation. The skill's [entry point](../stat-proof-check/SKILL.md) and references define the agent workflow; this folder explains the code and repository boundaries.

| Source | Responsibility |
|---|---|
| [Architecture](architecture.md) | Data flow, authority, review, rendering, and compatibility |
| [`shared/paper_core`](../shared/paper_core) | Maintained database, validation, controller, assessment, and renderer source |
| [`stat-proof-check`](../stat-proof-check) | Self-contained skill package and generated core bundle |
| [`tests/new_format`](../tests/new_format) | Shared-core behavior and packaging checks |
| [`tools`](../tools) | Bundle builder and proof-check installer |

The companion [Proof Graphify repository](https://github.com/rqzhu-aide/proof-graphify) owns its skill and architecture. Its local checkout is nested at `proof-graphify/` for cross-package development and is ignored by this repository. The two repositories have separate Git histories and remotes.

Completed plans, audits, and old architecture versions are retained in the local `archived/` folder, outside skill discovery and Git. They are historical evidence, not current implementation instructions.

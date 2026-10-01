# Proof-check architecture

This folder describes the current `stat-proof-check` architecture and retains labeled change records and proposals. The skill's [entry point](../stat-proof-check/SKILL.md) and references define the agent workflow; this folder explains the code and repository boundaries.

| Source | Responsibility |
|---|---|
| [Architecture](architecture.md) | Data flow, authority, review, rendering, and compatibility |
| [`shared/paper_core`](../shared/paper_core) | Maintained database, validation, controller, assessment, and renderer source |
| [`stat-proof-check`](../stat-proof-check) | Self-contained skill package and generated core bundle |
| [`tests/new_format`](../tests/new_format) | Shared-core behavior and packaging checks |
| [`tools`](../tools) | Bundle builder and proof-check installer |

The companion [Proof Graphify repository](https://github.com/rqzhu-aide/proof-graphify) owns its skill and architecture. Its local checkout is a sibling at `../proof-graphify/` for cross-package development. The two repositories have separate Git histories and remotes.

## Proof-check change records and proposals

These notes preserve decisions and evidence. Current workflow instructions remain in the skill and its references.

| Note | Status |
|---|---|
| [Workflow revision handoff](proofcheck-workflow-revision-handoff.md) | Implemented scope for preserving examinations, coherent independent reviews, and precise PDF coverage |
| [Workflow revision validation](proofcheck-workflow-revision-validation.md) | October 1 implementation, compatibility, installation, and live-test limitation |
| [Targeted reliability fixes](proofcheck-targeted-fixes-handoff.md) | Implemented; retained scope of the September 27 fixes |
| [Targeted fixes validation](proofcheck-targeted-fixes-validation.md) | Implementation, verification, and subsequent installation record |
| [Reader and output fixes](proofcheck-reader-output-fixes.md) | Implemented in maintained sources; records validation and remaining live-browser/test-run limitations |
| [Automatic-workflow handoff](proofcheck-automatic-workflow-handoff.md) | Unimplemented proposal for a new wrapper and managed-run design; not current workflow instructions |

Additional completed plans, audits, and old architecture versions are retained in the local `archived/` folder, outside skill discovery and Git. They are historical evidence, not current implementation instructions.

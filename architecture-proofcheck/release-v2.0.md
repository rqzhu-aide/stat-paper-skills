# Proofcheck v2.0

Release date: September 15, 2026. This version is being committed and tagged `v2.0` at the user's explicit request. Package metadata and shared core version are `2.0.0`.

New audits use the database workflow. The coordinator reads the manuscript, registers and refines the graph, chooses assignments and makes scientific decisions. The controller lists recorded work, prepares coherent bounded assignments, validates structured responses, saves progress and supports explicit recovery. Existing v1.5 folders keep the unchanged legacy runtime and templates until explicitly imported.

The companion [Archify repository](https://github.com/rqzhu-aide/archify-proofs-overview/tree/v2.0) is tagged `v2.0` with the same shared core. Its ordinary overview workflow remains available; its audit reader uses the common records and their recorded judgments. Both bundles have source identity `b45abd465da23a6c67ce43c40d3a547ebfa88cb9f36c5eab25e9476350ae9b7d`. Storage is format 3, record contract 3, packets 2 and projection 2; these identifiers are independent of the release tag.

## Validation and remaining limits

The [implementation receipt](controller-implementation-2026-09-15/README.md) records the full 1,124-test new-format suite passing with one Windows symlink-permission skip, 115 overview tests, 13 installer tests, and the bounded live pilot. The final pilot completed 19/19 examinations without changing its scientific records, retaining both refuted statements and the higher argument's conditional local validity.

The release changes version metadata and workflow routing, not the tested scientific runtime. A separate export of the exact staged repositories passed 54 packaging tests (one existing Windows symlink-permission skip), 115 overview tests, seven skill-structure tests, 13 installer tests and both metadata validators. The packaging tests include installed-only execution. [Staged runtime verification](controller-implementation-2026-09-15/release-staged-runtime-verification.json) confirms that all 124 maintained/bundled runtime files in the two indexes preserve the tested working bytes. The `release-validate-*.log` files beside it contain the check outputs. Shared source and bundled copies are stored without Git text conversion so their content identities survive checkout.

Actual browser visual acceptance and large-paper performance measurement remain outstanding. The pilot needed documented corrections and is not an unassisted clean run of the final instructions. Tagging this version does not claim these evaluation gates passed, mathematical completeness, or a speed improvement on the DRL paper. This explicit distribution decision supersedes the earlier plan's instruction to defer R8; it preserves the unresolved evaluation work.

## Release contents

The commits include the runtime, controller instructions and examples, tests, active architecture/handoff documents, selected evaluation receipts and the working pilot reader. The 20 previously tracked historical architecture files are preserved at their archived paths. The full historical archive, temporary workspaces, raw pilot database/runtime archive and dirty-tree inventory remain local. Unrelated writing-skill changes are excluded.

For clean-checkout development tests, clone the companion `v2.0` repository into `archify-proofs-overview/` as described in the root README. Installed skills are self-contained and need no sibling checkout. This release does not install either skill into the user's machine-wide skill directory.

The released content is identified by each repository's annotated `v2.0` tag; `git rev-parse v2.0^{commit}` resolves its commit without a self-referential receipt.

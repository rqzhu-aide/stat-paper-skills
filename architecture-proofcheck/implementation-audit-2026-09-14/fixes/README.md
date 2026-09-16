# Implementation audit corrections

The software corrections for F1 through F10 are implemented in the shared core and both generated skill bundles. This follows the [original implementation audit](../review.md), whose findings and counterexamples remain a record of the earlier tree.

## What changed

| Finding | Corrected behavior |
|---|---|
| F1: missing coverage | Full/focused completion requires coverage of declared written proof passages. Substantive spans need current responsible checks that consumed their listed claims. Structural spans need no extra proof verdict. Working reports remain available and show uncovered or unchecked spans. |
| F2: conflicting checks | Conflicting current, unsuperseded judgments stay disputed in either insertion order. Explicit successors preserve earlier evidence. Independent disagreement is compared by target and check kind, so agreement elsewhere cannot hide it. |
| F3: independent review scope | Mapping checks the original reviewed scope, source evidence, worker coverage and coordinator packet. The original packet is checked again inside the acceptance transaction. Direct submission also cannot credit a target outside the worker's coverage. |
| F4: calibration | A successful qualification requires distinct passing cases on both the valid and invalid sides. Failed or inconclusive calibration remains recordable as an unsuccessful qualification. |
| F5: packet consistency | Packet construction captures its starting revision and rejects an intervening commit before saving the packet. Records, guards and source context cannot be accepted from mixed revisions. |
| F6: consumed evidence | Application bindings include supplier scopes, statement passages and exact borrowed proof evidence. Ordinary statement use retains its independence from unrelated proof edits and outgoing consumers. |
| F7: hidden proof support | Hidden claim final groups and their own argument composition affect the connection through them. The displayed major result's final composition stays on that result. Missing hidden composition also prevents a green edge. |
| F8: reader interface | The audit reader uses the actual bundled Archify shell and native camera, selection, tracing, presentation and export controls. The major-only graph opens canonical intermediate evidence below it. Search and keyboard navigation reach the intended records and graph locations. Cycle fallback uses the same shell. |
| F9: publication destination | Report output is checked against the database and registered sources, including path aliases, before rendering and before replacement. Existing report files can still be replaced. |
| F10: packet extension | Successive extensions preserve earlier anchors and source paths while retaining the original mode and source-context rules. |

The shared and CLI/vertical-slice fixtures now supply actual coverage before asserting completion. Tests that intend to correct a prior judgment record explicit supersession; tests of contradictory judgments assert disputed status. No completion or representation assertion was relaxed to hide missing work.

The handoff's projection envelope now documents `summary.limitations`. The record contract clarifies statement passage membership and consumed supplier/borrowed evidence in binding recipes. The architecture and implementation sequence remain unchanged.

## Verification

| Check | Final result |
|---|---|
| Full new-format suite | 1,001 tests run in 229.010 seconds; passed with one skip |
| Existing overview reader suite | 115 tests passed in 26.605 seconds |
| Installer suite | 13 tests passed in 0.517 seconds |
| Bundle verification | Both 38-file cores and wrappers match their maintained sources |

The new-format lane contains 40 additional regression tests. The first integrated run exposed outdated bundle-count assertions and a missing-binding coverage expectation; those were corrected, and the complete lane was rerun successfully. Its [first-run log](new-format-first-run.log) is retained alongside the final passing log.

Integrated verification results are recorded in [verification.json](verification.json). The [bundle check](bundle-check.json) identifies the exact maintained source and confirms that both generated bundles match it.

The [synthetic reader example](example.html) shows two major nodes and a red connection for a gap inside a hidden claim. Its [projection](example-projection.json) and [render receipt](example-receipt.json) provide inspectable evidence. It is deliberately an incomplete working audit, not a completed mathematical review.

Browser visual acceptance remains pending. The browser URL policy prevented opening the local artifact; no alternative transport or browser workaround was used. The Node interaction simulation verifies the adapter contract and generated script syntax, but does not establish real browser layout, rendering or exported pixel quality.

The bounded timing pilot, fresh mathematical review and R7 forward evaluation have not been run. R8 release version changes remain gated on that evaluation. The full legacy proofcheck lane was not rerun for these changes; the new-format, existing overview and installer lanes cover the changed software paths. No commit or installation was performed.

Previously saved audits can now show incomplete or stale work when they lack coverage or the required consumed evidence. Such work needs completion or reassessment before release.

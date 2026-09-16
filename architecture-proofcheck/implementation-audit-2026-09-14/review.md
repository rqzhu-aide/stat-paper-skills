# Implementation audit

Date: September 14, 2026, America/Chicago.

Follow-up: the software corrections and final test results are recorded in [Implementation audit corrections](fixes/README.md). This audit preserves the findings against the earlier source identity below.

**Verdict: do not accept this as the completed handoff implementation yet.** The software foundation and automated checks are substantial, and the new-format test count and bundle identity are reproducible. However, targeted counterexamples expose several failures in the exact guarantees the architecture was intended to provide: complete coverage, trustworthy saved judgments, independent-review provenance, and honest connection colors. These are software defects to fix before the forward mathematical evaluation.

This audit reviewed `shared/paper_core`, the corresponding tests, shipped bundles, and relevant skill/renderer integration. It used disposable synthetic papers and public record/submission APIs. The packet-race probe additionally used a temporary function hook to schedule a second connection's legitimate commit at a deterministic interleaving point. Production implementation files and the user's manuscripts were not edited.

Audited shared-core source identity: `a97a20e098c2564d1de18a6ff0422acff1248178f5a187253de3109978d04269`. Both packaged cores and wrappers matched their maintained sources during the bundle check.

## Main consequences

1. **A report can overstate completion or support.** It can release an audit with zero coverage records, ignore an unresolved conflicting judgment, or show a green connection whose hidden derivation has a current gap.
2. **Independent review can be credited to unread or changed material.** Mapping does not preserve the original review's scope and source binding. Failed calibration can also be accepted as qualification.
3. **Reuse and concurrency can attach judgments to unexamined inputs.** Relevant supplier changes are omitted from bindings, and packet assembly can mix records from one state with guards from another.
4. **The requested UI is not delivered.** The new renderer builds its own page instead of retaining the actual adapted Archify interface.

The remaining timing pilot, fresh mathematical review, and forward evaluation identified by the programmer are still necessary. They are not the only unfinished work. The software findings below can and should be closed with code and regression fixtures.

## Verified findings

### F1. P1: completion and release do not require proof coverage

The delivered `Fixture.complete()` has statement/proof anchors, primary checks, independent responses, and reconciliations, but **zero coverage records**. Assessment still returns `process_complete: true`, with 11 of 11 required obligations satisfied and both results green. The packaged CLI then successfully creates a release, returning exit 0 and validation `ok: true`.

This is not an inference about whether the synthetic proof is mathematically correct. It is a mechanical counterexample to the promised requirement that all substantive proof spans be accounted for before process completion. Coverage validation checks bounds for records that exist; absent or uncovered spans never enter the completion gate.

Relevant code: [obligation construction](../../shared/paper_core/assessment.py:456), [completion calculation](../../shared/paper_core/assessment.py:925), [coverage validation](../../shared/paper_core/queries.py:72). The test suite treats the no-coverage fixture as complete in [test_assessment.py](../../tests/new_format/test_assessment.py:920).

**Required correction:** derive and evaluate coverage requirements over the declared written proof passages. Missing spans must prevent process completion and release while still allowing draft saves and working reports. Include zero coverage, a missing substantive span, and an entirely structural span in the regression cases.

Evidence: [assessment_repros.py](assessment_repros.py), [results](assessment-run-6a9b2a21/results.json), and the resulting [release receipt](assessment-run-6a9b2a21/no-coverage-release/receipt.json).

### F2. P1: a later positive check silently wins over an unresolved current gap

I created a completed application check with outcome `gap`, then another completed check with outcome `supported`, without a supersession or reconciliation. Both remain current and unsuperseded. Assessment chooses the later check, makes the application green, and leaves the audit process complete.

The code retains all check references but takes the newest judgment's outcome. Retaining old bytes is insufficient when the visible assessment silently discards their disagreement.

Relevant code: [candidate selection and completion](../../shared/paper_core/assessment.py:543).

**Required correction:** identify contradictory unsuperseded judgments for the same obligation and consumed input. Preserve disputed status until explicit resolution. Test both insertion orders so a positive or negative result cannot win simply because it was written last.

Evidence: `contradictory_checks` in [results](assessment-run-6a9b2a21/results.json), generated by [assessment_repros.py](assessment_repros.py).

### F3. P1: response mapping can manufacture independent-review credit

Two public-API probes demonstrate the broken boundary:

- A worker response covered only a lemma. The coordinator mapped its judgment to the theorem's argument, which was absent even from the mapping packet. The operation returned `accepted`, and the theorem's independent composition obligation became satisfied/current.
- After a response was saved, the proof source was changed, recaptured, and rebound. Mapping the old response through a fresh packet produced a current independent check with `context_changed: false`. The old reasoning had not reviewed that new proof.

Mapping checks that the target exists and permits the check kind, then creates a check using the new mapping packet. It does not establish that the target and its consumed source were covered by the original independent packet/response.

Relevant code: [original-packet handling](../../shared/paper_core/review.py:234), [target checks](../../shared/paper_core/review.py:256), [acceptance against mapping packet](../../shared/paper_core/review.py:286).

**Required correction:** validate mapping against both original reviewed scope/evidence and the coordinator's mapping scope. Bind independent reasoning to its original inputs; changed material needs a fresh review or explicitly permitted reviewed reuse. A coordinator mapping must not supply mathematical work that the independent reviewer did not perform.

The existing [out-of-scope mapping test](../../tests/new_format/test_review.py:713) explicitly documents the containment gap and asserts that it is accepted. This is a useful reproduction, but it is not an acceptance gate for the handoff. Reverse that expectation when fixing the defect.

Evidence: [review_probes.py](review_probes.py), `wrong_mapping` and `changed_source_mapping` in [review_probe_results.json](review_probe_results.json).

### F4. P1: failed calibration can qualify an independent reviewer

A qualification with every valid-case and invalid-case outcome explicitly set to `fail` was accepted when `qualified: true` was also supplied. That qualification then authorized an accepted independent check.

The validator requires nonempty case arrays but does not reconcile their outcomes with the qualification claim. Intake trusts the boolean.

Relevant code: [qualification validation](../../shared/paper_core/contract.py:361), [review intake](../../shared/paper_core/review.py:115).

**Required correction:** enforce the declared balanced calibration policy against recorded outcomes and configuration. Do not accept a successful qualification that contradicts its own evidence. Test failure and inconclusive combinations as well as missing cases.

Evidence: `failed_calibration` in [review_probe_results.json](review_probe_results.json).

### F5. P1: a packet can omit a premise yet authorize a check bound to it

Packet construction collects records before computing membership guards and reading the base revision. A second connection can commit in between those operations.

The deterministic probe inserted `use_unseen` at that point. The issued packet omitted it from both its records and read set, but used the new revision and new relation digest. Submitting a completed derivation succeeded; the stored check binding included the unseen use and the check was current.

Thus the existing commit-time conflict checks can all pass while the checker never received an input its judgment is recorded as consuming.

Relevant code: [packet collection, guards, and revision](../../shared/paper_core/packets.py:426).

**Required correction:** assemble each packet against one consistent database revision, including records, read set, guards, source context, and saved payload. Reject/retry assembly if its state changes. Keep this two-connection interleaving as a regression test; the existing races after packet issuance do not cover it.

Evidence: `interleaved_packet` in [dataset results](dataset_run_37f0fa32/results.json), generated by [dataset_repro.py](dataset_repro.py).

### F6. P1: application bindings omit relevant supplier scope and borrowed evidence

Two changes that must require review were invisible to freshness:

- Changing a supplier's local condition from `x > 0` to `x > 1` left its consumer's application current, with no reported changes.
- Rebinding the supplier's borrowed proof anchor to different text left a `proof_argument` application current. Its binding contained the consumer's proof anchor but omitted the supplier's borrowed anchor content.

The statement helper binds the item/part facet without traversing its scope. The proof-argument branch binds the supplier item's passage IDs without following them to the borrowed content.

Relevant code: [statement binding](../../shared/paper_core/bindings.py:60), [proof-argument binding](../../shared/paper_core/bindings.py:72).

**Required correction:** bind the consumed supplier scope chain and exact statement/borrowed-proof evidence, while retaining the intended distinction between statement-only use and proof reuse. Add negative tests for semantic changes and positive tests for labels, outgoing consumers, and reviewed exact relocation.

Evidence: `supplier_scope` and `borrowed_anchor` in [dataset results](dataset_run_37f0fa32/results.json).

### F7. P1: a defective hidden derivation can disappear from connection status

When an intermediate claim has its own argument, its final group is treated as though it were the displayed theorem's final composition. The projection excludes that hidden derivation from the incoming connection's assessed obligations.

The probe records a current gap on the hidden derivation. Its group is red, but the corresponding major-item connection is green and says all required supporting derivations are supported.

Relevant code: [trace stopping condition](../../shared/paper_core/projection.py:306).

**Required correction:** distinguish a hidden claim's final group from the displayed owning result's final composition. Only the latter belongs outside incoming-edge aggregation. Preserve the separate requirement that genuinely green incoming applications can coexist with a failed final combination on the target theorem.

Evidence: [ui_repro.py](ui_repro.py), `hidden_argument_final` in [ui_repro_results.json](ui_repro_results.json), and the [generated report](ui_hidden_final_report.html). This finding is established by projection data and source inspection; the report was not visually accepted in a browser.

### F8. P1: the actual Archify interface was replaced

The new renderer constructs a custom HTML page, styles, and interaction runtime. Its only template extraction is Archify's font style block. It does reuse/adapt layout and routing, but it does not retain the actual adapted viewer requested by the user.

The page exposes theme and actual-size/fit-width controls. The established main-result navigation, zoom/pan, dependency tracing, and presentation/export controls are absent. This changes how a user explores a large proof graph, rather than being a cosmetic implementation choice.

Relevant code: [custom page construction](../../shared/paper_core/renderer/render_projection.mjs:1105), [font-only template extraction](../../shared/paper_core/renderer/render_projection.mjs:1163). Compare the requirement in [architecture section 10](../architecture.md#10-the-archify-reader).

**Required correction:** integrate the audit projection and lower reader with the actual shared Archify shell and its established controls. Then perform the required browser acceptance on long mathematics, hidden-claim search, edge details, keyboard interaction, narrow layouts, and cycle fallback.

### F9. P2: report output can overwrite a registered manuscript

Publishing a report to the registered synthetic `paper.tex` path returned `published` and replaced 411 bytes of TeX with 247,737 bytes of HTML. The output check only rejects directories before replacement. The affected file was an audit fixture, not the user's manuscript.

Relevant code: [output validation](../../shared/paper_core/publish.py:259), [replacement](../../shared/paper_core/publish.py:284).

This requires a wrong output destination from the caller, so it is separate from the normal mathematical-status defects above. It is nevertheless a consequential failure for an agent-operated workflow that knows both its source paths and report destination.

**Required correction:** reject output collisions with the database and registered source files before rendering or replacement; resolve aliases when comparing paths. Continue allowing intended replacement of an existing report. Test collision rejection with the source bytes unchanged.

Evidence: `source_overwrite` in [ui_repro_results.json](ui_repro_results.json), reproduced by [ui_repro.py](ui_repro.py).

### F10. P2: repeated context extension loses earlier extra evidence

The first extension included an explicitly requested `anc_extra` anchor. A second extension dropped it. The implementation retains previous targets but rebuilds using only the latest extra anchors/paths, rather than the promised union.

Relevant code: [extension reconstruction](../../shared/paper_core/packets.py:487).

**Required correction:** retain prior explicit evidence selections across extensions while applying the same packet-mode allowlist and source-version rules. Test two successive extensions with distinct anchors.

Evidence: `extension_union` in [dataset results](dataset_run_37f0fa32/results.json).

## What the test results do and do not establish

The new-format lane was rerun successfully: **961 tests in 236.673 seconds, one skip**. The overview/reader lane passed **115 tests in 27.951 seconds**, and the installer lane passed **13 tests in 0.520 seconds**. The bundle gate also passed with the source identity above. See [new-format log](new-format-tests.log), [overview log](overview-tests.log), [installer log](installer-tests.log), and [verification receipt](verification.json).

The legacy 1,072-test lane was not rerun in this audit. Its reported pass is not independently verified here. The live mathematical pilot and forward evaluation were also not run. The browser's URL policy blocked opening the generated local report, so this audit does not claim visual browser acceptance.

The targeted probes explain how a large passing suite can coexist with these problems. Some fixtures omit a required condition and then assert completion. One test deliberately asserts acceptance of a known scope violation. Other cases test conflicts after packet creation without testing a commit during creation. These tests are evidence about implemented behavior, not all evidence that the handoff requirements hold.

The packet lookup optimization is a real improvement in the inspected code: reverse-reference lookup replaces the particular whole-item scan, and the delivered scaling lane passes. Its flat returned-row/byte counters apply to the measured statement-packet fixtures. They do not establish constant total execution cost for every graph shape/history or reduced mathematical reasoning time. Keep those claims distinct from the still-unrun authoring-versus-reasoning pilot.

## Recommended order before acceptance

First fix F1-F7 with adversarial regression cases that fail on this audited source. Address the UI requirement and output/evidence-loss defects before treating the package as ready for a real paper. Rebuild and verify both bundles after code changes.

Then rerun the affected tests and the full new-format lane, inspect the actual Archify reader in a browser, and execute the bounded timing/fresh-review pilot. Keep R7 forward evaluation and R8 distribution as explicit gates. The evidence here supports targeted corrections; it does not call for another architecture rewrite or more per-line proof paperwork.

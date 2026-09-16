# Revision plan: current proofcheck to the item-graph architecture

Date: September 12, 2026.

September 15 follow-up: the database pilot has since been implemented and audited. The [small controller revision plan](controller-revision-plan.md) defines the next focused changes; the [detailed implementation plan](controller-implementation-plan.md) fixes their interfaces, work packages and acceptance tests. Both use C0-C5 mapped to this plan's original R0-R8 gates. The starting-point descriptions below document the earlier migration baseline, not the current pilot's implementation status.

Status: proposed implementation plan. None of the runtime phases below is marked implemented by the creation of this document. The complete destination is defined in [architecture.md](architecture.md). This plan explains how to reach it from the current code and existing paper audits. The September 13 [implementation handoff](implementation-handoff.md) supplies the fixed contract, command signatures, packaging decision, concrete work packages, and test disposition. R0 exercises those decisions rather than delegating their invention to the implementer.

## 1. Starting point and intended change

The current `stat-paper-proofcheck` v1.5 runtime uses canonical JSON manifests, ledgers, dependency registries, issue logs, and progress records. Its compiler binds compact annotations into a complete ledger. Its validators enforce physical-line coverage and per-step evidence. Its report and graph are generated from those files. It already has substantial mathematical review rules, calibrated independent review, source capture, version checks, and transactional report publication.

The separate `archify-proofs-overview` has a newer source/item/use model with stable identities, multiple passages, SQLite snapshots, bounded retrieval, source comparisons, reviewed reuse, and an adapted Archify reader. It currently supports overview interpretation rather than mathematical audit outcomes. Its item comparison avoids including outgoing consumers, but still includes the whole source revision and all prerequisite passages; that freshness boundary is too broad to reuse unchanged for every proof check.

The destination uses that shared paper-record foundation with optional audit records. Checkers save meaningful claim derivations, applications, drafts, findings, and independent responses directly. The graph contains only major mathematical items. Selecting a connection exposes intermediate reasoning in the existing lower reader. Green/red/gray/amber connection states are derived from current evidence. Selecting the target result exposes final composition and full coverage.

The DRL case establishes concrete problems to resolve: repeated ledger renewal, paperwork for headings, reasoning left outside submitted records, stale reader summaries, custom conditional labels rejected by the validator, and contradictory citation requirements for external restatements without proofs. The [archived case review](archived/pre-item-graph-2026-09-12/drl-case-review-2026-09-12/review.md) records the evidence and limits. Its reported runtime is not a controlled performance baseline.

## 2. What to retain, replace, and retire

| Current component | Treatment in the new implementation |
|---|---|
| Overview `paper_records.py`, `paper_database.py`, `paper_revision.py` | Extract shared record/source behavior; replace full-snapshot edit/load persistence with individual record versions; preserve overview-only operation |
| Overview `render.mjs` and bundled Archify viewer | Reuse the actual UI; add audit projection, connection traces, status display, and dataset-wide search |
| Proofcheck `proofcheck_sources.py`, `proofcheck_source_check.py` | Extract source-location and diagnostic behavior behind a source interface; current helpers depend on the monolith |
| `proofcheck_labels.py`, `proofcheck_math.py` | Reuse tested label and mathematical rendering behavior where compatible; unify source selection |
| `proofcheck_authoring.py` | Retain atomic submission principles; replace whole-ledger assembly with incremental database operations |
| `proofcheck_reconcile.py` | Reimplement persistence against new records while preserving original responses and explicit reconciliation; do not import its monolith namespace API |
| `proofcheck_report.py`, `proofcheck_release.py` | Retain evidence-aware summaries and publication/history guarantees; generate new-format reports from one database snapshot |
| `proofcheck_graph.py` | Keep for legacy reports during transition; retire its graph/overview toggle from new-format reports |
| Monolithic `proofcheck.py` | Retain the legacy entry point; introduce a thin new-format dispatcher without running new records through legacy ledger gates |
| Skill instructions, examples, installer, evaluations | Develop pilot instructions alongside the new commands; distribute the accepted workflow after end-to-end evaluation |

Do not convert the database into an extra wrapper around the old manifests, mirrored registries, and ledger compiler. That would preserve the DRL workload while adding another authority. Do not require workers to regenerate paper-specific Python authoring programs.

Historical behavior and acceptance receipts remain evidence for their own versions. The new architecture intentionally changes some representation requirements, particularly mandatory heading records and per-line risk matrices. Retain old tests for legacy execution, port mathematical distinctions and actual guarantees into new-format fixtures, and do not impose legacy-only representation tests on the replacement. Handoff section 9 identifies specific test families and the required mapping. No new-format core import may reach the legacy monolith indirectly.

## 3. Implementation phases

Each phase has a concrete exit condition. Ordinary edits and meaningful checks remain small. Broader regression work is run at integration and release boundaries, rather than after every document or field change.

The [phase-to-package mapping](implementation-handoff.md#revision-phases-and-work-packages) assigns these R0-R8 gates to P0-P7 without creating a second sequence or adding their estimates. R8 belongs to the release portion of P7, using P6's packaging tooling after forward evaluation.

### R0. Establish the baseline and freeze the first new contract

**Work**

- Record the current proofcheck and overview source revisions/content identities, installed runtime identities when relevant, and the applicable existing acceptance receipts.
- Preserve the current bundled reference and selected existing audits. Choose separate working copies for migration exercises; do not alter the DRL manuscript or existing audit.
- Exercise the fixed [record contract](handoff/record-contract.md), [DDL](handoff/schema.sql), and [example batch](handoff/example-batch.json). Resolve any failing fixture before shared implementation; document deliberate contract changes rather than allowing independent interpretations.
- Use the handoff's one maintained `shared/paper_core` source and identical generated bundles in both installed skills. Validate format/feature compatibility and installed paths without sibling checkout imports or runtime downloads.
- Implement against the public command/packet signatures and record-level read/write/membership conflict protocol in handoff sections 4 and 5.
- Run the bounded early measurement in handoff section 10 before substantial implementation: distinguish saved-reasoning authoring from fresh checking, measure command/retry/renewal costs, and record unknowns or incomplete scope. Repeat matched scenarios with the first vertical slice; keep R7 for broader evaluation.

**Exit condition**

A small example can represent two major premises, a hidden intermediate claim, a joint derivation, and its final result without duplicated dependencies. Its IDs, category rules, proof scope, and intended reader states are unambiguous. Overview-only records still have a clear compatibility path. No new protocol is described as compatible with old verdicts merely because both use the word verified.

### R1. Repair source acquisition and citation consistency

**Work**

- Unify the source-selection interpretation used by inventory, labels, passages, packets, and final checks.
- Repair the observed custom-conditional failure. Supported literal branches resolve mechanically; unsupported custom selections have a source-bound review path and explicit limitations. Preserve the distinction between a source concern and a mathematical gap.
- Collect citations consistently from item statements, relevant context, and proof passages. A cited external restatement without a local proof must have a valid inventory, authoring, and validation route.
- Support multiple statement/proof anchors and explicit aliases; detect genuine ambiguity without forcing the manuscript into a single proof span.
- Keep source edits as new captured versions. Do not treat unchanged line numbering as an unchanged file identity.

**Exit condition**

The DRL-shaped custom wrapper and no-proof external restatement both pass a supported source-registration workflow. An actually inactive or ambiguous label is still distinguished from an active one. The same citation inventory drives authoring and final assessment. These tests exercise behavior, not only expected error-message text.

### R2. Add the audit records to the shared database

**Work**

- Extend the shared core with the agreed typed records, stable references, statement parts, local scopes, argument membership, coverage spans, and source/check history.
- Append changed record versions and preserve immutable completed review evidence. Keep build/usage receipts separate from mathematical commits. Validate all links and allowed values on atomic batch commit, including non-overlapping rebase and relationship-addition conflicts.
- Allow a structurally valid draft with incomplete mathematical work. Saving a finding must not depend on first publishing a complete parent ledger.
- Add bounded queries for a claim, application, result, unresolved work, and independent-review packet. Return exact needed context rather than all captured files and review history.
- Preserve shared-claim identity when several uses or display connections reference it. Reject dangling references and conflicting stale edits.

**Exit condition**

A process can save useful draft reasoning and a finding, stop, resume from the database, and retrieve that work without a scratchpad. An interrupted or rejected edit leaves the preceding snapshot usable. Two uses of one lemma retain separate IDs. Renumbering preserves identity. An overview-only edit does not discard audit records.

### R3. Implement local checking, coverage, and selective reuse

**Work**

- Replace the whole-ledger submission barrier with direct saving of claim derivations and use checks. Keep exact targets, source evidence, relevant hypotheses, and concise paper-specific reasoning.
- Generate lightweight coverage for structural text. Link all substantive proof spans to their claims/checks without forcing a node or adversarial record for every physical line.
- Check local scope, combined premises, cases, and the final composition. Distinguish a complete alternative argument from a case that must be joined with other cases.
- Separate local outcome from freshness and dependency support. Bind each check to the content it actually consumes. Exclude new outgoing consumers and unrelated report metadata from the supplier's inputs.
- Adapt the existing source-diff and reviewed-reuse workflow. Inspect changed global context before reuse; preserve eligible reasoning automatically once the review is recorded.
- Derive precise recheck tasks and explain the changed input instead of instructing the operator to rebuild an entire unit indiscriminately.
- Implement the corresponding pilot entry point using [checker-protocol.md](handoff/checker-protocol.md), then evaluate its granularity and token/authoring costs alongside the commands. It must not direct a checker back to the legacy ledger protocol.

**Exit condition**

A newly added consumer leaves its supplier's completed local check current. A changed assumption triggers appropriate attention. A changed supplier proof with an unchanged statement preserves the consumer's conditional derivation while updating its support. A borrowed proof argument becomes pending when its borrowed passage changes. A long proof with headings has complete source coverage without heading proof verdicts.

### R4. Integrate independent review and audit completion

**Work**

- Reuse the balanced checker qualification protocol, with its actual blinding limitations and profile/configuration identity. Preserve context-only handoff reuse.
- Generate blinded packets from the declared proof scope and source context. Dispatch only the source packet and checker protocol to a fresh independent context, with no database/report path or inherited primary conversation. Keep primary judgments, intermediate interpretations, findings, reasoning, reconstructions, repairs, and expected canary answers out of that context and its source-only extensions. Record actual exposure limitations; omission of a path is not an OS sandbox.
- Save the original independent response before exposing primary work for reconciliation. Retain disagreements and the evidence resolving them.
- Account for complete result review, including hidden claims, applications, cases, and final composition. If a long proof is divided, explicitly review its integration.
- Port global consistency, external-dependency, issue-propagation, adversarial, and applicable method-interface requirements onto the new records.
- Derive audit-process completion separately from mathematical support. Completed audits can contain justified defects or adjudicated inconclusive findings; undone work stays incomplete.
- Add pilot coordinator, independent-review, and reconciliation instructions so a fresh checker can execute this workflow before release documentation is finalized.

**Exit condition**

A short proof chain has primary and independent reasoning, an intentionally introduced disagreement, explicit reconciliation, and an accurate completion status. Checking one theorem part does not complete the others. An alternative successful route does not erase a defect in another audited written route.

### R5. Build the new report projection in the existing Archify UI

**Work**

- Render only major items in the diagram. Remove the proposed expanded-intermediate graph from the new workflow entirely.
- Derive display connections and their traces from canonical use IDs, hidden claims, and argument groups. Do not author a second overview graph.
- Extend the lower connection reader with required form, supplied form, intermediate steps, shared inputs, source passages, checks, and findings. Preserve per-use/case states in combined connections.
- Extend the result reader with full derivation, locally originating steps, coverage, final composition, and independently assessed theorem parts.
- Implement the green/red/gray/amber rules from architecture section 9, including partial groups, changed historical defects, independent disagreements, and upstream uncertainty. Keep mathematical type colors on nodes.
- Search the full dataset. Selecting a hidden claim opens its owning result's detail without adding it to the graph.
- Preserve all records in a major-item/connection index when a truthful projection has a cycle. Keep the same viewer shell and explanation; do not delete edges or invent circular-proof findings.
- Generate summary counts, findings, repair directions, and all status labels from the same saved snapshot. Keep draft and historical evidence clearly labeled.

**Exit condition**

Browser inspection shows a readable major-only graph, a long selected-edge trace, shared intermediate steps, accessible source mathematics, keyboard navigation, and useful narrow layouts. A proof with no incoming edge is still completely inspectable. A case with green incoming uses but an invalid final composition shows the target's problem. No colored connection makes a stronger claim than its constituent current checks.

### R6. Implement publication and exercise legacy import

**Work**

- Preserve consistent-snapshot rendering, validated embedded identities, atomic publication, immutable releases, and reliable recovery after failure.
- Make checkpoint regenerate a current working report; retain saved database progress even if rendering fails and identify the previous HTML as older.
- Implement explicit legacy import into a separate working database using the mapping rules in section 4 below.
- Exercise import first on a small completed reference and a partial audit, then selected DRL units and their notes. Do not import all old setup steps as new graph nodes.
- Keep the v1.5 reader and delivery checker available for old reports during transition. An old report remains valid only under its own original contract and source state.

**Exit condition**

The old sealed reference is unchanged byte-for-byte. New-format imports begin as working reports with faithful provenance and appropriately qualified assessments. A failed render/publish preserves the last good report. The visible summary and database agree on findings and progress. Presentation-only regeneration requires no mathematical model call.

### R7. Run realistic forward evaluation

**Work**

- Have an independent checker execute a fresh, bounded audit using the packaged pilot skill and instructions from R3/R4, the source, and an ordinary task prompt. Give no expected answer or diagnosis to that checking context.
- Use a compact argument containing meaningful intermediate reasoning, a substantive application, and a relevant edge case. Complete primary work, independent review, reconciliation, and report delivery.
- Exercise a later consumer and a source revision. Confirm that reuse saves actual work and that mathematical changes still cause appropriate review.
- Then replay a demanding DRL proof or prerequisite chain, followed by a larger scoped audit when the short workflow is reliable.
- Measure reasoning/reading, authoring, retries, repeated context, preserved checks, time to a useful report, and actual usage when available. Compare matched scope and review standards. The old 20-plus-hour run is contextual evidence, not a controlled timing comparator.

**Exit condition**

An independent assessment finds the checking evidence and reader claims faithful to the source and declared scope. The operator can finish without ad hoc schema edits, hand-managed renewal filenames, or separate unpublished mathematical notes. Report observed benefits and unresolved limitations; do not promise an accuracy or cost improvement from software tests alone.

### R8. Update skill instructions and distribute the accepted implementation

**Work**

- Finalize the pilot entry point and role references using the observed R7 results, covering item/use/argument checking, incremental saving, scoped reuse, and the major-only reader.
- Remove contradictory instructions that require canonical per-paper JSON masters, whole-ledger publication, per-line risk rows, or detailed intermediate graph navigation for new-format audits.
- Keep instructions for supported legacy reading/import clearly separated. Update examples, installer checks, packaged assets, and release documentation.
- Run the relevant combined regression suite once on the actual release tree, validate the regenerated reference, and exercise the user-wide installation with shared runtimes.
- Record the released code/schema/renderer identities and acceptance evidence. Do not label the architecture implemented before this acceptance is complete.

**Exit condition**

The installed package, not only the repository checkout, completes the representative audit and opens the intended reader. Overview-only use remains functional. Existing audits retain a documented path for reading or explicit migration. Release status distinguishes local acceptance from any later commit, tag, installation, or remote publication.

## 4. Legacy data migration rules

Migration is an import with preserved provenance, not an in-place rewrite of an authenticated audit. It requires a record mapping and a qualified review-reuse decision.

| Legacy material | New-format handling |
|---|---|
| Manifest and inventory | Import paper/scope/item/source identities; retain exclusions and parser limits with their actual state |
| Dependency registry and uses | Map each exact use and consumed conclusion; preserve separate applications and external-source bindings |
| Normalized theorem conclusions | Map to a major item and stable parts when separately addressable; compare them with source before claiming fidelity |
| Ledger steps | Retain the complete original artifact as evidence; extract useful claims/checks where mapping is justified; do not create heading nodes |
| Issue log | Import individual findings, original targets/classifications/lifecycle, evidence, and repair relationships |
| Scratchpad notes | Import as drafts with original locations and relevant source bindings; do not mark them completed checks |
| Primary verdicts | Retain historical labels and their contract; reuse only after target/input/scope compatibility is reviewed |
| Independent responses | Preserve original response and provenance; assess compatibility before satisfying new review requirements |
| HTML and FINAL seal | Preserve unchanged as a historical release; never treat the seal as certification of the new database |

Record source artifact hashes and old-to-new IDs, including one-to-many mappings. Unknown mappings remain explicit rather than guessing. Import canonical records ahead of narrative summaries when they disagree, and retain that discrepancy as migration work. In the DRL case, for example, a journal's planned exclusion or changed finding classification is not applied as if it were already canonical.

Migration must preserve distinctions: a conditional judgment stays conditional; a proof gap is not a statement refutation; a source parser limitation is not a mathematical counterexample. Imported green-like labels do not automatically produce green connections. Only current compatible checks and support determine the new reader's state.

If compatibility is established for an unchanged argument, carry its reasoning with an explicit source/target/contract reference rather than repeating it just for a new storage shape. If compatibility cannot be established, preserve the old evidence and create a focused review task. Never invoke the legacy whole-ledger validator as the universal validator of the new record format.

## 5. Required acceptance scenarios

These are behavior tests and review exercises, not a new parallel acceptance framework. Keep small software fixtures separate from real mathematical checking.

| Scenario | Observable requirement |
|---|---|
| Invalid category or missing endpoint | Rejected before commit with the precise record identified |
| Alias/renumbering | Same mathematical item and links preserved |
| Two applications of one lemma | Separate use IDs and application outcomes retained |
| Joint probability inputs | Combination check distinguishes a \(1-2\delta\) guarantee from a claimed \(1-\delta\) guarantee |
| Fixed-point/local-event scope | A local claim cannot acquire a stronger scope merely through graph traversal |
| Cases and alternative proofs | Required cases remain required; alternate routes and their defects remain separately visible |
| Correct supplier, incorrect application | Receiving use has the finding; supplier is not falsely condemned |
| Shared hidden claim | One stored check, accessible through all represented uses with additional inputs visible |
| Local derivation without incoming major edge | Full evidence is accessible from the target result |
| Green incoming edges, failed final combination | Target assessment exposes the failure |
| Successfully checked repair | Original route retains its finding; supplemental or restricted support has its own argument/form and checked uses |
| Projection-created cycle | Actual uses retained; major-only index fallback explains the display limitation |
| Path through another major result | No new direct overview arrow appears without a separate recorded application |
| Headings and routine algebra | Full substantive coverage with proportionate records |
| New consumer | Supplier's completed local check remains current |
| Changed supplier statement versus proof | Different local-reuse and dependency-support consequences are preserved |
| Macro/hypothesis change outside local spans | Source-context review required before reuse |
| Custom conditional and no-proof citation | Supported source workflow through final assessment |
| Interruption after draft/finding | Work survives and appears in the next working report |
| Stale concurrent edit | Rejected without losing earlier work; relevant changes are retrievable |
| Historical red finding after source change | Marked for review, not presented as a confirmed current defect |
| Original independent disagreement | Preserved and explicitly reconciled; no silent overwrite |
| Blinded independent packet | Source evidence is available without the primary reasoning, reconstructed proof, findings, or repairs |
| Legacy completed audit import | Original bytes unchanged and new completion not inferred from the old seal |
| Failed report publication | Last good report retained, with current saved work and report-version distinction intact |

## 6. Scope, sequencing, and stopping criteria

Source fixes and the record contract precede bulk mathematical authoring. Selective reuse is implemented before importing a large audit. Reader projection can be developed alongside the audit workflow once the record contract is stable. Real independent evaluation follows a complete short path through saving, review, reconciliation, and publication.

Do not launch another full-paper audit while the short workflow still needs manual record surgery, cannot preserve partial work, produces contradictory statuses, or hides part of the proof behind a missing connection. Resolve the concrete failure, then repeat the affected exercise. Do not repeatedly rerun every historical suite or renew every sealed audit for unrelated edits.

This revision does not introduce a theorem prover, a universal TeX interpreter, a graph database service, an editable browser application, or a new layout engine for arbitrary cycles. It improves the existing agent's access to evidence, the persistence of its work, and the user's ability to inspect it.

The revision is complete when the accepted installed implementation satisfies the target architecture, the representative mathematical and reader evaluations pass with their limitations stated, compatible old evidence has a supported migration path, and the documentation describes the actual delivered behavior.

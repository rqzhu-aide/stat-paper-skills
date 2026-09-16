# Goal-alignment audit of the graph-based proofchecker

Date: 2026-09-14, America/Chicago. Audited source identity: `6b27574bf1baece6d7c1bbd5c404a9eca4afe14ad75b6db3e42d74e485f1f428`.

**Assessment: the dataset foundation matches the intended design, but the workflow does not yet reliably turn that graph into a complete, efficient checking process.** Keep the current architecture and correct the omissions below before using a large-paper run to measure improvement. This audit changed no production files.

The intended workflow is: register the major statements and their source context, refine meaningful intermediate claims as the argument is examined, derive the required checking work from those dependencies, and save each local judgment. The graph guides the next task and explains unfinished work. The major-node Archify view remains the navigation surface; selecting a connection exposes the relevant intermediate reasoning.

The foundations worth keeping are already present: a single local SQLite authority; stable, collection-qualified IDs; eight allowed item kinds; typed references and inference groups; incremental versions and drafts; and a major-node graph with detailed readers. Joint-premise groups are necessary: checking two applications separately does not establish their combined conclusion. Code can track identities, dependencies and completion, while a mathematical reviewer must still judge each inference.

## Findings requiring correction

### G1. Required work can be omitted while the audit reports completion

**Priority: P1.** This is the principal correctness issue. Three structurally valid public-API fixtures reproduce it:

| Case | Observed result | Missing work |
|---|---|---|
| Focused audit selects a theorem that consumes an internal lemma | 4/4 tasks complete; `process_complete=true`; no problems | The lemma has no checking tasks or checks |
| The theorem consumes a registered intermediate claim with no establishing group or argument | 7/7 complete; no problems | No task asks how that intermediate claim is established |
| A Full audit finishes, then another source-backed theorem is registered in the same paper | Still 7/7 complete; no problems | The new theorem is neither included nor excluded |

In the first two cases the theorem correctly remains amber/conditional. These are false completion signals, not false green proof verdicts. The probes disable independent review to isolate scope derivation; no fresh mathematical review is claimed.

The common cause is [assessment.py](../../shared/paper_core/assessment.py:431): scope is expanded from explicit targets to their parts, without deriving the consumed prerequisite closure or reconciling Full scope with the current proof inventory. The obligation builder at line 466 traverses existing groups and arguments but does not emit missing-establishment work for a consumed intermediate without one. Completion at line 1060 counts only the resulting tasks.

This conflicts with [architecture.md](../architecture.md:28), which includes exact internal prerequisites in Focused mode and all in-scope proof-required results in Full mode. Its completion rule at line 307 explicitly distinguishes unfinished work from a completed inconclusive assessment.

**Focused correction:** derive the required scope from the existing graph. Include consumed internal prerequisites, account for the Full inventory, and expose missing establishing work for consumed proof-required claims. Assumptions and definitions can supply context; external results follow source verification and application checking rather than automatically requiring a local proof route. Retain explicit exclusions and their consequences. Missing structure should remain saveable as a draft and reopen the worklist. Do not require the coordinator to maintain a second dependency list.

**Acceptance:** each example above must expose the omitted work and remain incomplete until it is performed or explicitly adjudicated under the declared scope. Completed gap/refuted/inconclusive findings must still be allowed; do not equate completion with every node being green.

Evidence: [dataset findings](dataset_findings.md), [probe](dataset_probe.py), [results](dataset_run_f3d3bcb3/results.json).

### G2. The graph does not provide an actionable checking order

**Priority: P2, central to the requested user experience.** The instructions describe prerequisite-first scheduling, but the public workflow does not supply it.

[queries.py](../../shared/paper_core/queries.py:181) returns required and unsatisfied obligation IDs without each task's target, action, prerequisite blockers or next packet request. The richer derived obligations are available in the projection/core, but [assessment.py](../../shared/paper_core/assessment.py:1029) orders them by hashed ID. In a simple unchecked chain this places lemma composition before lemma derivation and theorem derivation before its prerequisite is checked.

The reader also prints these opaque IDs. In a small unfinished fixture, one ID appeared 15 times without a link, and searching that ID through the generated search index returned zero matches. These were programmatic renderer checks, not browser interaction tests.

**Focused correction:** expose one derived worklist containing the target, check kind, readiness, unmet prerequisites, saved draft/next action, and the packet to request. Derive it from existing records rather than storing another authored queue. Order ready work from prerequisites toward conclusions, with local derivations before final composition. Allow explicitly provisional work when useful. Make unfinished tasks navigable in the existing reader.

Actual detailed-graph cycles also need an inspection action. The current projection correctly detects a major-node cycle and switches to its index, while mathematical support stays conditional. That display diagnostic does not distinguish genuine circular dependencies from ownership projection, induction, or a simultaneous argument. A cycle is not automatically a mathematical refutation.

**Acceptance:** a small chain should yield a clear next prerequisite task, then advance after its check is saved. A missing intermediate route should yield an authoring task. A genuine dependency cycle should name the records requiring inspection instead of leaving the coordinator to reconstruct it.

Evidence: [worklist results](worklist_results.json), [worklist probe](worklist_probe.py), [UI results](ui_results.json), [cycle diagnostic](dataset_cycle_projection.json).

### G3. Small checking assignments still retrieve the whole theorem

**Priority: P2.** This directly limits the expected efficiency gain on long proofs.

[packets.py](../../shared/paper_core/packets.py:20) accepts only paper, item, part and audit targets. Argument/group/use targets are rejected. Its statement closure at line 184 widens a selected part or hidden claim to the major owner, all its parts, intermediate claims and arguments.

In the generated 100-step theorem with 30 suppliers, requesting one hidden item returned all 101 arguments and 466 records, or 426,195 packet bytes. This is separate from the previously fixed scan of unrelated records: the indexed lookup is working, but the requested mathematical scope is still too broad.

Independent review has another narrowing obstacle: for focused audits, [packets.py](../../shared/paper_core/packets.py:338) requires an exact audit-target match. A source-origin part of a theorem already included in a focused audit cannot receive its own independent packet without additional audit-target administration. The protocol explicitly recommends bounded part review.

**Focused correction:** allow a bounded argument or coherent part as a real work target. Include its exact source, scope, jointly required inputs and consumed supplier content; extend explicitly when more context is needed. Resolve part membership through the audit's derived scope. Preserve independent source-only isolation and the requirement to review final integration.

**Acceptance:** adding unrelated sibling arguments within the same theorem should not enlarge a local task packet. A part of an in-scope theorem should support bounded independent dispatch without widening to the whole theorem or duplicating audit targets.

Evidence: [UI findings](ui_findings.md), [packet measurements](ui_results.json), [part-dispatch result](review_workflow_results.json).

### G4. A cosmetic edit can force a repeat independent review

**Priority: P2.** A saved independent response could not be mapped after changing only the lemma's caption. The error requested a fresh review even though source context, statement and proof were unchanged; the original response remained preserved.

The protection added in the previous correction round rechecks the original worker packet inside the acceptance transaction. That protection is necessary, but [acceptance.py](../../shared/paper_core/acceptance.py:174) compares raw record versions, including presentation-only changes.

**Focused correction:** preserve the original-input check while distinguishing consumed mathematical/source facets from cosmetic fields. Reuse an unchanged review through explicit, recorded mapping/rebinding; retain conflicts for changed source, statement, scope, dependency membership or other relevant input. Do not remove the safety check or silently accept old reviews.

**Acceptance:** a caption-only change must not require new mathematical reasoning. The existing stale-source, changed-scope and out-of-scope mapping cases must continue to fail.

Evidence: `cosmetic_mapping` in [review workflow results](review_workflow_results.json); [probe](review_workflow_probes.py).

### G5. Some invalid worker judgments bypass the promised response preservation

**Priority: P2.** A response that is valid JSON but contains a completed judgment with empty reasoning is rejected with no stored response record or original response blob.

[acceptance.py](../../shared/paper_core/acceptance.py:184) puts the blob and validates generated checks in the same transaction. A semantic check failure rolls both back. This contradicts the intake order in [record-contract.md](../handoff/record-contract.md:178), which preserves the original worker response before interpreting its judgments.

**Focused correction:** after valid coordinator-envelope, qualification and dispatch checks, preserve unusable worker output as `needs_revision` with a diagnostic and no accepted checks. Keep the original bytes immutable. This does not mean accepting a bad judgment, and the probe does not imply deletion of a response file on disk.

**Acceptance:** valid-envelope malformed or semantically invalid worker output remains retrievable and repairable, while invalid coordinator credentials/envelopes remain rejected and no incomplete judgment receives completion credit.

Evidence: `invalid_intake` in [review workflow results](review_workflow_results.json).

### G6. The reader eagerly duplicates shared proof content

**Priority: P2.** Canonical records are deduplicated correctly. Their complete reader bodies are then repeated across every detail that references them.

| Synthetic graph | Canonical records | Rendered record blocks | HTML bytes |
|---|---:|---:|---:|
| 100 intermediate steps, 10 suppliers | 426 | 4,706 | 9,210,762 |
| 100 intermediate steps, 30 suppliers | 466 | 14,506 | 26,528,251 |

The second case generated 551,942 HTML elements by the programmatic count. Shared downstream steps are included in multiple connection details by [projection.py](../../shared/paper_core/projection.py:514), and [render_projection.mjs](../../shared/paper_core/renderer/render_projection.mjs:894) eagerly expands all detail sections into full record bodies.

These fixtures demonstrate repeated content growth, not measured browser latency or a mathematical throughput result. Node rendering took about 0.42 and 1.13 seconds respectively. The concern is the large initial document and repeated reader content, especially as checking records accumulate.

**Focused correction:** retain the standalone Archify shell and one canonical record map, and populate the selected detail on demand. Keep search/navigation indexes compact. Connections should still explain their relevant intermediate route, but need not preload a full duplicate body for every occurrence.

**Acceptance:** shared proof steps should not multiply full HTML bodies by the number of incoming connections. Confirm navigation, search, edge selection and exports in a real browser after the change.

Evidence: [UI findings and method](ui_findings.md), [measurements](ui_results.json), [Python probe](ui_probe.py), [Node inspection](ui_inspect.mjs).

### G7. The installed pilot instructions still make the lean path hard to follow

**Priority: P2.** Keeping v1.5 as the release default until evaluation is intentional and is not itself a defect. The problem is that selecting the database pilot still requires reading an entrypoint with unconditional legacy rules.

[SKILL.md](../../stat-paper-proofcheck/SKILL.md:64) calls JSON canonical, requires every atomic-move field, and later requires all eight risk dispositions. The pilot references instead specify the database as authority and proportionate argument checking. The entrypoint also sends unfamiliar-record/schema questions to legacy examples. This leaves the agent to decide which apparently mandatory instructions to discard.

The installed [database guide](../../stat-paper-proofcheck/references/database-audit.md:54) supplies `body: {...}`, then asks the agent to create several kinds of record. Its pilot references provide neither the full record field tables nor a complete runnable database example. The exact schemas exist in bundled Python code, so this is an authoring/usability gap rather than missing validation.

**Focused correction:** make legacy and database workflows explicit mutually exclusive instruction branches. Supply the new path with a compact, installed record reference and a complete small example, plus minimal request skeletons for ordinary registration and checking. Generate IDs, bindings and mechanical fields through the existing tooling. Avoid adding a second manual checklist or copying the architecture into every worker prompt.

**Acceptance:** a fresh agent with only the installed skill can register a short proof chain, save a draft/check, read the next task and generate the reader without opening development-repository documents or legacy record examples.

## Recommended correction order

1. Repair required-scope derivation and missing-establishment work (G1).
2. Expose the graph-derived worklist and truly bounded packets (G2, G3).
3. Preserve useful independent work across harmless edits and imperfect submissions (G4, G5).
4. Reduce eager reader duplication and clarify the installed authoring path (G6, G7).
5. Run the planned bounded mathematical pilot using the corrected workflow.

This needs focused corrections to the existing system. Keep one database, one record contract, the current major-node UI, and substantive intermediate claims. Do not add a graph server, another state ledger, mandatory per-line records, or a separate scheduling service. Start with the major inventory, refine the graph during reasoning, and let code maintain the remaining-work view.

The complete ordinary two-result fixture used two inference groups, 33 live records, 13 semantic commits and 10 packets. These counts include generated provenance and review records and are not all manually authored. They show that the implementation does not inherently require one node or form per source line. They do not establish real-paper efficiency.

## Evidence and limits

- New public-API synthetic probes exercised scope, task discovery, independent-review recovery and packet size. Dataset omission fixtures passed structural validation.
- Renderer probes used the shipped production renderer and its generated search-index logic. They did not use a browser.
- Both shipped cores and wrappers still match the maintained source byte-for-byte: [bundle check](bundle-check.json).
- The preceding correction round's 1,001 new-format tests (one skip), 115 reader tests and 13 installer tests passed. Those suites were not rerun for this read-only audit; their receipts are in [the prior correction report](../implementation-audit-2026-09-14/fixes/README.md). Passing them did not exercise the omissions above.
- No two-hour live mathematical pilot, genuinely fresh independent mathematical review, forward evaluation or browser visual acceptance was performed in this round. Actual authoring-versus-reasoning time remains unknown.
- All new files are audit evidence under this directory. Production code, skill instructions, bundles, release versions and existing working-tree edits were left unchanged.

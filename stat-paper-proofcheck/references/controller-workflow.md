# Bounded controller workflow (v2.0)

Read [database-audit.md](database-audit.md) for source capture, graph records and storage setup.
The coordinator owns scientific decisions, graph construction/refinement, dispatch, and adjudication.
The controller derives recorded work, prepares context, validates explicit results, and saves progress.
It never calls a model or decides that the registered graph is mathematically complete.

## Prepare one useful assignment

After the coordinator has read the manuscript and registered a source-linked graph and audit:

```text
python "<skill-root>/scripts/paper_audit.py" work list AUDIT.db --audit aud_ID --focus items:itm_ID
python "<skill-root>/scripts/paper_audit.py" work prepare AUDIT.db --audit aud_ID --mode primary --focus items:itm_ID --out assignment
```

An obligation is one examination. A work unit keeps the complete context of a joint inference
together, including its individual applications. An assignment contains an ordered sequence of
compatible units for one argument/result and role. The default maximum is five units, configurable
with `--max-units 1..10`; the number of saved checks can be larger. Preparation grows from ready
work into its same-context successors, so a single model call can check applications, their joint
derivation and final composition. It does not require a new call after each edge.

`--task ID` selects a task and its necessary whole group context. `--exclude-task ID` keeps work
already assigned elsewhere out of this preparation without pretending it is complete. There are
no worker claims or background queue; the coordinator manages actual concurrent dispatch.
`--allow-provisional` explicitly permits local reasoning under unfinished recorded premises; it
does not bypass missing source, broken references, qualification, or independent-context rules.

Preparation writes `worker-packet.json`, `coordinator-manifest.json`, and `response-scaffold.json`.
Give the primary checker its worker packet, scaffold and the primary section of
[checker-protocol.md](checker-protocol.md). The coordinator manifest records permitted tasks and
inputs. For independent assignments, keep that manifest private and give the checker only the
source-only worker packet, its response scaffold and independent protocol.

`prepared:false` with exit 0 means no suitable complete context was prepared. Read the diagnostic:
choose another focus, finish a prerequisite, or refine the graph. The controller does not truncate
an oversized joint inference. Worker context defaults to 131,072 bytes, configurable with
`--max-bytes` up to 1,048,576, with a hard ceiling of 2,048 records. A derivation that exceeds the
limits needs a scientifically meaningful boundary chosen by the coordinator.

## Perform mathematical checking

Check the written argument against its registered premises as part of the substantive examination.
If an omitted dependency or scope distinction is discovered, preserve the exact source and explain
the unfinished reasoning in a draft or finding. The coordinator then edits the graph through
`get --mode author` and `apply`. Do not ask the script to invent the missing premise.

When a higher result invokes a lower lemma, use its exact statement and check its application.
Do not recheck the lower proof unless this assignment explicitly concerns it or borrows its internal
argument. A defect in that proof belongs to its own derivation. The higher local implication may
still be supported under the stated premise while its dependency support remains conditional.
Final composition must assess what the combined written route establishes, not merely count
positive application checks.

## Primary response fields

Complete the generated scaffold; copy task IDs from it. All listed fields are required and unknown
fields are rejected. Empty arrays and nulls are permitted only where indicated by the shape.
The root is `{packet_id, results, coverage, findings}`. Each included result has one of these shapes:

| Result | Fields |
|---|---|
| Check | `type: "check"`, `task_id`, `state: "draft"|"complete"`, `outcome: "supported"|"gap"|"refuted"|"inconclusive"|null`, `reasoning`, `evidence_refs: [anchor ID]`, `conditions: [string]`, `next_action: string|null`, `replaces: PinnedRef|null`, `supersedes: PinnedRef|null` |
| Source fidelity | `type: "source_fidelity"`, `task_id`, `result: "matched"|"needs_attention"`, `note`, `evidence_refs: [anchor ID]` |

The controller supplies the record ID, target, kind, audit, role and reviewer from the assigned
task and coordinator envelope. A complete check needs an actual outcome and substantive reasoning.
An accepted draft remains unfinished. `replaces` identifies the exact supplied draft version owned
by this reviewer; `supersedes` identifies a completed judgment being corrected with a new check.
Use null when neither operation is intended. Never guess a draft to overwrite.

`Ref = {collection, id}`; `PinnedRef = {collection, id, version}`. Source evidence uses registered
anchor IDs from the packet. Additional rows are explicit scientific output, not controller inference:

| Row | Fields |
|---|---|
| Coverage | `argument_id`, `anchor_id`, `start_offset`, `end_offset`, `classification: "substantive"|"structural"`, `claim_refs: [Ref]`, `check_task_ids: [task ID]`, `existing_check_refs: [PinnedRef]`, `replaces: PinnedRef|null`, `note` |
| Finding | `target: Ref`, `category: "presentation"|"proof_gap"|"dependency_mismatch"|"statement_refutation"|"inconclusive"`, `description`, `evidence_refs: [anchor ID]`, `related_task_ids: [task ID]`, `existing_check_refs: [PinnedRef]`, `affected_uses: [use ID]`, `impact_reason` |

Coverage uses zero-based half-open character offsets `[start_offset, end_offset)` into the captured
anchor excerpt. Link substantive spans to their claims and explicit checks. Structural spans have
empty claim/check arrays. Task references in coverage/findings refer to checks included in this
response; use pinned existing checks for earlier saved work. A complete check does not generate
coverage automatically. Findings are new open records; resolving an existing finding remains a
coordinator edit. No worker response creates graph nodes, changes sources, or adjudicates reviews.

[Example response](controller-example-response.json) shows two assumptions, `u <= v` and `v <= w`,
used jointly to conclude `u <= w`. Three units produce five observations/checks and one explicit
coverage row in one response. Its example IDs are illustrative; obtain actual IDs and packet scope
from preparation. The proof excerpt is exactly `By transitivity, u <= v and v <= w imply u <= w.`
with no trailing newline, so its coverage is `[0, 48)`.

## Submit unchanged output

The coordinator writes a separate envelope, exemplified by
[controller-example-envelope.json](controller-example-envelope.json):

```json
{
  "contract_version": 3,
  "request_id": "req_unique",
  "packet_id": "pkt_original",
  "rebase_packet_id": null,
  "reviewer": "primary-reviewer",
  "qualification_id": null,
  "exposure": null,
  "exposure_note": ""
}
```

```text
python "<skill-root>/scripts/paper_audit.py" work submit AUDIT.db --submission SUBMISSION.json --response RESPONSE.json
```

The worker file remains unchanged. One request ID identifies its exact bytes and the parsed
coordinator envelope; the first envelope bytes are retained too. An identical retry returns the
original receipt. A changed response, corrected attempt, or explicit rebase needs a new request ID.
Envelope size is limited to 65,536 bytes and response size to 2,097,152 bytes.

For validly identified work, intake is preserved before worker interpretation or freshness checks.
One submission saves all included checks, observations, coverage and findings atomically. A malformed
included entry prevents all included mathematical edits from committing; the coordinator can
deliberately submit a corrected subset under a new ID. Omitted results remain unfinished. A gap,
refutation or inconclusive result is an accepted examination, not a transport failure.

`state` records this submission's outcome: `received`, `accepted`, `needs_revision`, or `conflict`.
Always read `stored` and `committed_revision` separately. A retained malformed response may return
exit 2 with no mathematical commit; a stale response may return exit 3. A pending independent
source-target mapping may have a mathematical receipt while its submission is `needs_revision`.
None of these transport states alone establishes proof support or audit completion.

## Resume or refine

```text
python "<skill-root>/scripts/paper_audit.py" work inspect AUDIT.db --request req_ID --out recovered-input
python "<skill-root>/scripts/paper_audit.py" work inspect AUDIT.db --packet pkt_ID --out recovered-assignment
python "<skill-root>/scripts/paper_audit.py" work inspect AUDIT.db --audit aud_ID --limit 20
```

Inspect separates the original submission outcome from current record/review state. A preparation
with no response is still recoverable by packet ID. A `received` submission may be explicitly
replayed after interruption; no background retry runs. A terminal rejection remains historical.

After a partial save, prepare current remaining work. If the model already produced unsaved reasoning
under the original packet, preserve that `packet_id` in both files and set `rebase_packet_id` to the
fresh assignment in a new envelope. The controller compares consumed mathematical inputs, relevant
memberships and source context inside the write transaction. Cosmetic or unrelated progress can
pass; changed premises, scope or judgments actually consumed by composition require renewed
reasoning. Do not rewrite packet IDs to disguise old reasoning as newly checked.

## Independent review and reconciliation

Prepare with `--mode independent`, dispatch into a genuinely fresh source-only context, and use
the independent response shape in [checker-protocol.md](checker-protocol.md). The controller
envelope uses the actual reviewer and qualification IDs plus `exposure: "source_only"|"compromised"`
and its explanatory note. The worker's own exposure report cannot improve the coordinator's
assessment. Do not give independent workers primary task outlines, judgments, findings or intake
diagnostics. Map unresolved source identities using `review map`; mapping does not rewrite the
original response or historical submission result.

An earlier pending response stays in history when corrected work is submitted. It grants no
independent credit, but does not permanently block reconciliation of accepted evidence. Inspect
its diagnostics and retain any unresolved scientific issue as a finding or unfinished judgment.
Reconciliation must include all applicable accepted reviews; it cannot credit checks from a
still-pending response or silently omit an accepted disagreement.

Prepare with `--mode reconcile` only when the necessary compared judgments are available. The
coordinator authors the existing `{contract_version, request_id, packet_id, edits}` batch, with the
same IDs as its envelope, and submits it through `work submit`. The controller validates and saves
the explicit adjudication. It does not decide who is right or generate successor reasoning.

Reconcile at the exact target of the compared checks, usually an `arguments`, `groups`, or `uses`
record. The major owner item shown in the worklist is a navigation destination, not a replacement
for that target. Use separate reconciliation rows for distinct targets. Obtain current check IDs,
versions and source anchors from the reconciliation packet; do not guess or reuse stale versions.
Completion combines current resolved rows across those exact targets. Every required independent
examination and applicable accepted judgment must be covered; reconciling one group cannot stand
in for the final composition or another required route. A newly accepted judgment reopens the
uncovered reconciliation work.

The batch uses the create/replace envelopes in [graph-records.md](graph-records.md). These are the
complete record bodies needed for adjudication; all fields are required and `?` means nullable:

| Collection | Complete body fields |
|---|---|
| `reconciliations` | `audit_id`, `target: Ref`, `primary_checks: [PinnedRef]`, `independent_checks: [PinnedRef]`, `decision: "agree"|"primary_revised"|"independent_revised"|"unresolved"`, `rationale: nonempty string`, `evidence_refs: [anchor ID]`, `successor_checks: [PinnedRef]`, `supersedes: PinnedRef?`, `adjudicator: nonempty string` |
| `checks` (primary successor) | `audit_id`, `target: Ref`, `kind: CheckKind`, `role: "primary"`, `reviewer: nonempty string`, `protocol_version: "item-audit/1"`, `state: "draft"|"complete"`, `outcome: "supported"|"gap"|"refuted"|"inconclusive"?`, `reasoning: string`, `evidence_refs: [anchor ID]`, `conditions: [nonempty string]`, `next_action: string?`, `response_id: null`, `supersedes: PinnedRef?` |

Pin the actual compared checks, including all applicable accepted independent reviews. A revised
decision names explicit successor checks with reasons; it does not overwrite the originals. Keep
the successor's audit, role, kind and target the same as its predecessor. A newly created successor
in the same batch has version 1. An independent correction must come from that reviewer's unchanged
response through the review path, not a coordinator-authored independent check.

For `agree`, explain agreement on the same local question; for an unresolved substantive difference,
use `unresolved`. Do not reconcile statement truth against conditional argument validity as though
they were the same examination. An earlier primary classification error can be corrected explicitly
while the statement counterexample remains in its finding.

Preparation schedules unfinished work only. To correct an already satisfied primary judgment,
use `get --mode primary` and `apply` with the full successor-check body above, or include that
successor in an authorized reconciliation batch. `--task` does not silently reopen completed work.

Use `work list` or the reader's worklist for the next action, and regenerate a working report at
meaningful checkpoints. Do not spend model calls polling counters, rendering, or transforming a
response the controller can register directly. Back up the SQLite database for recovery; the
mathematical JSON export does not preserve controller intake or commit history.
